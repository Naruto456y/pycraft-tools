"""
🏠 ================================================================
   Яндекс Умный Дом — модуль для управления устройствами
   ================================================================

   📦 Что умеет модуль:
      ✅ Включать и выключать лампы
      ✅ Менять яркость (1-100%)
      ✅ Менять цветовую температуру (2700-6500K)
      ✅ Управлять группами (например, "Верхний свет")
      ✅ Запускать сценарии ("Я дома", "Ночник" и т.д.)
      ✅ Выключить весь свет одной командой
      ✅ Проверять, что устройство реально умеет, перед отправкой команды

   🔑 Токен берётся из переменной окружения SMART_HOME_TOKEN
      (читается из файла .env через библиотеку python-dotenv)

   🚀 Быстрый старт:
   
      from dotenv import load_dotenv
      from yandex_smart_home import SmartHome

      load_dotenv()  # читает .env
      home = SmartHome()  # токен берётся автоматически

      # 🔌 Включить лампу "Саске"
      home.device("Саске").turn_on()

      # 💡 Поставить яркость 50%
      home.device("Саске").set_brightness(50)

      # 🌡️ Поставить цветовую температуру 4000K
      home.device("Саске").set_temperature(4000)

      # ❌ Выключить
      home.device("Саске").turn_off()

      # 👥 Включить группу "Верхний свет"
      home.group("Верхний свет").turn_on()

      # 🎬 Запустить сценарий "Я дома"
      home.scenario("Я дома").run()

      # 🔌 Выключить вообще все лампы сразу
      home.turn_off_all_lights()
"""

import os
import requests


class SmartHomeError(Exception):
    """🚫 Ошибка при работе с умным домом.

    Возникает, когда:
      - устройство не найдено по имени
      - устройство не поддерживает нужную функцию (например, вкл/выкл для ТВ)
      - значение вне допустимого диапазона (например, яркость 200%)
      - API Яндекса вернул ошибку

    Пример перехвата:

        from yandex_smart_home import SmartHome, SmartHomeError

        try:
            home.device("Яндекс ТВ").turn_on()
        except SmartHomeError as e:
            print(f"Не вышло: {e}")
            # Выведет: "Устройство 'Яндекс ТВ' не поддерживает вкл/выкл"
    """
    pass


