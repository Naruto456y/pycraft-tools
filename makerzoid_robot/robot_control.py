"""
🤖 ================================================================
   Робот Makerzoid — модуль для управления по Bluetooth
   ================================================================

   📦 Что умеет модуль:
      ✅ Управлять моторами (скорость 0-10, направление вперёд/назад)
      ✅ Управлять светом (7 цветов + выключение)
      ✅ Ехать вперёд, назад, поворачивать влево и вправо
      ✅ Останавливать все моторы одной командой
      ✅ Комбинировать моторы и свет в одной команде
      ✅ Запоминать состояние — вызов light1 не гасит light2
      ✅ restore() — сброс в базовое состояние (всё выключено)
      ✅ disconnect(restore=True) — выключить всё перед отключением
      ✅ Работать без await — как обычные блоки в Scratch

   📡 Протокол:
      Связь по Bluetooth Low Energy (BLE).
      MAC-адрес и UUID берутся из переменных окружения
      ROBOT_MAC и ROBOT_UUID (читаются из файла .env),
      либо передаются напрямую в конструктор.

      Каждая команда — это 14-байтовый пакет:

         FF FE 09 01 02 [M1] [M2] 00 [L1] [L2] 00 00 FD FC

      Где:
         M1 — мотор 1 (0=стоп, 1-10=вперёд, 0xFF-0xF6=назад)
         M2 — мотор 2 (аналогично)
         L1 — свет 1 (0=выкл, 1-7=цвета)
         L2 — свет 2 (0=выкл, 1-7=цвета)

      При подключении НЕ отправляется никаких команд —
      робот остаётся в том состоянии, в котором был.

   🚀 Быстрый старт:

      from dotenv import load_dotenv
      from robot_control import Robot
      import time

      load_dotenv()
      bot = Robot()       # MAC и UUID из .env
      bot.connect()       # просто подключается, ничего не выключает

      # 🔴 Включить свет 1 (цвет 3)
      bot.light1(3)

      # 🟡 Включить свет 2 (цвет 5) — свет 1 НЕ погаснет
      bot.light2(5)

      # 🚗 Поехали вперёд на скорости 5
      bot.forward(5)
      time.sleep(2)
      bot.stop()

      # 📦 Моторы и свет одновременно
      bot.send(m1=7, m2=7, l1=2, l2=6)
      time.sleep(3)

      # 🔄 Сбросить всё в ноль
      bot.restore()

      # 📴 Отключиться (можно с автоматическим restore)
      bot.disconnect(restore=True)   # выключит всё, потом отключит
"""

import os
import asyncio
import threading
from bleak import BleakClient


# --- НАСТРОЙКИ ПО УМОЛЧАНИЮ ---
_DEFAULT_MAC = "EC:62:60:53:C6:12"
_DEFAULT_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

# Init-пакет (байт 0x06) — нужен некоторым роботам для активации.
# НЕ отправляется автоматически при connect().
# Вызови bot.init() вручную, если робот не реагирует на команды.
CMD_INIT = bytes([0xFF, 0xFE, 0x09, 0x01, 0x02,
                  0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0xFD, 0xFC])


def _packet(m1=0, m2=0, l1=0, l2=0):
    """📦 Собирает 14-байтовый пакет для отправки роботу.

    Args:
        m1: байт мотора 1 (0=стоп, 1-10=вперёд, 0xFF-0xF6=назад)
        m2: байт мотора 2 (аналогично)
        l1: байт света 1 (0=выкл, 1-7=цвета)
        l2: байт света 2 (0=выкл, 1-7=цвета)

    Returns:
        bytes — готовый 14-байтовый пакет
    """
    return bytes([0xFF, 0xFE, 0x09, 0x01, 0x02,
                  m1, m2, 0x00, l1, l2, 0x00, 0x00,
                  0xFD, 0xFC])


def _speed_to_byte(speed):
    """🔄 Конвертирует скорость в байт для протокола робота.

    Args:
        speed: 0=стоп, 1-10=вперёд, -1..-10=назад

    Returns:
        int — байт (0, 1-10, или 0xFF-0xF6 для отрицательных)

    Пример:
        _speed_to_byte(5)   → 5
        _speed_to_byte(0)   → 0
        _speed_to_byte(-3)  → 253 (0xFD)
    """
    if speed < 0:
        return (256 + speed) & 0xFF
    return max(0, min(10, speed))


