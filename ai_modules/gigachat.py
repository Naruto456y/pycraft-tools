"""GigaChat (Сбер): чат, изображения, файлы, токены, очистка речи."""
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class GigaChatError(Exception):
    """
    ❌ ОШИБКА API GigaChat

    Наследует Exception, поэтому старый код с except Exception продолжает работать.

    Атрибуты:
        status_code (int или None): HTTP-код ответа (401, 422, 429...)
        body (str или None): Тело ответа сервера

    📌 ПРИМЕР:
        >>> try:
        ...     ai.chat("Привет")
        ... except GigaChatError as e:
        ...     print(e.status_code, e)
    """

    def __init__(self, message: str, status_code: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class GigaChat:
    """
    🤖 ИНТЕГРАЦИЯ С GigaChat (СБЕР): ЧАТ, ИЗОБРАЖЕНИЯ, ФАЙЛЫ, ТОКЕНЫ И ОЧИСТКА РЕЧИ

    Класс позволяет общаться с нейросетью GigaChat (с памятью диалога и потоковым ответом),
    отправлять изображения и документы, получать описание картинок, генерировать изображения,
    считать токены и автоматически исправлять распознанную речь (убирать заикания, слова-паразиты).

    Токен доступа живёт 30 минут: класс сам обновляет его и повторяет запрос при ошибке 401.

    📌 ПРИМЕР:
        >>> ai = GigaChat(client_id="your_id", client_secret="your_secret")
        >>> answer = ai.chat("Как дела?")
        >>> cleaned = ai.clean_speech("я э-э-э хочу пиццу")
        >>> print(ai.describe_image("photo.jpg"))
        >>> print(ai.ask_image("Сколько людей на фото?", "photo.jpg"))

    🎯 ОСНОВНЫЕ МЕТОДЫ:
        - chat(): общение с ИИ (параметры модели, память, картинки, файлы)
        - chat_stream(): ответ по кусочкам, по мере генерации
        - ask_image() / describe_image(): вопрос по изображению и его описание
        - generate_image(): создание изображения по тексту
        - clean_speech(): очистка речи от шумов и повторов
        - upload_file() / list_files() / get_file_info() / download_file() / delete_file(): файлы
        - count_tokens() / get_balance() / list_models() / embeddings(): служебные функции
        - reset_history(): очистить память диалога

    🔑 ДОСТУП:
        client_id + client_secret ИЛИ готовый «ключ авторизации» (credentials) из кабинета Сбера.
        Переменные окружения: GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, GIGACHAT_CREDENTIALS.
    """

    API_URL = "https://gigachat.devices.sberbank.ru/api/v1"     # Прежний адрес (работает)
    API_URL_NEW = "https://api.giga.chat/v1"                     # Новый адрес из документации Сбера
    AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    MAX_IMAGE_BYTES = 15 * 1024 * 1024     # Лимит изображения — 15 МБ
    MAX_FILE_BYTES = 40 * 1024 * 1024      # Лимит текстового документа — 40 МБ
    MAX_IMAGES = 10                        # Не больше 10 изображений в одном запросе
    IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp")

    IMAGE_PROMPTS = {
        "brief": "Опиши изображение одним-двумя предложениями.",
        "detailed": "Подробно опиши, что изображено на картинке: объекты, людей, цвета, обстановку и надписи.",
        "alt": "Напиши короткий alt-текст для этого изображения (до 120 символов).",
        "text": "Перепиши весь текст, который виден на изображении. Если текста нет — так и скажи.",
        "objects": "Перечисли списком все объекты, которые есть на изображении.",
    }

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 verify_ssl: bool = False, *, credentials: Optional[str] = None,
                 model: str = "GigaChat", scope: str = "GIGACHAT_API_PERS",
                 base_url: Optional[str] = None, auth_url: Optional[str] = None,
                 timeout: int = 30, ca_bundle: Optional[str] = None, system_prompt: str = "",
                 remember: bool = False, max_history: int = 20, max_retries: int = 2):
        """
        Инициализация клиента GigaChat.

        Параметры:
            client_id (str, optional): ID клиента из кабинета разработчика Сбера.
                                       По умолчанию берётся из переменной окружения GIGACHAT_CLIENT_ID.
            client_secret (str, optional): Секрет клиента.
                                           По умолчанию из переменной окружения GIGACHAT_CLIENT_SECRET.
            verify_ssl (bool): Проверять SSL-сертификаты (True — безопасно, False — только для отладки).
            credentials (str, optional): Готовый ключ авторизации (Base64 от client_id:client_secret).
                                         Вместо пары client_id/client_secret. Или переменная GIGACHAT_CREDENTIALS.
            model (str): Модель по умолчанию ('GigaChat', 'GigaChat-2-Max' и др., список: list_models()).
            scope (str): Тип доступа: 'GIGACHAT_API_PERS' (физлица), 'GIGACHAT_API_B2B', 'GIGACHAT_API_CORP'.
            base_url (str, optional): Адрес API. Новый адрес Сбера: GigaChat.API_URL_NEW ('https://api.giga.chat/v1').
            auth_url (str, optional): Адрес получения токена (по умолчанию GigaChat.AUTH_URL).
            timeout (int): Таймаут запросов в секундах.
            ca_bundle (str, optional): Путь к сертификату Минцифры (.cer/.pem) для проверки SSL вместо verify_ssl.
            system_prompt (str): Системный промпт по умолчанию для всех запросов.
            remember (bool): True — запоминать диалог (история подставляется в каждый запрос).
            max_history (int): Сколько последних сообщений хранить в памяти диалога.
            max_retries (int): Сколько раз повторять запрос при 429/502/503/504.

        Исключения:
            ValueError: Если ни client_id/client_secret, ни credentials не указаны и не найдены в окружении.
        """
        import uuid
        self.client_id = client_id or os.environ.get("GIGACHAT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("GIGACHAT_CLIENT_SECRET")
        self.credentials = credentials
        if not self.credentials and not (self.client_id and self.client_secret):
            self.credentials = os.environ.get("GIGACHAT_CREDENTIALS")
        self.verify_ssl = verify_ssl

        if not self.credentials and (not self.client_id or not self.client_secret):
            raise ValueError("Токены не найдены. Передайте client_id/client_secret (или credentials) или задайте переменные окружения GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET (или GIGACHAT_CREDENTIALS).")

        self.model = model
        self.scope = scope
        self.base_url = (base_url or self.API_URL).rstrip("/")
        self.auth_url = auth_url or self.AUTH_URL
        self.timeout = timeout
        self.ca_bundle = ca_bundle
        self.system_prompt = system_prompt
        self.remember = remember
        self.max_history = max_history
        self.max_retries = max_retries

        self.session_id = str(uuid.uuid4())      # Один ID сессии на весь диалог
        self.history: List[Dict[str, Any]] = []  # Память диалога (без системного промпта)
        self.last_usage: Optional[Dict[str, Any]] = None     # Токены последнего ответа
        self.last_response: Optional[Dict[str, Any]] = None  # Полный JSON последнего ответа
        self.last_files: List[str] = []          # ID файлов, приложенных к последнему запросу
        self._token = None
        self._token_expires_at = 0.0
        self._file_cache: Dict[Any, str] = {}    # Чтобы не загружать одну картинку дважды
        self._image_ids: set = set()

    # ---------- Внутренние методы ----------

    def _verify(self):
        """Что передавать в requests как verify (внутренний метод)."""
        return self.ca_bundle if self.ca_bundle else self.verify_ssl

    def _silence_ssl_warnings(self) -> None:
        """Отключает предупреждения urllib3, если SSL не проверяется (внутренний метод)."""
        if not self.verify_ssl and not self.ca_bundle:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @staticmethod
    def _parse_expires(value: Any) -> float:
        """Время окончания токена в секундах Unix (внутренний метод)."""
        try:
            moment = float(value)
            return moment / 1000.0 if moment > 1e11 else moment    # Сбер отдаёт миллисекунды
        except (TypeError, ValueError):
            return time.time() + 1700                               # Токен живёт 30 минут

    def _get_token(self) -> None:
        """Получает токен доступа к API GigaChat (внутренний метод)."""
        import base64
        import uuid
        from urllib.parse import urlencode
        import requests
        self._silence_ssl_warnings()

        key = self.credentials or base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {key}",
            "RqUID": str(uuid.uuid4()),
        }
        data = {"scope": self.scope}

        resp = requests.post(self.auth_url, headers=headers, data=urlencode(data),
                             verify=self._verify(), timeout=self.timeout)
        if resp.status_code == 200:
            payload = resp.json()
            self._token = payload.get("access_token")
            self._token_expires_at = self._parse_expires(payload.get("expires_at"))
        else:
            raise GigaChatError(f"Ошибка получения токена: {resp.status_code} - {resp.text}",
                                resp.status_code, resp.text)

    def _ensure_token(self) -> None:
        """Обновляет токен, если его нет или он скоро истечёт (внутренний метод)."""
        if not self._token or time.time() >= self._token_expires_at - 60:
            self._get_token()

    def _request(self, method: str, path: str, *, json_body: Optional[Dict] = None,
                 files: Optional[Dict] = None, data: Optional[Dict] = None,
                 stream: bool = False, timeout: Optional[int] = None):
        """
        Запрос к API с токеном, обновлением при 401 и повтором при 429/502/503/504 (внутренний метод).

        Исключения:
            GigaChatError: Если сервер вернул ошибку.
        """
        import requests
        self._silence_ssl_warnings()
        refreshed = False
        attempt = 0
        while True:
            self._ensure_token()
            headers = {"Authorization": f"Bearer {self._token}", "X-Session-ID": self.session_id}
            resp = requests.request(method, f"{self.base_url}{path}", headers=headers, json=json_body,
                                    files=files, data=data, stream=stream, verify=self._verify(),
                                    timeout=timeout or self.timeout)
            if resp.status_code == 401 and not refreshed:
                refreshed = True
                self._token = None            # Токен протух — получим новый и повторим
                continue
            if resp.status_code in (429, 502, 503, 504) and attempt < self.max_retries:
                attempt += 1
                try:
                    delay = float(resp.headers.get("Retry-After", 2 ** attempt))
                except ValueError:
                    delay = 2 ** attempt
                time.sleep(min(delay, 30))
                continue
            if resp.status_code >= 400:
                raise GigaChatError(f"GigaChat API error {resp.status_code}: {resp.text}",
                                    resp.status_code, resp.text)
            return resp

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        """None → [], одиночное значение → [значение] (внутренний метод)."""
        if value is None:
            return []
        return list(value) if isinstance(value, (list, tuple)) else [value]

    def _resolve_file(self, item: Any) -> str:
        """Путь, ссылка или готовый ID файла → ID файла в хранилище (внутренний метод)."""
        import re
        text = str(item)
        if re.fullmatch(r"[0-9a-fA-F-]{36}", text) and not os.path.exists(text):
            return text                                    # Это уже ID загруженного файла
        if text.lower().startswith(("http://", "https://")):
            import requests
            reply = requests.get(text, timeout=self.timeout)
            reply.raise_for_status()
            name = os.path.basename(text.split("?")[0]) or "image.jpg"
            suffix = os.path.splitext(name)[1] or ".jpg"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(reply.content)
                return self.upload_file(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        return self.upload_file(text)

    def _user_messages(self, user_text: str, images: Any, files: Any) -> List[Dict[str, Any]]:
        """Собирает сообщения пользователя с вложениями (внутренний метод)."""
        image_ids = [self._resolve_file(x) for x in self._as_list(images)]
        doc_ids = [self._resolve_file(x) for x in self._as_list(files)]
        if len(image_ids) > self.MAX_IMAGES:
            raise ValueError(f"❌ Слишком много изображений: {len(image_ids)} (максимум {self.MAX_IMAGES})")
        for fid in image_ids:
            self._image_ids.add(fid)
        self.last_files = image_ids + doc_ids

        messages = []
        for number, fid in enumerate(image_ids[:-1], 1):   # В одном сообщении — только одно изображение
            messages.append({"role": "user", "content": f"Изображение {number}:", "attachments": [fid]})
        final: Dict[str, Any] = {"role": "user", "content": user_text}
        attachments = (image_ids[-1:] if image_ids else []) + doc_ids
        if attachments:
            final["attachments"] = attachments
        messages.append(final)
        return messages

    def _limit_images(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Убирает самые старые изображения, если их больше лимита (внутренний метод)."""
        total = sum(1 for m in messages for a in m.get("attachments", []) if a in self._image_ids)
        excess = total - self.MAX_IMAGES
        if excess <= 0:
            return messages
        result = []
        for message in messages:
            attachments = message.get("attachments")
            if excess > 0 and attachments:
                kept = []
                for a in attachments:
                    if a in self._image_ids and excess > 0:
                        excess -= 1
                    else:
                        kept.append(a)
                message = {k: v for k, v in message.items() if k != "attachments"}
                if kept:
                    message["attachments"] = kept
            result.append(message)
        return result

    def _build_payload(self, user_text: str, system_text: str, temperature: float, max_tokens: int,
                       model: Optional[str], top_p: Optional[float], repetition_penalty: Optional[float],
                       images: Any, files: Any, use_history: bool, response_format: Optional[Dict],
                       function_call: Any, extra: Optional[Dict]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Собирает тело запроса chat/completions (внутренний метод)."""
        turn = self._user_messages(user_text, images, files)
        messages: List[Dict[str, Any]] = []
        system = system_text or self.system_prompt
        if system:
            messages.append({"role": "system", "content": system})
        if use_history:
            messages.extend(self.history)
        messages.extend(turn)

        payload: Dict[str, Any] = {
            "model": model or self.model,
            "messages": self._limit_images(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if top_p is not None:
            payload["top_p"] = top_p
        if repetition_penalty is not None:
            payload["repetition_penalty"] = repetition_penalty
        if response_format:
            payload["response_format"] = response_format
        if function_call is None and len([a for m in turn for a in m.get("attachments", [])
                                          if a not in self._image_ids]) > 1:
            function_call = "auto"            # Несколько документов учитываются только с function_call=auto
        if function_call:
            payload["function_call"] = function_call
        if extra:
            payload.update(extra)
        return payload, turn

    def _remember(self, turn: List[Dict[str, Any]], answer: str) -> None:
        """Добавляет обмен репликами в память диалога (внутренний метод)."""
        self.history.extend(turn)
        self.history.append({"role": "assistant", "content": answer})
        if self.max_history and len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        while self.history and self.history[0]["role"] != "user":
            self.history.pop(0)

    def _complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Отправляет chat/completions и возвращает полный ответ (внутренний метод)."""
        resp = self._request("POST", "/chat/completions", json_body=payload)
        data = resp.json()
        if not data.get("choices"):
            raise GigaChatError(f"GigaChat вернул ответ без choices: {data}", resp.status_code, resp.text)
        self.last_response = data
        self.last_usage = data.get("usage")
        return data

    # ---------- Чат ----------

    def chat(self, user_text: str, system_text: str = "", temperature: float = 0.7, max_tokens: int = 500,
             *, model: Optional[str] = None, top_p: Optional[float] = None,
             repetition_penalty: Optional[float] = None, images: Any = None, files: Any = None,
             history: Optional[bool] = None, response_format: Optional[Dict] = None,
             function_call: Any = None, extra: Optional[Dict] = None) -> str:
        """
        💬 ОТПРАВКА СООБЩЕНИЯ НЕЙРОСЕТИ И ПОЛУЧЕНИЕ ОТВЕТА

        Параметры:
            user_text (str): Текст пользователя
            system_text (str): Системный промпт (инструкция для модели). Если пусто — берётся self.system_prompt
            temperature (float): Креативность (0.0 — точный, 1.0 — творческий)
            max_tokens (int): Максимальная длина ответа в токенах
            model (str, optional): Модель для этого запроса (по умолчанию self.model)
            top_p (float, optional): Ядерная выборка от 0 до 1 (альтернатива temperature)
            repetition_penalty (float, optional): Штраф за повторы (1.0 — нейтрально, больше — меньше повторов)
            images (str или list, optional): Изображение: путь к файлу, ссылка http(s) или ID уже загруженного файла.
                                             Можно списком (до 10).
            files (str или list, optional): Документы (txt, pdf, docx, xlsx...), аналогично images
            history (bool, optional): Использовать память диалога (None — как задано в remember)
            response_format (dict, optional): Структурированный ответ, например
                                              {"type": "json_schema", "schema": {...}, "strict": False}
            function_call (str или dict, optional): 'auto', 'none' или {"name": "..."} (работа с функциями)
            extra (dict, optional): Любые дополнительные поля тела запроса (functions и т.п.)

        Возвращает:
            str: Ответ нейросети

        Исключения:
            GigaChatError: Если сервер вернул ошибку.
            FileNotFoundError: Если файл для images/files не найден.

        Пример:
            >>> ai = GigaChat()
            >>> reply = ai.chat("Напиши стих про Python", temperature=0.8)
            >>> print(reply)
            >>> ai.chat("Что на фото?", images="photo.jpg")
            >>> print(ai.last_usage)   # {'prompt_tokens': ..., 'completion_tokens': ..., ...}

        Примечание:
            Одно сообщение может содержать только одно изображение, поэтому несколько картинок
            уходят отдельными сообщениями (для нескольких изображений это не проверено на реальном API).
            Несколько документов за раз учитываются только при function_call='auto' — он ставится сам.
        """
        use_history = self.remember if history is None else history
        
        # --- ИСПРАВЛЕНИЕ: Если переданы картинки, а модель не указана явно, используем GigaChat-2-Max ---
        if images and model is None:
            model = "GigaChat-2-Max"
        # -----------------------------------------------------------------------------------------

        payload, turn = self._build_payload(user_text, system_text, temperature, max_tokens, model, top_p,
                                            repetition_penalty, images, files, use_history,
                                            response_format, function_call, extra)
        data = self._complete(payload)
        answer = data["choices"][0]["message"].get("content", "")
        if use_history:
            self._remember(turn, answer)
        return answer

    def chat_stream(self, user_text: str, system_text: str = "", temperature: float = 0.7,
                    max_tokens: int = 500, *, model: Optional[str] = None, top_p: Optional[float] = None,
                    repetition_penalty: Optional[float] = None, update_interval: float = 0,
                    images: Any = None, files: Any = None, history: Optional[bool] = None,
                    extra: Optional[Dict] = None) -> Any:
        """
        ⚡ ПОТОКОВЫЙ ОТВЕТ — ТЕКСТ ПРИХОДИТ КУСОЧКАМИ ПО МЕРЕ ГЕНЕРАЦИИ

        Параметры:
            user_text, system_text, temperature, max_tokens, model, top_p, repetition_penalty,
            images, files, history, extra: Как в chat()
            update_interval (float): Минимальный интервал (сек) между отправками токенов (0 — сразу)

        Возвращает:
            generator[str]: Генератор кусочков текста

        Пример:
            >>> for piece in ai.chat_stream("Расскажи про роботов"):
            ...     print(piece, end="", flush=True)

        Примечание:
            В память диалога ответ попадает после того, как генератор полностью прочитан.
            Статистика токенов сохраняется в ai.last_usage.
        """
        use_history = self.remember if history is None else history
        
        # --- ИСПРАВЛЕНИЕ: Если переданы картинки, а модель не указана явно, используем GigaChat-2-Max ---
        if images and model is None:
            model = "GigaChat-2-Max"
        # -----------------------------------------------------------------------------------------

        payload, turn = self._build_payload(user_text, system_text, temperature, max_tokens, model, top_p,
                                            repetition_penalty, images, files, use_history,
                                            None, None, extra)
        payload["stream"] = True
        payload["update_interval"] = update_interval

        resp = self._request("POST", "/chat/completions", json_body=payload, stream=True)
        resp.encoding = "utf-8"
        parts: List[str] = []
        try:
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                obj = json.loads(chunk)
                if obj.get("usage"):
                    self.last_usage = obj["usage"]
                choices = obj.get("choices") or [{}]
                piece = (choices[0].get("delta") or {}).get("content") or ""
                if piece:
                    parts.append(piece)
                    yield piece
        finally:
            resp.close()
        if use_history:
            self._remember(turn, "".join(parts))

    def reset_history(self) -> None:
        """
        🧹 ОЧИСТИТЬ ПАМЯТЬ ДИАЛОГА

        Пример:
            >>> ai = GigaChat(remember=True)
            >>> ai.chat("Меня зовут Юсуф")
            >>> ai.reset_history()
        """
        self.history = []

    def clean_speech(self, raw_text: str) -> str:
        """
        🎤 ОЧИСТКА РАСПОЗНАННОЙ РЕЧИ ОТ ЗАИКАНИЙ И СЛОВ-ПАРАЗИТОВ

        Параметры:
            raw_text (str): Сырой текст с возможными артефактами

        Возвращает:
            str: Грамматически правильный русский текст

        Пример:
            >>> clean = ai.clean_speech("я э-э-э хочу вот типа пиццу")
            >>> print(clean)  # "Я хочу пиццу"

        Примечание:
            Внутри отправляет запрос к GigaChat с низкой температурой (0.2).
            Память диалога не используется и не засоряется.
        """
        system_prompt = """
            Ты — аудио-корректор. Получив текст, который может содержать:
            - запинки и заикания («э-э-э», «ну-у-у»),
            - слова-паразиты («вот», «короче», «типа»),
            - ошибки распознавания речи (шум микрофона).

            Верни ТОЛЬКО чистый, грамматически правильный русский текст.
            Не добавляй ничего от себя.
            """
        return self.chat(
            user_text=raw_text,
            system_text=system_prompt,
            temperature=0.2,
            max_tokens=200,
            history=False
        )

    # ---------- Изображения ----------

    def ask_image(self, question: str, image: Any, *, system_text: str = "", temperature: float = 0.2,
                  max_tokens: int = 500, model: Optional[str] = None, top_p: Optional[float] = None,
                  history: Optional[bool] = None, delete_after: bool = False,
                  extra: Optional[Dict] = None) -> str:
        """
        🖼️ ВОПРОС ПО ИЗОБРАЖЕНИЮ

        Параметры:
            question (str): Вопрос к картинке («Что здесь изображено?», «Сколько людей на фото?»)
            image (str или list): Путь к файлу, ссылка http(s) или ID загруженного файла (или список до 10)
            system_text (str): Системный промпт
            temperature (float): Креативность (для описаний лучше низкая)
            max_tokens (int): Максимальная длина ответа
            model (str, optional): Модель (если не указана, автоматически используется GigaChat-2-Max)
            top_p (float, optional): Ядерная выборка
            history (bool, optional): Использовать память диалога (для уточняющих вопросов к той же картинке)
            delete_after (bool): Удалить загруженные файлы из хранилища после ответа (не используй с памятью диалога)
            extra (dict, optional): Дополнительные поля запроса

        Возвращает:
            str: Ответ нейросети

        Пример:
            >>> ai = GigaChat(remember=True)
            >>> print(ai.ask_image("Что на фото?", "cat.jpg"))
            >>> print(ai.ask_image("А какого он цвета?", "cat.jpg"))   # та же картинка не загружается повторно

        Примечание:
            Лимиты: изображение до 15 МБ, не больше 10 изображений в запросе. Повторно та же картинка
            не загружается (ID берётся из кэша).
        """
        answer = self.chat(question, system_text=system_text, temperature=temperature,
                           max_tokens=max_tokens, model=model, top_p=top_p, images=image,
                           history=history, extra=extra)
        if delete_after:
            for file_id in list(self.last_files):
                self.delete_file(file_id)
        return answer

    def describe_image(self, image: Any, style: str = "detailed", prompt: Optional[str] = None,
                       **kwargs) -> str:
        """
        👁️ ОПИСАНИЕ ИЗОБРАЖЕНИЯ

        Параметры:
            image (str или list): Путь к файлу, ссылка http(s) или ID загруженного файла
            style (str): 'brief' (1-2 предложения), 'detailed' (подробно), 'alt' (alt-текст),
                         'text' (переписать надписи с картинки), 'objects' (список объектов)
            prompt (str, optional): Свой запрос вместо готового стиля
            **kwargs: Параметры ask_image() (model, temperature, max_tokens, delete_after...)

        Возвращает:
            str: Описание изображения

        Исключения:
            ValueError: Если указан неизвестный style.

        Пример:
            >>> print(ai.describe_image("photo.jpg"))
            >>> print(ai.describe_image("sign.png", style="text"))
            >>> print(ai.describe_image("room.jpg", prompt="Опиши мебель в комнате"))
        """
        if prompt is None:
            if style not in self.IMAGE_PROMPTS:
                raise ValueError(f"❌ Неизвестный style '{style}'. Доступны: {', '.join(self.IMAGE_PROMPTS)}")
            prompt = self.IMAGE_PROMPTS[style]
        return self.ask_image(prompt, image, **kwargs)

    def generate_image(self, prompt: str, save_path: str = "gigachat_image.jpg", *,
                       model: Optional[str] = None) -> str:
        """
        🎨 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ ПО ТЕКСТУ

        Параметры:
            prompt (str): Что нарисовать («розовый кот в космосе»)
            save_path (str): Куда сохранить картинку
            model (str, optional): Модель (по умолчанию GigaChat-2-Max)

        Возвращает:
            str: Путь к сохранённому изображению

        Исключения:
            GigaChatError: Если модель не вернула изображение.

        Пример:
            >>> path = ai.generate_image("уютный робот читает книгу")
            >>> print(path)

        Примечание:
            Работает через встроенную функцию генерации (function_call='auto'). ID картинки берётся
            из тега <img src="..."/> в ответе. Эта функция сделана по документации Сбера и не проверялась
            на реальном API.
        """
        import re
        text = prompt if "нарису" in prompt.lower() else f"Нарисуй: {prompt}"
        
        # --- ИСПРАВЛЕНИЕ: Для генерации картинок нужна модель GigaChat-2-Max ---
        payload = {"model": model or "GigaChat-2-Max", "function_call": "auto",
                   "messages": [{"role": "user", "content": text}]}
        # ----------------------------------------------------------------------

        content = self._complete(payload)["choices"][0]["message"].get("content", "") or ""
        found = re.search(r'<img[^>]*\bsrc="([^"]+)"', content)
        if not found:
            raise GigaChatError(f"Модель не вернула изображение. Ответ: {content[:200]}")
        return self.download_file(found.group(1), save_path)

    # ---------- Файлы ----------

    def upload_file(self, path: str, purpose: str = "general", reuse: bool = True) -> str:
        """
        📤 ЗАГРУЗКА ФАЙЛА В ХРАНИЛИЩЕ GigaChat

        Параметры:
            path (str): Путь к файлу (изображение до 15 МБ, документ до 40 МБ)
            purpose (str): Назначение (сейчас только 'general')
            reuse (bool): Не загружать повторно тот же неизменённый файл

        Возвращает:
            str: ID файла (его можно передавать в images=/files=)

        Исключения:
            FileNotFoundError: Если файла нет.
            ValueError: Если файл больше лимита.

        Пример:
            >>> file_id = ai.upload_file("report.pdf")
            >>> ai.chat("Сделай краткое резюме", files=file_id)
        """
        import mimetypes
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"❌ Файл не найден: {path}")
        is_image = file_path.suffix.lower() in self.IMAGE_EXTENSIONS
        size = file_path.stat().st_size
        limit = self.MAX_IMAGE_BYTES if is_image else self.MAX_FILE_BYTES
        if size > limit:
            raise ValueError(f"❌ Файл слишком большой: {size / 1048576:.1f} МБ (лимит {limit // 1048576} МБ)")

        cache_key = (str(file_path.resolve()), size, int(file_path.stat().st_mtime))
        if reuse and cache_key in self._file_cache:
            return self._file_cache[cache_key]

        mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        content = file_path.read_bytes()
        resp = self._request("POST", "/files", files={"file": (file_path.name, content, mime)},
                             data={"purpose": purpose}, timeout=max(self.timeout, 60))
        file_id = resp.json()["id"]
        self._file_cache[cache_key] = file_id
        if is_image:
            self._image_ids.add(file_id)
        return file_id

    def list_files(self) -> List[Dict[str, Any]]:
        """
        📂 СПИСОК ЗАГРУЖЕННЫХ ФАЙЛОВ

        Возвращает:
            List[dict]: Файлы с полями id, filename, bytes, created_at, purpose...

        Пример:
            >>> for f in ai.list_files():
            ...     print(f["id"], f["filename"])
        """
        return self._request("GET", "/files").json().get("data", [])

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        ℹ️ ИНФОРМАЦИЯ О ФАЙЛЕ

        Параметры:
            file_id (str): ID файла

        Возвращает:
            dict: id, filename, bytes, created_at, purpose, access_policy

        Пример:
            >>> print(ai.get_file_info(file_id)["filename"])
        """
        return self._request("GET", f"/files/{file_id}").json()

    def download_file(self, file_id: str, save_path: str) -> str:
        """
        📥 СКАЧИВАНИЕ ФАЙЛА ИЗ ХРАНИЛИЩА (например, сгенерированной картинки)

        Параметры:
            file_id (str): ID файла
            save_path (str): Куда сохранить

        Возвращает:
            str: Путь к сохранённому файлу

        Пример:
            >>> ai.download_file(file_id, "result.jpg")
        """
        content = self._request("GET", f"/files/{file_id}/content").content
        folder = os.path.dirname(os.path.abspath(save_path))
        os.makedirs(folder, exist_ok=True)
        with open(save_path, "wb") as handle:
            handle.write(content)
        return save_path

    def delete_file(self, file_id: str) -> bool:
        """
        🗑️ УДАЛЕНИЕ ФАЙЛА ИЗ ХРАНИЛИЩА

        Параметры:
            file_id (str): ID файла

        Возвращает:
            bool: True, если файл удалён

        Пример:
            >>> ai.delete_file(file_id)
        """
        result = self._request("POST", f"/files/{file_id}/delete").json()
        self._image_ids.discard(file_id)
        self._file_cache = {k: v for k, v in self._file_cache.items() if v != file_id}
        return bool(result.get("deleted", False))

    # ---------- Служебные функции ----------

    def count_tokens(self, text: Union[str, List[str]], model: Optional[str] = None) -> Union[int, List[int]]:
        """
        🔢 ПОДСЧЁТ ТОКЕНОВ В ТЕКСТЕ

        Параметры:
            text (str или list): Текст или список текстов
            model (str, optional): Модель (у разных моделей токенизация может отличаться)

        Возвращает:
            int или List[int]: Число токенов (число для строки, список для списка)

        Пример:
            >>> print(ai.count_tokens("Привет, как дела?"))
            >>> print(ai.count_tokens(["раз", "два три"]))
        """
        texts = [text] if isinstance(text, str) else list(text)
        data = self._request("POST", "/tokens/count",
                             json_body={"model": model or self.model, "input": texts}).json()
        items = data if isinstance(data, list) else data.get("data", [])
        counts = [int(item["tokens"]) for item in items]
        return counts[0] if isinstance(text, str) else counts

    def get_balance(self) -> Dict[str, int]:
        """
        💰 ОСТАТОК ТОКЕНОВ

        Возвращает:
            dict: {"GigaChat": 1000000, ...} — остаток токенов по моделям

        Исключения:
            GigaChatError: Если метод недоступен (при оплате pay-as-you-go сервер отвечает 403).

        Пример:
            >>> print(ai.get_balance())
        """
        data = self._request("GET", "/balance").json()
        return {item["usage"]: item["value"] for item in data.get("balance", [])}

    def list_models(self, kind: Optional[str] = "chat") -> List[str]:
        """
        📜 СПИСОК ДОСТУПНЫХ МОДЕЛЕЙ

        Параметры:
            kind (str, optional): Тип: 'chat' (чат), 'embedder' (эмбеддинги), 'aicheck'. None — все

        Возвращает:
            List[str]: Названия моделей (значения для параметра model)

        Пример:
            >>> print(ai.list_models())
            >>> ai.model = ai.list_models()[0]
        """
        data = self._request("GET", "/models").json().get("data", [])
        return [m["id"] for m in data if kind is None or m.get("type") == kind]

    def embeddings(self, texts: Union[str, List[str]], model: str = "Embeddings") -> List[List[float]]:
        """
        🧬 ЭМБЕДДИНГИ (ВЕКТОРНОЕ ПРЕДСТАВЛЕНИЕ ТЕКСТА)

        Параметры:
            texts (str или list): Текст или список текстов
            model (str): 'Embeddings', 'Embeddings-2' или 'EmbeddingsGigaR'

        Возвращает:
            List[List[float]]: Вектор для каждого текста (в том же порядке)

        Пример:
            >>> vectors = ai.embeddings(["кошка", "собака"])
            >>> print(len(vectors), len(vectors[0]))
        """
        items = [texts] if isinstance(texts, str) else list(texts)
        data = self._request("POST", "/embeddings", json_body={"model": model, "input": items}).json()
        rows = sorted(data.get("data", []), key=lambda row: row.get("index", 0))
        return [row["embedding"] for row in rows]