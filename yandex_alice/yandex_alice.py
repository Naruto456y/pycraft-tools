"""
🗣️ ================================================================
   Яндекс Алиса — управление ТВ и колонками по локальной сети
   ================================================================

   📦 Что умеет модуль:
      ✅ Находить все устройства с Алисой в аккаунте (ТВ, колонки)
      ✅ Произносить любую фразу голосом Алисы
      ✅ Отдавать любые команды текстом ("открой YouTube", "включи канал Пятница")
      ✅ Открывать приложения на Яндекс ТВ (YouTube, Rutube, VK Видео...)
      ✅ Пауза / продолжить / следующий / предыдущий / перемотка
      ✅ Точная громкость (0-100%)
      ✅ Включать музыку из Яндекс Музыки по id трека, альбома, плейлиста
      ✅ Читать состояние: что играет, громкость, пауза

   🔌 Как работает:
      Команды идут напрямую в устройство по протоколу Glagol
      (WebSocket wss://IP:1961). Интернет нужен только чтобы
      получить у Яндекса список устройств и одноразовый токен разговора.
      Ноутбук и устройство должны быть в одной Wi-Fi сети.

   🔑 Токен берётся из переменной окружения GLAGOL_TOKEN
      (OAuth-токен Яндекс Музыки, читается из .env через python-dotenv).
      Получить: https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d
      ⚠️ Токен умного дома (SMART_HOME_TOKEN) сюда НЕ подходит — Glagol вернёт 403.

   🚀 Быстрый старт:

      from dotenv import load_dotenv
      from yandex_alice import Alice

      load_dotenv()      # читает .env
      alice = Alice()    # токен берётся автоматически

      # 📺 Открыть YouTube на телевизоре
      alice.tv.open_app("YouTube")

      # 🗣️ Пусть колонка скажет фразу
      alice.speaker.say("Ужин готов!")

      # 🔊 Громкость 30% на ТВ
      alice.tv.set_volume(30)

      # ⏸️ Пауза
      alice.tv.pause()

      # 📢 Сказать сразу на всех устройствах
      alice.say_everywhere("Всем привет!")
"""

import os
import ssl
import json
import time
import uuid

import requests

try:
    import websocket  # пакет websocket-client
except ImportError as e:
    raise ImportError("Для Алисы нужен websocket-client: pip install pycraft-tools[yandex_alice]") from e


class AliceError(Exception):
    """🚫 Ошибка при работе с Алисой.

    Возникает, когда:
      - токен не найден или протух (Яндекс вернул 401/403)
      - устройство не найдено по имени/IP
      - устройство выключено или не в той же Wi-Fi сети
      - значение вне допустимого диапазона (например, громкость 200%)
      - устройство ответило ошибкой на команду

    Пример перехвата:

        from yandex_alice import Alice, AliceError

        try:
            alice.tv.open_app("YouTube")
        except AliceError as e:
            print(f"Не вышло: {e}")
            # Выведет: "📴 Устройство 'Яндекс ТВ' не отвечает по 192.168.1.46:1961 ..."
    """
    pass