class RobotError(Exception):
    """🚫 Ошибка при работе с роботом.

    Возникает, когда:
      - не удалось подключиться к роботу по Bluetooth
      - соединение потеряно во время отправки команды
      - робот не отвечает

    Пример перехвата:

        from robot_control import Robot, RobotError

        try:
            bot = Robot()
            bot.connect()
            bot.forward(5)
        except RobotError as e:
            print(f"Не вышло: {e}")
    """
    pass


class Robot:
    """🤖 Главный класс — точка входа для управления роботом.

    Создаётся один раз, после чего через него идёт вся работа.
    Внутри себя запускает фоновый поток для Bluetooth,
    поэтому все методы синхронные — без await.

    Модуль запоминает текущее состояние моторов и света,
    поэтому вызов light1(3) не погасит ранее включённый light2(5) —
    каждый метод обновляет только свой параметр и отправляет
    пакет со всеми актуальными значениями.

    Args:
        mac:  MAC-адрес робота (строка).
              Если не передан — берётся из env ROBOT_MAC, иначе по умолчанию.
        uuid: UUID BLE-характеристики для записи команд.
              Если не передан — берётся из env ROBOT_UUID, иначе по умолчанию.

    Пример с .env:

        from dotenv import load_dotenv
        from robot_control import Robot
        import time

        load_dotenv()
        bot = Robot()
        bot.connect()        # подключается, ничего не выключает

        bot.light1(3)        # свет 1 горит
        bot.light2(5)        # свет 2 горит, свет 1 НЕ гаснет

        bot.forward(5)
        time.sleep(2)
        bot.stop()

        # Сбросить всё в ноль и отключиться
        bot.disconnect(restore=True)

    Пример с прямым указанием:

        bot = Robot(mac="EC:62:60:53:C6:12",
                    uuid="6e400002-b5a3-f393-e0a9-e50e24dcca9e")
    """

    def __init__(self, mac=None, uuid=None):
        """🔧 Создать контроллер робота.

        Args:
            mac:  MAC-адрес робота (строка).
                  Если None — берётся из env ROBOT_MAC, иначе _DEFAULT_MAC.
            uuid: UUID BLE-характеристики.
                  Если None — берётся из env ROBOT_UUID, иначе _DEFAULT_UUID.
        """
        self.mac = mac or os.environ.get("ROBOT_MAC") or _DEFAULT_MAC
        self.uuid = uuid or os.environ.get("ROBOT_UUID") or _DEFAULT_UUID
        self.client = None

        # Текущее состояние — чтобы не затирать один параметр другим
        self._m1 = 0
        self._m2 = 0
        self._l1 = 0
        self._l2 = 0

        # Запускаем фоновый event loop в отдельном потоке
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    # ================================================================
    #  ВНУТРЕННИЕ МЕТОДЫ
    # ================================================================

    def _run(self, coro):
        """🔄 Запускает async-функцию в фоновом потоке и ждёт результат.

        Внутренний метод — не вызывай напрямую.

        Args:
            coro: корутина (async-функция)

        Returns:
            результат выполнения корутины
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=15)

    async def _connect_async(self):
        """🔌 Внутренний асинхронный метод подключения.

        Создаёт BleakClient и подключается.
        НЕ отправляет никаких команд — робот остаётся как есть.
        """
        self.client = BleakClient(self.mac, timeout=10)
        await self.client.connect()

    async def _send_async(self, m1, m2, l1, l2):
        """📤 Внутренний асинхронный метод отправки пакета."""
        pkt = _packet(m1, m2, l1, l2)
        await self.client.write_gatt_char(self.uuid, pkt, response=False)

    async def _send_raw_async(self, data):
        """📤 Внутренний метод отправки сырых байтов."""
        await self.client.write_gatt_char(self.uuid, data, response=False)

    def _commit(self):
        """📦 Отправляет пакет со всеми текущими значениями состояния.

        Внутренний метод — вызывается после любого изменения
        _m1, _m2, _l1, _l2.
        """
        self._run(self._send_async(self._m1, self._m2, self._l1, self._l2))

    # ================================================================
    #  ПОДКЛЮЧЕНИЕ И ОТКЛЮЧЕНИЕ
    # ================================================================

    def connect(self):
        """🔌 Подключиться к роботу.

        НЕ отправляет никаких команд при подключении —
        робот остаётся в текущем состоянии (свет и моторы не трогаются).

        Если робот не реагирует на команды после подключения,
        попробуй вызвать bot.init() — это отправит активационный пакет.

        Пример:
            bot = Robot()
            bot.connect()
        """
        print(f"🔍 Подключение к {self.mac}...")
        try:
            self._run(self._connect_async())
            print("✅ Подключено!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def init(self):
        """📡 Отправить init-пакет (байт 0x06).

        Некоторым роботам нужен активационный пакет перед тем,
        как они начнут реагировать на команды.
        Вызови после connect(), если робот не откликается.

        Пример:
            bot.connect()
            bot.init()       # активация
            bot.forward(5)   # теперь поедет
        """
        self._run(self._send_raw_async(CMD_INIT))
        import time
        time.sleep(0.2)

    def disconnect(self, restore=False):
        """📴 Отключиться от робота.

        Args:
            restore: если True — перед отключением отправляет команду
                     «всё выключено» (моторы стоп, свет выкл).
                     По умолчанию False — просто разрывает соединение.

        Пример:
            # Просто отключиться
            bot.disconnect()

            # Выключить всё и отключиться
            bot.disconnect(restore=True)
        """
        if restore and self.client and self.client.is_connected:
            self.restore()
        if self.client and self.client.is_connected:
            self._run(self.client.disconnect())
            print("📴 Отключено.")

    # ================================================================
    #  НИЗКОУРОВНЕВАЯ ОТПРАВКА
    # ================================================================

    def send(self, m1=None, m2=None, l1=None, l2=None):
        """📤 Отправить пакет, обновив только указанные параметры.

        None = оставить текущее значение без изменений.
        Это значит, что send(l1=3) не погасит свет 2 —
        он отправит l1=3 вместе с текущим l2.

        Args:
            m1: байт мотора 1 (0=стоп, 1-10=вперёд, 0xFF-0xF6=назад) или None
            m2: байт мотора 2 (аналогично) или None
            l1: байт света 1 (0=выкл, 1-7=цвета) или None
            l2: байт света 2 (0=выкл, 1-7=цвета) или None

        Пример:
            # Оба мотора вперёд на скорости 7, свет не трогаем
            bot.send(m1=7, m2=7)

            # Свет 1 = цвет 3, моторы не трогаем
            bot.send(l1=3)

            # Всё сразу
            bot.send(m1=7, m2=7, l1=3, l2=3)
        """
        if m1 is not None:
            self._m1 = m1
        if m2 is not None:
            self._m2 = m2
        if l1 is not None:
            self._l1 = l1
        if l2 is not None:
            self._l2 = l2
        self._commit()

    def send_raw(self, data):
        """📡 Отправить сырые байты напрямую (без обновления состояния).

        Используй, если нужно отправить нестандартный пакет,
        который не укладывается в обычную схему motor/light.

        Args:
            data: байты (bytes) — готовый пакет

        Пример:
            bot.send_raw(bytes([0xFF, 0xFE, 0x09, 0x01, 0x02,
                                0x07, 0x07, 0x00, 0x03, 0x05, 0x00, 0x00,
                                0xFD, 0xFC]))
        """
        self._run(self._send_raw_async(data))

    # ================================================================
    #  МОТОРЫ
    # ================================================================

    def motor1(self, speed=0):
        """🔄 Установить скорость мотора 1 (мотор 2 и свет не трогает).

        Args:
            speed: 0=стоп, 1-10=вперёд, -1..-10=назад

        Пример:
            bot.motor1(5)    # вперёд, скорость 5
            bot.motor1(-3)   # назад, скорость 3
            bot.motor1(0)    # стоп
        """
        self._m1 = _speed_to_byte(speed)
        self._commit()

    def motor2(self, speed=0):
        """🔄 Установить скорость мотора 2 (мотор 1 и свет не трогает).

        Args:
            speed: 0=стоп, 1-10=вперёд, -1..-10=назад

        Пример:
            bot.motor2(5)    # вперёд, скорость 5
            bot.motor2(-3)   # назад, скорость 3
            bot.motor2(0)    # стоп
        """
        self._m2 = _speed_to_byte(speed)
        self._commit()

    def stop(self):
        """🛑 Остановить оба мотора (свет не трогает).

        Пример:
            bot.forward(5)
            time.sleep(2)
            bot.stop()
        """
        self._m1 = 0
        self._m2 = 0
        self._commit()

    # ================================================================
    #  ДВИЖЕНИЕ
    # ================================================================

    def forward(self, speed=5):
        """🚗 Ехать вперёд (оба мотора в одну сторону).

        Свет не трогает — сохраняет текущие значения.

        Args:
            speed: скорость от 1 до 10

        Пример:
            bot.forward(5)
            time.sleep(2)
            bot.stop()
        """
        self._m1 = speed
        self._m2 = speed
        self._commit()

    def backward(self, speed=5):
        """🚗 Ехать назад (оба мотора в обратную сторону).

        Свет не трогает — сохраняет текущие значения.

        Args:
            speed: скорость от 1 до 10

        Пример:
            bot.backward(3)
            time.sleep(2)
            bot.stop()
        """
        s = (256 - speed) & 0xFF
        self._m1 = s
        self._m2 = s
        self._commit()

    def turn_left(self, speed=5):
        """🔄 Поворот влево (мотор 1 назад, мотор 2 вперёд).

        Свет не трогает.

        Args:
            speed: скорость от 1 до 10

        Пример:
            bot.turn_left(4)
            time.sleep(1)
            bot.stop()
        """
        s_back = (256 - speed) & 0xFF
        self._m1 = s_back
        self._m2 = speed
        self._commit()

    def turn_right(self, speed=5):
        """🔄 Поворот вправо (мотор 1 вперёд, мотор 2 назад).

        Свет не трогает.

        Args:
            speed: скорость от 1 до 10

        Пример:
            bot.turn_right(4)
            time.sleep(1)
            bot.stop()
        """
        s_back = (256 - speed) & 0xFF
        self._m1 = speed
        self._m2 = s_back
        self._commit()

    # ================================================================
    #  СВЕТ
    # ================================================================

    def light1(self, color=0):
        """💡 Установить цвет света 1 (свет 2 и моторы не трогает).

        Args:
            color: 0=выкл, 1-7=цвета (розовый, бирюзовый, фиолетовый и т.д.)

        Пример:
            bot.light1(3)   # цвет 3
            bot.light1(0)   # выключить
        """
        self._l1 = max(0, min(7, color))
        self._commit()

    def light2(self, color=0):
        """💡 Установить цвет света 2 (свет 1 и моторы не трогает).

        Args:
            color: 0=выкл, 1-7=цвета

        Пример:
            bot.light2(5)   # цвет 5
            bot.light2(0)   # выключить
        """
        self._l2 = max(0, min(7, color))
        self._commit()

    def light_off(self):
        """🌙 Выключить оба света (моторы не трогает).

        Пример:
            bot.light1(3)
            bot.light2(5)
            time.sleep(2)
            bot.light_off()
        """
        self._l1 = 0
        self._l2 = 0
        self._commit()

    # ================================================================
    #  СБРОС И ВОССТАНОВЛЕНИЕ
    # ================================================================

    def restore(self):
        """🔄 Привести робота в базовое состояние: выключить всё.

        Останавливает оба мотора и выключает оба света.
        Эквивалент bot.all_off(), но с понятным названием
        для использования перед отключением.

        Пример:
            bot.forward(5)
            bot.light1(3)
            bot.light2(5)
            time.sleep(3)

            bot.restore()         # всё выключено
            bot.disconnect()      # теперь отключаемся

        Также можно через параметр disconnect:

            bot.disconnect(restore=True)   # выключит всё, потом отключит
        """
        self._m1 = 0
        self._m2 = 0
        self._l1 = 0
        self._l2 = 0
        self._commit()
        print("🔄 Робот приведён в базовое состояние (всё выключено).")

    def all_off(self):
        """🔌 Выключить всё: оба мотора и оба света.

        Полный сброс в нулевое состояние.
        То же самое, что restore(), но с другим названием.

        Пример:
            bot.all_off()
        """
        self._m1 = 0
        self._m2 = 0
        self._l1 = 0
        self._l2 = 0
        self._commit()

    # ================================================================
    #  ЧТЕНИЕ СОСТОЯНИЯ
    # ================================================================

    @property
    def is_connected(self):
        """⚡ True, если робот подключен по Bluetooth."""
        return self.client is not None and self.client.is_connected

    @property
    def state(self):
        """📋 Текущее состояние в виде словаря.

        Пример:
            print(bot.state)
            # {'m1': 5, 'm2': 5, 'l1': 3, 'l2': 0}
        """
        return {'m1': self._m1, 'm2': self._m2, 'l1': self._l1, 'l2': self._l2}

    def __repr__(self):
        """📖 Красивый вывод при print()"""
        connected = "да" if self.is_connected else "нет"
        return (f"🤖 Robot(mac='{self.mac}', connected={connected}, "
                f"m1={self._m1}, m2={self._m2}, l1={self._l1}, l2={self._l2})")