class Device:
    """💡 Устройство умного дома (лампа, колонка, ТВ и т.д.)

    Не создаётся вручную — получается через home.device("имя").

    Свойства:
      - name        — имя устройства (строка)
      - id          — уникальный идентификатор (строка)
      - type        — тип устройства, например "devices.types.light"
      - is_on       — включено ли сейчас (True/False/None)
      - brightness  — текущая яркость в процентах (1-100/None)
      - temperature — цветовая температура в кельвинах (2700-6500/None)
      - room        — название комнаты (строка/None)

    Проверки возможностей:
      - can_turn_on_off     — True, если устройство можно вкл/выкл
      - can_set_brightness  — True, если можно менять яркость
      - can_set_temperature — True, если можно менять цветовую температуру

    Методы управления:
      - turn_on()              — включить
      - turn_off()             — выключить
      - toggle()               — переключить (вкл ↔ выкл)
      - set_brightness(value)  — поставить яркость (1-100)
      - set_temperature(value) — поставить цветовую температуру (2700-6500)
    """

    def __init__(self, raw_data, home):
        """ 🔧 Внутренний конструктор. Не вызывай напрямую — используй home.device() """
        self._raw = raw_data  # сырой JSON от Яндекса
        self._home = home     # ссылка на SmartHome (для отправки команд)
        self.id = raw_data["id"]
        self.name = raw_data["name"]
        self.type = raw_data["type"]
        self.room = raw_data.get("room")  # может быть None

    # ================================================================
    #  ЧТЕНИЕ СОСТОЯНИЯ
    # ================================================================

    @property
    def capabilities(self):
        """📋 Список capabilities (функций) устройства из ответа API"""
        return self._raw.get("capabilities", [])

    def _find_cap(self, cap_type, instance=None):
        """🔍 Найти конкретную capability по типу и (опционально) instance"""
        for cap in self.capabilities:
            if cap.get("type") == cap_type:
                if instance is None or cap.get("parameters", {}).get("instance") == instance:
                    return cap
        return None

    @property
    def can_turn_on_off(self):
        """🔌 True, если устройство поддерживает вкл/выкл (есть capability on_off)"""
        return self._find_cap("devices.capabilities.on_off") is not None

    @property
    def can_set_brightness(self):
        """☀️ True, если устройство поддерживает регулировку яркости"""
        return self._find_cap("devices.capabilities.range", "brightness") is not None

    @property
    def can_set_temperature(self):
        """🌈 True, если устройство поддерживает смену цветовой температуры"""
        return self._find_cap("devices.capabilities.color_setting") is not None

    @property
    def is_on(self):
        """⚡ Включено ли устройство прямо сейчас. True/False/None (None = неизвестно)"""
        cap = self._find_cap("devices.capabilities.on_off")
        if cap and cap.get("state"):
            return cap["state"].get("value")
        return None

    @property
    def brightness(self):
        """☀️ Текущая яркость (1-100). None, если не поддерживается."""
        cap = self._find_cap("devices.capabilities.range", "brightness")
        if cap and cap.get("state"):
            return cap["state"].get("value")
        return None

    @property
    def temperature(self):
        """🌡️ Текущая цветовая температура (2700-6500K). None, если не поддерживается."""
        cap = self._find_cap("devices.capabilities.color_setting")
        if cap and cap.get("state"):
            return cap["state"].get("value")
        return None

    # ================================================================
    #  УПРАВЛЕНИЕ
    # ================================================================

    def _action(self, capabilities):
        """📤 Внутренний метод — отправляет команду устройству.

        capabilities — список словарей вида:
            {"type": "devices.capabilities.on_off",
             "state": {"instance": "on", "value": True}}

        Ключ "actions" (а не "capabilities"!) используется в payload.
        Это главная ловушка Яндекса API — без "actions" команда игнорируется.
        """
        return self._home.custom_action([(self.id, capabilities)])

    def turn_on(self):
        """✅ Включить устройство.

        Пример:
            home.device("Саске").turn_on()

        Ошибка SmartHomeError, если устройство не поддерживает вкл/выкл
        (например, Яндекс ТВ или Яндекс Станция).
        """
        if not self.can_turn_on_off:
            raise SmartHomeError(
                f"🔌 Устройство '{self.name}' не поддерживает вкл/выкл"
            )
        return self._action([
            {"type": "devices.capabilities.on_off",
             "state": {"instance": "on", "value": True}}
        ])

    def turn_off(self):
        """❌ Выключить устройство.

        Пример:
            home.device("Саске").turn_off()

        Ошибка SmartHomeError, если устройство не поддерживает вкл/выкл.
        """
        if not self.can_turn_on_off:
            raise SmartHomeError(
                f"🔌 Устройство '{self.name}' не поддерживает вкл/выкл"
            )
        return self._action([
            {"type": "devices.capabilities.on_off",
             "state": {"instance": "on", "value": False}}
        ])

    def toggle(self):
        """🔄 Переключить устройство (если вкл — выключить, если выкл — включить).

        Пример:
            home.device("Саске").toggle()
        """
        if self.is_on:
            self.turn_off()
        else:
            self.turn_on()

    def set_brightness(self, value):
        """☀️ Поставить яркость лампы (от 1 до 100 процентов).

        Пример:
            home.device("Саске").set_brightness(50)  # 50% яркости

        Args:
            value: яркость от 1 до 100 (целое число)

        Ошибка SmartHomeError, если:
            - устройство не поддерживает регулировку яркости
            - значение вне диапазона 1-100
        """
        if not self.can_set_brightness:
            raise SmartHomeError(
                f"☀️ Устройство '{self.name}' не поддерживает регулировку яркости"
            )
        if not isinstance(value, (int, float)) or value < 1 or value > 100:
            raise SmartHomeError(
                f"☀️ Яркость {value} вне диапазона (1-100%)"
            )
        return self._action([
            {"type": "devices.capabilities.range",
             "state": {"instance": "brightness", "value": int(value)}}
        ])

    def set_temperature(self, value):
        """🌡️ Поставить цветовую температуру (от 2700 до 6500 кельвинов).

        2700K = тёплый жёлтый свет (как лампа накаливания)
        6500K = холодный белый свет (как дневной)

        Пример:
            home.device("Саске").set_temperature(4000)  # нейтральный белый

        Args:
            value: температура от 2700 до 6500 (целое число)

        Ошибка SmartHomeError, если:
            - устройство не поддерживает смену температуры
            - значение вне диапазона 2700-6500
        """
        if not self.can_set_temperature:
            raise SmartHomeError(
                f"🌡️ Устройство '{self.name}' не поддерживает смену цветовой температуры"
            )
        if not isinstance(value, (int, float)) or value < 2700 or value > 6500:
            raise SmartHomeError(
                f"🌡️ Температура {value} вне диапазона (2700-6500K)"
            )
        return self._action([
            {"type": "devices.capabilities.color_setting",
             "state": {"instance": "temperature_k", "value": int(value)}}
        ])

    def __repr__(self):
        """📖 Крастый вывод при print() — показывает имя, тип и состояние"""
        return (f"💡 Device(name='{self.name}', type='{self.type}', "
                f"is_on={self.is_on}, brightness={self.brightness}, "
                f"temperature={self.temperature})")