class AliceDevice:
    """📺 Устройство с Алисой: Яндекс ТВ, Станция, Станция Лайт и т.д.

    Не создаётся вручную — получается через alice.device("имя"),
    alice.tv или alice.speaker.

    Свойства:
      - name       — имя устройства ("Яндекс ТВ")
      - id         — уникальный идентификатор
      - platform   — платформа, например "yandex_tv_mt9632_11_cv" или "yandexmicro"
      - ip         — IPv4-адрес в локальной сети (строка/None)
      - is_tv      — True, если это телевизор
      - is_speaker — True, если это колонка
      - is_local   — True, если устройство видно в локальной сети (есть IP)

    Методы:
      - command(text)          — любая команда Алисе текстом
      - say(text)              — произнести фразу
      - open_app(name)         — открыть приложение ("YouTube", "Rutube")
      - play() / pause()       — продолжить / пауза
      - next() / prev()        — следующий / предыдущий
      - rewind(seconds)        — перемотать на позицию в секундах
      - set_volume(percent)    — громкость 0-100
      - volume_up() / volume_down() — громче / тише на шаг
      - play_music(id, kind)   — трек/альбом/исполнитель/плейлист из Яндекс Музыки
      - get_state()            — состояние: громкость, играет ли, что играет
      - volume / is_playing    — быстрые свойства поверх get_state()
    """

    PORT = 1961  # 🔌 порт Glagol на всех устройствах с Алисой

    def __init__(self, raw_data, alice):
        """🔧 Внутренний конструктор. Не вызывай напрямую — используй alice.device()"""
        self._raw = raw_data   # сырой JSON из glagol/device_list
        self._alice = alice    # ссылка на Alice (для токенов)
        self.id = raw_data["id"]
        self.name = raw_data.get("name", "")
        self.platform = raw_data.get("platform", "")

    # ================================================================
    #  ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ
    # ================================================================

    @property
    def ip(self):
        """🌐 IPv4-адрес устройства в локальной сети. None, если устройство не в сети."""
        addrs = self._raw.get("networkInfo", {}).get("ip_addresses") or []
        return next((a for a in addrs if "." in a), None)

    @property
    def is_local(self):
        """📡 True, если у устройства есть локальный IP (значит, им можно управлять)"""
        return self.ip is not None

    @property
    def is_tv(self):
        """📺 True, если это Яндекс ТВ (платформа начинается с yandex_tv)"""
        return self.platform.startswith("yandex_tv")

    @property
    def is_speaker(self):
        """🔊 True, если это колонка: Станция, Мини, Лайт, Макс и т.д."""
        return self.is_local and not self.is_tv

    # ================================================================
    #  ОТПРАВКА КОМАНД (низкий уровень)
    # ================================================================

    def _connect(self):
        """🔌 Внутренний метод — открывает WebSocket к устройству.

        У устройства самоподписанный сертификат, поэтому проверку SSL
        выключаем — соединение всё равно идёт только внутри домашней сети.
        """
        if not self.is_local:
            raise AliceError(f"📴 У устройства '{self.name}' нет локального IP — оно выключено или не в сети")
        try:
            return websocket.create_connection(
                f"wss://{self.ip}:{self.PORT}",
                sslopt={"cert_reqs": ssl.CERT_NONE},
                timeout=10,
            )
        except (OSError, websocket.WebSocketException) as e:
            raise AliceError(
                f"📴 Устройство '{self.name}' не отвечает по {self.ip}:{self.PORT}\n"
                f"   Проверь, что оно включено и ноутбук в той же Wi-Fi сети ({e})"
            ) from e

    def _message(self, payload):
        """📦 Собирает сообщение Glagol: токен разговора + id + время + команда"""
        return json.dumps({
            "conversationToken": self._alice._conversation_token(self),
            "id": str(uuid.uuid4()),
            "sentTime": int(time.time() * 1000),
            "payload": payload,
        })

    def send(self, payload):
        """📤 Отправить устройству сырую команду Glagol и дождаться ответа.

        Args:
            payload: словарь команды, например {"command": "play"}
                     или {"command": "setVolume", "volume": 0.3}

        Returns:
            dict — ответ устройства (в нём есть "status": "SUCCESS")

        Пример:
            alice.tv.send({"command": "next"})

        Ошибка AliceError, если устройство не ответило SUCCESS.
        """
        ws = self._connect()
        try:
            ws.send(self._message(payload))
            for _ in range(20):  # 🔁 до ответа устройство может прислать пару сообщений о состоянии
                msg = json.loads(ws.recv())
                if msg.get("requestId") or msg.get("status"):
                    if msg.get("status") != "SUCCESS":
                        raise AliceError(f"❌ '{self.name}' ответил {msg.get('status')}: {msg.get('errorText', '')}")
                    return msg
            raise AliceError(f"⌛ '{self.name}' не прислал ответ на команду {payload.get('command')}")
        except websocket.WebSocketException as e:
            raise AliceError(f"🔌 Связь с '{self.name}' оборвалась: {e}") from e
        finally:
            ws.close()

    # ================================================================
    #  ГОЛОС И КОМАНДЫ АЛИСЕ
    # ================================================================

    def command(self, text):
        """💬 Отдать Алисе любую команду текстом — как будто сказал голосом.

        Args:
            text: фраза-команда ("включи канал Пятница", "какая погода", "поставь таймер на 5 минут")

        Пример:
            alice.tv.command("включи мультики")
            alice.speaker.command("какая завтра погода")
        """
        if not text or not text.strip():
            raise AliceError("💬 Пустая команда — Алисе нечего делать")
        return self.send({"command": "sendText", "text": text.strip()})

    def say(self, text):
        """🗣️ Произнести фразу голосом Алисы.

        Под капотом — команда "повтори за мной ...", поэтому Алиса
        может отказаться повторять грубые слова.

        Args:
            text: что сказать ("Ужин готов!")

        Пример:
            alice.speaker.say("Юсуф, пора делать уроки")
        """
        return self.command(f"повтори за мной {text}")

    def open_app(self, app_name):
        """📲 Открыть приложение на Яндекс ТВ.

        Работает с тем, что умеет открывать Алиса:
        YouTube, Rutube, ВК Видео, Кинопоиск, Okko, Иви и т.д.

        Args:
            app_name: название приложения ("YouTube", "Rutube", "ВК Видео")

        Пример:
            alice.tv.open_app("Rutube")

        ⚠️ На колонке без экрана команда не имеет смысла.
        """
        return self.command(f"открой {app_name}")

    # ================================================================
    #  ПЛЕЕР
    # ================================================================

    def play(self):
        """▶️ Продолжить воспроизведение.

        Пример:
            alice.tv.play()
        """
        return self.send({"command": "play"})

    def pause(self):
        """⏸️ Поставить на паузу.

        Пример:
            alice.tv.pause()
        """
        return self.send({"command": "stop"})

    def next(self):
        """⏭️ Следующий трек / видео / серия.

        Пример:
            alice.speaker.next()
        """
        return self.send({"command": "next"})

    def prev(self):
        """⏮️ Предыдущий трек / видео / серия.

        Пример:
            alice.speaker.prev()
        """
        return self.send({"command": "prev"})

    def rewind(self, seconds):
        """⏩ Перемотать на нужную позицию (в секундах от начала).

        Args:
            seconds: позиция в секундах (0 и больше)

        Пример:
            alice.tv.rewind(90)  # на 1:30
        """
        if seconds < 0:
            raise AliceError(f"⏩ Позиция должна быть 0 и больше, получено {seconds}")
        return self.send({"command": "rewind", "position": seconds})

    def play_music(self, music_id, kind="track"):
        """🎵 Включить музыку из Яндекс Музыки по id.

        Args:
            music_id: id трека / альбома / исполнителя / плейлиста
                      (видно в ссылке music.yandex.ru/album/123/track/456 → "456")
            kind: "track", "album", "artist" или "playlist"

        Пример:
            alice.speaker.play_music("456", "track")
            alice.speaker.play_music("123", "album")

        💡 Проще через голос: alice.speaker.command("включи Linkin Park")
        """
        kinds = ("track", "album", "artist", "playlist")
        if kind not in kinds:
            raise AliceError(f"🎵 kind должен быть одним из {kinds}, получено {kind!r}")
        return self.send({"command": "playMusic", "id": str(music_id), "type": kind})

    # ================================================================
    #  ГРОМКОСТЬ
    # ================================================================

    def set_volume(self, percent):
        """🔊 Поставить громкость (от 0 до 100 процентов).

        Args:
            percent: громкость в процентах (0 — тишина, 100 — максимум)

        Пример:
            alice.tv.set_volume(30)

        Ошибка AliceError, если значение вне 0-100.
        """
        if not 0 <= percent <= 100:
            raise AliceError(f"🔊 Громкость должна быть от 0 до 100, получено {percent}")
        return self.send({"command": "setVolume", "volume": round(percent / 100, 2)})  # Glagol ждёт 0.0-1.0

    def volume_up(self, step=10):
        """🔼 Сделать громче на step процентов (по умолчанию 10).

        Пример:
            alice.tv.volume_up()
        """
        return self.set_volume(min(100, (self.volume or 0) + step))

    def volume_down(self, step=10):
        """🔽 Сделать тише на step процентов (по умолчанию 10).

        Пример:
            alice.tv.volume_down(20)
        """
        return self.set_volume(max(0, (self.volume or 0) - step))

    # ================================================================
    #  СОСТОЯНИЕ
    # ================================================================

    def get_state(self):
        """📊 Узнать текущее состояние устройства.

        Сразу после подключения устройство само присылает своё состояние —
        его и возвращаем.

        Returns:
            dict, например:
                {"volume": 30, "playing": True, "title": "Numb",
                 "subtitle": "Linkin Park", "raw": {...полное состояние...}}

        Пример:
            state = alice.speaker.get_state()
            print(f"Играет: {state['title']} — {state['subtitle']}, громкость {state['volume']}%")
        """
        ws = self._connect()
        try:
            ws.send(self._message({"command": "ping"}))  # 🏓 без сообщения устройство может молчать
            for _ in range(20):
                msg = json.loads(ws.recv())
                state = msg.get("state")
                if state:
                    track = (state.get("playerState") or {})
                    volume = state.get("volume")
                    return {
                        "volume": round(volume * 100) if volume is not None else None,
                        "playing": state.get("playing"),
                        "title": track.get("title") or None,
                        "subtitle": track.get("subtitle") or None,
                        "raw": state,
                    }
            raise AliceError(f"⌛ '{self.name}' не прислал своё состояние")
        except websocket.WebSocketException as e:
            raise AliceError(f"🔌 Связь с '{self.name}' оборвалась: {e}") from e
        finally:
            ws.close()

    @property
    def volume(self):
        """🔊 Текущая громкость в процентах (0-100/None). Каждый раз спрашивает устройство."""
        return self.get_state()["volume"]

    @property
    def is_playing(self):
        """▶️ Играет ли сейчас что-нибудь (True/False/None). Каждый раз спрашивает устройство."""
        return self.get_state()["playing"]

    def __repr__(self):
        kind = "📺" if self.is_tv else "🔊" if self.is_speaker else "📱"
        return f"{kind} AliceDevice('{self.name}', {self.platform}, ip={self.ip})"