class Group:
    """👥 Группа устройств (например, "Верхний свет" — это Саске + Сакура).

    Не создаётся вручную — получается через home.group("имя").

    Свойства:
      - name  — имя группы (строка)
      - id    — уникальный идентификатор (строка)
      - devices — список ID устройств в группе

    Методы управления:
      - turn_on()              — включить всю группу
      - turn_off()             — выключить всю группу
      - set_brightness(value)  — поставить яркость для всей группы
    """

    def __init__(self, raw_data, home):
        """ 🔧 Внутренний конструктор. Не вызывай напрямую — используй home.group() """
        self._raw = raw_data
        self._home = home
        self.id = raw_data["id"]
        self.name = raw_data["name"]
        self.devices = raw_data.get("devices", [])

    def _find_cap(self, cap_type, instance=None):
        """🔍 Найти capability в группе"""
        for cap in self._raw.get("capabilities", []):
            if cap.get("type") == cap_type:
                if instance is None or cap.get("parameters", {}).get("instance") == instance:
                    return cap
        return None

    @property
    def can_turn_on_off(self):
        """🔌 True, если группу можно вкл/выкл"""
        return self._find_cap("devices.capabilities.on_off") is not None

    @property
    def can_set_brightness(self):
        """☀️ True, если у группы есть регулировка яркости"""
        return self._find_cap("devices.capabilities.range", "brightness") is not None

    @property
    def is_on(self):
        """⚡ Включена ли группа прямо сейчас"""
        cap = self._find_cap("devices.capabilities.on_off")
        if cap and cap.get("state"):
            return cap["state"].get("value")
        return None

    @property
    def brightness(self):
        """☀️ Текущая яркость группы (1-100/None)"""
        cap = self._find_cap("devices.capabilities.range", "brightness")
        if cap and cap.get("state"):
            return cap["state"].get("value")
        return None

    def _action(self, capabilities):
        """📤 Отправить команду группе. Ключ "actions" обязателен!"""
        payload = {"groups": [{"id": self.id, "actions": capabilities}]}
        return self._home._post("/groups/actions", payload)

    def turn_on(self):
        """✅ Включить всю группу.

        Пример:
            home.group("Верхний свет").turn_on()
        """
        return self._action([
            {"type": "devices.capabilities.on_off",
             "state": {"instance": "on", "value": True}}
        ])

    def turn_off(self):
        """❌ Выключить всю группу.

        Пример:
            home.group("Верхний свет").turn_off()
        """
        return self._action([
            {"type": "devices.capabilities.on_off",
             "state": {"instance": "on", "value": False}}
        ])

    def set_brightness(self, value):
        """☀️ Поставить яркость для всей группы (1-100%).

        Пример:
            home.group("Верхний свет").set_brightness(75)
        """
        if not isinstance(value, (int, float)) or value < 1 or value > 100:
            raise SmartHomeError(f"☀️ Яркость {value} вне диапазона (1-100%)")
        return self._action([
            {"type": "devices.capabilities.range",
             "state": {"instance": "brightness", "value": int(value)}}
        ])

    def __repr__(self):
        return (f"👥 Group(name='{self.name}', devices={len(self.devices)}, "
                f"is_on={self.is_on}, brightness={self.brightness})")


class Scenario:
    """🎬 Сценарий умного дома (запускает цепочку действий).

    Не создаётся вручную — получается через home.scenario("имя").

    Свойства:
      - name      — имя сценария (строка)
      - id        — уникальный идентификатор (строка)
      - is_active — активен ли сценарий (True/False)

    Методы:
      - run() — запустить сценарий
    """

    def __init__(self, raw_data, home):
        """ 🔧 Внутренний конструктор. Не вызывай напрямую — используй home.scenario() """
        self._home = home
        self.id = raw_data["id"]
        self.name = raw_data["name"]
        self.is_active = raw_data.get("is_active", False)

    def run(self):
        """▶️ Запустить сценарий.

        Пример:
            home.scenario("Я дома").run()       # Алиса скажет "С возвращением!" и включит Саске
            home.scenario("Ночник").run()       # Саске плавно убавит яркость
            home.scenario("Я ухожу").run()      # Выключит свет и скажет "Пока!"

        Возвращает JSON-ответ от Яндекса (dict).
        """
        return self._home._post(f"/scenarios/{self.id}/actions", payload=None)

    def __repr__(self):
        return f"🎬 Scenario(name='{self.name}', is_active={self.is_active})"


class SmartHome:
    """🏠 Главный класс — точка входа для управления умным домом.

    Создаётся один раз, после чего через него идёт вся работа.

    Args:
        token: OAuth-токен Яндекса (строка, начинается с "y0_").
               Если не передан — берётся из переменной окружения
               SMART_HOME_TOKEN (через python-dotenv).

    Пример:
        from dotenv import load_dotenv
        from yandex_smart_home import SmartHome

        load_dotenv()
        home = SmartHome()  # токен из .env

        # 📋 Посмотреть все устройства
        for dev in home.devices:
            print(dev.name, dev.is_on, dev.brightness)

        # 💡 Включить Саске и поставить яркость 50%
        home.device("Саске").turn_on()
        home.device("Саске").set_brightness(50)

        # 👥 Группа
        home.group("Верхний свет").turn_off()

        # 🎬 Сценарий
        home.scenario("Я дома").run()

        # 🔌 Выключить весь свет
        home.turn_off_all_lights()

        # 🔄 Обновить данные с сервера (если что-то изменилось вне скрипта)
        home.refresh()
    """

    API_BASE = "https://api.iot.yandex.net/v1.0"

    def __init__(self, token=None):
        """🔧 Создать подключение к умному дому.

        Args:
            token: OAuth-токен (начинается с y0_).
                   Если None — берётся из env SMART_HOME_TOKEN.
        """
        # 🔑 Ищем токен: аргумент → переменная окружения
        token = token or os.environ.get("SMART_HOME_TOKEN")
        if not token:
            raise SmartHomeError(
                "🔑 Токен не найден!\n"
                "   Передайте его: SmartHome('y0_...')\n"
                "   Или создайте файл .env со строкой:\n"
                "   SMART_HOME_TOKEN=y0_..."
            )

        self._token = token
        self._headers = {
            "Authorization": f"Bearer {token}",  # ⚠️ Bearer, не OAuth!
            "Content-Type": "application/json"
        }

        # 📦 Данные с сервера (кэшируются, обновляются через refresh())
        self._data = None
        self.refresh()

    # ================================================================
    #  ВЗАИМОДЕЙСТВИЕ С API
    # ================================================================

    def _get(self, path):
        """📥 Внутренний GET-запрос к API Яндекса"""
        url = f"{self.API_BASE}{path}"
        try:
            r = requests.get(url, headers=self._headers, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise SmartHomeError(f"🌐 Ошибка сети: {e}")

    def _post(self, path, payload):
        """📤 Внутренний POST-запрос к API Яндекса

        ⚠️ ВАЖНО: для /devices/actions и /groups/actions
        ключ в payload должен быть "actions", а не "capabilities".
        Без этого Яндекс вернёт пустой ответ и ничего не сделает.
        """
        url = f"{self.API_BASE}{path}"
        try:
            r = requests.post(url, headers=self._headers, json=payload, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise SmartHomeError(f"🌐 Ошибка сети: {e}")

    def refresh(self):
        """🔄 Обновить данные с сервера Яндекса.

        Вызывай, если что-то изменилось вне скрипта
        (например, кто-то включил свет руками через приложение).

        Пример:
            home.refresh()  # подтянул свежие данные
            print(home.device("Саске").is_on)  # актуальное состояние
        """
        self._data = self._get("/user/info")
        return self

    # ================================================================
    #  УСТРОЙСТВА
    # ================================================================

    @property
    def devices(self):
        """📋 Список всех устройств (list объектов Device).

        Пример:
            for dev in home.devices:
                print(f"{dev.name} | вкл={dev.is_on}")
        """
        return [Device(d, self) for d in self._data.get("devices", [])]

    def device(self, name):
        """💡 Найти устройство по имени или алиасу.

        Поиск идёт по имени и по списку aliases.
        Регистр не важен — "саске" и "Саске" одинаково сработают.

        Args:
            name: имя устройства или алиас (строка)

        Returns:
            Объект Device с методами turn_on(), turn_off() и т.д.

        Ошибка SmartHomeError, если устройство не найдено.

        Пример:
            lamp = home.device("Саске")       # по имени
            lamp = home.device("Шаринган")    # по алиасу (он же Саске)
            lamp = home.device("Светильник")  # по другому алиасу
            lamp.turn_on()
        """
        name_lower = name.lower().strip()
        for d in self._data.get("devices", []):
            # проверяем имя
            if d["name"].lower().strip() == name_lower:
                return Device(d, self)
            # проверяем алиасы
            for alias in d.get("aliases", []):
                if alias.lower().strip() == name_lower:
                    return Device(d, self)
        raise SmartHomeError(
            f"🔍 Устройство '{name}' не найдено!\n"
            f"   Доступные устройства: " +
            ", ".join(d["name"] for d in self._data.get("devices", []))
        )

    # ================================================================
    #  ГРУППЫ
    # ================================================================

    @property
    def groups(self):
        """📋 Список всех групп (list объектов Group)"""
        return [Group(g, self) for g in self._data.get("groups", [])]

    def group(self, name):
        """👥 Найти группу по имени.

        Args:
            name: имя группы (строка)

        Returns:
            Объект Group с методами turn_on(), turn_off(), set_brightness()

        Пример:
            home.group("Верхний свет").turn_on()
            home.group("Верхний свет").set_brightness(75)
        """
        name_lower = name.lower().strip()
        for g in self._data.get("groups", []):
            if g["name"].lower().strip() == name_lower:
                return Group(g, self)
        raise SmartHomeError(
            f"👥 Группа '{name}' не найдена!\n"
            f"   Доступные группы: " +
            ", ".join(g["name"] for g in self._data.get("groups", []))
        )

    # ================================================================
    #  СЦЕНАРИИ
    # ================================================================

    @property
    def scenarios(self):
        """📋 Список всех сценариев (list объектов Scenario)"""
        return [Scenario(s, self) for s in self._data.get("scenarios", [])]

    def scenario(self, name):
        """🎬 Найти сценарий по имени.

        Args:
            name: имя сценария (строка)

        Returns:
            Объект Scenario с методом run()

        Пример:
            home.scenario("Я дома").run()
            home.scenario("Ночник").run()
            home.scenario("Экономим электричество").run()
        """
        name_lower = name.lower().strip()
        for s in self._data.get("scenarios", []):
            if s["name"].lower().strip() == name_lower:
                return Scenario(s, self)
        raise SmartHomeError(
            f"🎬 Сценарий '{name}' не найден!\n"
            f"   Доступные сценарии: " +
            ", ".join(s["name"] for s in self._data.get("scenarios", []))
        )

    # ================================================================
    #  МАССОВЫЕ ДЕЙСТВИЯ
    # ================================================================

    def turn_off_all_lights(self):
        """🔌 Выключить вообще все лампы одним запросом.

        Находит все устройства с type="devices.types.light"
        и выключает их одновременно (одно API-сообщение).

        Пример:
            home.turn_off_all_lights()
        """
        light_ids = []
        for d in self._data.get("devices", []):
            if d["type"] == "devices.types.light":
                light_ids.append(
                    (d["id"], [{"type": "devices.capabilities.on_off",
                                "state": {"instance": "on", "value": False}}])
                )
        if not light_ids:
            raise SmartHomeError("💡 Ламп не найдено!")
        return self.custom_action(light_ids)

    def custom_action(self, device_commands):
        """📦 Отправить произвольные команды нескольким устройствам одновременно.

        ⚠️ ВАЖНО: ключ "actions" (не "capabilities"!) —
        без этого Яндекс проигнорирует команду.

        Args:
            device_commands: список кортежей (device_id, capabilities),
                где capabilities — список словарей вида:
                    {"type": "devices.capabilities.on_off",
                     "state": {"instance": "on", "value": False}}

        Пример:
            # Выключить Саске и Сакуру одним запросом
            home.custom_action([
                ("a0c17ef9-23fb-46bb-a193-966dbf7074be", [
                    {"type": "devices.capabilities.on_off",
                     "state": {"instance": "on", "value": False}}
                ]),
                ("a15ed02d-16b8-435a-8bb6-4ada65ff5586", [
                    {"type": "devices.capabilities.on_off",
                     "state": {"instance": "on", "value": False}}
                ]),
            ])
        """
        payload = {
            "devices": [
                {"id": dev_id, "actions": caps}
                for dev_id, caps in device_commands
            ]
        }
        return self._post("/devices/actions", payload)

    def __repr__(self):
        n_dev = len(self._data.get("devices", []))
        n_grp = len(self._data.get("groups", []))
        n_scn = len(self._data.get("scenarios", []))
        return (f"🏠 SmartHome(devices={n_dev}, groups={n_grp}, scenarios={n_scn})")