class Alice:
    """🗣️ Главный класс — точка входа для управления Алисой.

    Создаётся один раз, после чего через него идёт вся работа.

    Args:
        token: OAuth-токен Яндекс Музыки (строка, начинается с "y0_").
               Если не передан — берётся из переменной окружения
               GLAGOL_TOKEN (через python-dotenv).

    Пример:
        from dotenv import load_dotenv
        from yandex_alice import Alice

        load_dotenv()
        alice = Alice()  # токен из .env

        # 📋 Посмотреть все устройства
        for dev in alice.devices:
            print(dev)

        # 📺 Телевизор и 🔊 колонка — быстрые ярлыки
        alice.tv.open_app("YouTube")
        alice.speaker.say("Привет!")

        # 🔍 Найти по имени или IP
        alice.device("Яндекс Лайт").set_volume(40)
        alice.device("192.168.1.46").pause()

        # 📢 Сказать на всех устройствах
        alice.say_everywhere("Ужин готов!")

        # 🔄 Обновить список (если IP устройства сменился)
        alice.refresh()
    """

    API_BASE = "https://quasar.yandex.net/glagol"
    TOKEN_TTL = 30 * 60  # ⏳ токен разговора живёт недолго — обновляем раз в 30 минут

    def __init__(self, token=None):
        """🔧 Создать подключение к Алисе.

        Args:
            token: OAuth-токен Яндекс Музыки (начинается с y0_).
                   Если None — берётся из env GLAGOL_TOKEN.
        """
        # 🔑 Ищем токен: аргумент → переменная окружения
        token = token or os.environ.get("GLAGOL_TOKEN")
        if not token:
            raise AliceError(
                "🔑 Токен не найден!\n"
                "   Передайте его: Alice('y0_...')\n"
                "   Или создайте файл .env со строкой:\n"
                "   GLAGOL_TOKEN=y0_...\n"
                "   Получить: https://oauth.yandex.ru/authorize?response_type=token"
                "&client_id=23cabbbdc6cd418abb4b39c32c41195d"
            )

        # ✂️ Если токен скопирован из адресной строки целиком — отрезаем &token_type=...
        token = token.strip().strip("\"'").split("&")[0]
        self._headers = {"Authorization": f"OAuth {token}"}  # ⚠️ именно "OAuth", не "Bearer"

        self._conv_tokens = {}  # 🗝️ кэш токенов разговора: device_id → (токен, время получения)
        self._data = None
        self.refresh()

    # ================================================================
    #  ВЗАИМОДЕЙСТВИЕ С API
    # ================================================================

    def _get(self, path, params=None):
        """📥 Внутренний GET-запрос к API Glagol"""
        try:
            r = requests.get(f"{self.API_BASE}{path}", headers=self._headers, params=params, timeout=15)
        except requests.exceptions.RequestException as e:
            raise AliceError(f"🌐 Ошибка сети: {e}") from e
        if r.status_code in (401, 403):
            raise AliceError(
                "🔑 Яндекс не принял токен (протух или не тот).\n"
                "   Нужен токен Яндекс Музыки, а не умного дома — получи новый и обнови GLAGOL_TOKEN"
            )
        if not r.ok:
            raise AliceError(f"🌐 Яндекс вернул {r.status_code}: {r.text[:200]}")
        return r.json()

    def _conversation_token(self, device):
        """🗝️ Одноразовый токен разговора для устройства (кэшируется на TOKEN_TTL секунд)"""
        cached = self._conv_tokens.get(device.id)
        if cached and time.time() - cached[1] < self.TOKEN_TTL:
            return cached[0]
        token = self._get("/token", {"device_id": device.id, "platform": device.platform})["token"]
        self._conv_tokens[device.id] = (token, time.time())
        return token

    def refresh(self):
        """🔄 Обновить список устройств с сервера Яндекса.

        Вызывай, если устройство сменило IP или его только что включили.

        Пример:
            alice.refresh()
            print(alice.tv.ip)  # свежий адрес
        """
        self._data = self._get("/device_list")
        return self

    # ================================================================
    #  УСТРОЙСТВА
    # ================================================================

    @property
    def devices(self):
        """📋 Все устройства с Алисой в локальной сети (list объектов AliceDevice).

        Приложения на телефоне (Алиса, Карты, Погода) тоже есть в аккаунте,
        но у них нет локального IP — их отфильтровываем.

        Пример:
            for dev in alice.devices:
                print(dev.name, dev.ip)
        """
        return [d for d in (AliceDevice(raw, self) for raw in self._data.get("devices", [])) if d.is_local]

    def device(self, name):
        """🔍 Найти устройство по имени, IP или id.

        Регистр не важен — "яндекс тв" и "Яндекс ТВ" одинаково сработают.

        Args:
            name: имя ("Яндекс ТВ"), IP ("192.168.1.46") или id устройства

        Returns:
            AliceDevice

        Пример:
            alice.device("Яндекс Лайт").say("Привет")

        Ошибка AliceError, если устройство не найдено.
        """
        key = name.strip().lower()
        for dev in self.devices:
            if key in (dev.name.lower(), dev.ip, dev.id.lower()):
                return dev
        names = ", ".join(f"'{d.name}' ({d.ip})" for d in self.devices) or "нет ни одного"
        raise AliceError(f"🔍 Устройство '{name}' не найдено. Доступны: {names}")

    @property
    def tv(self):
        """📺 Первый Яндекс ТВ в сети.

        Пример:
            alice.tv.open_app("YouTube")

        Ошибка AliceError, если телевизора нет (выключен или не в сети).
        """
        dev = next((d for d in self.devices if d.is_tv), None)
        if not dev:
            raise AliceError("📺 Яндекс ТВ не найден в сети — он включён? (попробуй alice.refresh())")
        return dev

    @property
    def speaker(self):
        """🔊 Первая колонка с Алисой в сети.

        Пример:
            alice.speaker.say("Пора спать")

        Ошибка AliceError, если колонки нет.
        """
        dev = next((d for d in self.devices if d.is_speaker), None)
        if not dev:
            raise AliceError("🔊 Колонка с Алисой не найдена в сети (попробуй alice.refresh())")
        return dev

    # ================================================================
    #  ГРУППОВЫЕ КОМАНДЫ
    # ================================================================

    def say_everywhere(self, text):
        """📢 Произнести фразу сразу на всех устройствах.

        Если какое-то устройство не ответило — остальные всё равно скажут.

        Args:
            text: что сказать

        Returns:
            dict: имя устройства → True (сказало) или текст ошибки

        Пример:
            result = alice.say_everywhere("Всем привет!")
            print(result)  # {'Яндекс ТВ': True, 'Яндекс Лайт': True}
        """
        return self._for_all(lambda dev: dev.say(text))

    def pause_all(self):
        """⏸️ Поставить на паузу все устройства («Всем тихо»).

        Returns:
            dict: имя устройства → True или текст ошибки

        Пример:
            alice.pause_all()
        """
        return self._for_all(lambda dev: dev.pause())

    def _for_all(self, action):
        """🔁 Внутренний метод — выполнить действие на каждом устройстве, не падая на ошибках"""
        result = {}
        for dev in self.devices:
            try:
                action(dev)
                result[dev.name] = True
            except AliceError as e:
                result[dev.name] = str(e)
        return result

    def __repr__(self):
        return f"🗣️ Alice({len(self.devices)} устройств: {', '.join(d.name for d in self.devices)})"
