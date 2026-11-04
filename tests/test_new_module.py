#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
📦 HELP_MANAGER.PY — УНИВЕРСАЛЬНЫЙ ПОМОЩНИК НА PYTHON
================================================================================
Всё в одном файле: голос, базы данных, музыка, парсинг, автоматизация и ИИ.
Версия: 1.1.2
Автор: Юсуф
================================================================================
"""

import os
import sys
import time
import random
import threading
import json
from datetime import datetime
import socket
import subprocess
import webbrowser
import tempfile
import sqlite3
import math
import statistics
import string
from typing import Any, Callable, Optional, Tuple, List, Dict, Union
from urllib.parse import quote
import shutil
import inspect
from pathlib import Path
import hashlib

# =============================================================================
# КЛАСС Manager – 30+ УНИВЕРСАЛЬНЫХ ФУНКЦИЙ
# =============================================================================

class Manager:
    """
    ⚡ УНИВЕРСАЛЬНЫЙ МЕНЕДЖЕР — статические методы для повседневных задач.

    Все методы вызываются напрямую без создания экземпляра класса.

    📌 ВОЗМОЖНОСТИ:
        - Парсинг веб-страниц и получение погоды
        - Голосовой ввод и озвучка текста (TTS)
        - Работа с файлами и JSON
        - Время, дата, случайные числа
        - Проверка интернета, скачивание файлов
        - Поиск и открытие видео на YouTube
        - Очистка консоли, задержки, звуковые сигналы (кроссплатформенно)
        - Загрузка переменных окружения из .env

    📌 ПРИМЕР:
        >>> from help_manager import Manager
        >>> Manager.say("Привет, мир!")
        >>> weather = Manager.get_weather("Москва")
        >>> print(weather["Температура"])
    """

    # -------------------------------------------------------------------------
    # 🌐 ПАРСИНГ И ПОГОДА
    # -------------------------------------------------------------------------

    @staticmethod
    def get_text_with_url(url: str, class_name: str) -> str:
        """
        🔍 ИЗВЛЕЧЕНИЕ ТЕКСТА С ВЕБ-СТРАНИЦЫ ПО CSS-КЛАССУ

        Параметры:
            url (str): Полный URL страницы (например, "https://example.com")
            class_name (str): Имя CSS-класса, содержимое которого нужно извлечь

        Возвращает:
            str: Текст элемента или сообщение об ошибке

        Пример:
            >>> title = Manager.get_text_with_url("https://example.com", "article__title")
            >>> print(title)

        Примечание:
            Используется библиотеки requests и BeautifulSoup4.
            Не требует предварительного кодирования URL.
        """
        import requests
        from bs4 import BeautifulSoup

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            element = soup.find(class_=class_name)
            return element.text.strip() if element else f"❌ Класс '{class_name}' не найден"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @staticmethod
    def get_weather(city: str = "Москва", api_key: Optional[str] = None) -> Union[Dict[str, str], str]:
        """
        ☁️ ПОЛУЧЕНИЕ ТЕКУЩЕЙ ПОГОДЫ ДЛЯ ГОРОДА

        Параметры:
            city (str): Название города (по умолчанию "Москва")
            api_key (str, optional): API-ключ OpenWeatherMap. Если не указан, используется встроенный.

        Возвращает:
            dict: Словарь с ключами:
                - "Температура" (str)
                - "Ощущается" (str)
                - "Описание" (str)
                - "Влажность" (str)
                - "Ветер" (str)
            Или строку с ошибкой при неудаче.

        Пример:
            >>> weather = Manager.get_weather("Санкт-Петербург")
            >>> print(weather["Температура"])  # "+12 °C"

        Примечание:
            Для работы требуется интернет-соединение.
        """
        import requests
        if api_key is None:
            api_key = os.environ.get("OPENWEATHER_API_KEY")

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "Температура": f"{round(data['main']['temp'])} °C",
                "Ощущается": f"{round(data['main']['feels_like'])} °C",
                "Описание": data['weather'][0]['description'],
                "Влажность": f"{data['main']['humidity']} %",
                "Ветер": f"{data['wind']['speed']} м/с"
            }
        except Exception as e:
            return f"❌ Ошибка погоды: {e}"

    # -------------------------------------------------------------------------
    # 🎙️ ГОЛОС И ЗВУК
    # -------------------------------------------------------------------------

    @staticmethod
    def listen_text(seconds: int = 5) -> str:
        """
        🎤 РАСПОЗНАВАНИЕ РЕЧИ (SPEECH-TO-TEXT)

        Параметры:
            seconds (int): Время прослушивания в секундах (по умолчанию 5)

        Возвращает:
            str: Распознанный текст (русский язык) или пустую строку, если ничего не услышано.

        Пример:
            >>> command = Manager.listen_text(5)
            >>> if command:
            ...     print(f"Вы сказали: {command}")

        Примечание:
            Требуется микрофон и интернет (используется Google Speech Recognition).
            Автоматически настраивается шумоподавление.
        """
        import speech_recognition as sr
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=seconds, phrase_time_limit=seconds)
            return r.recognize_google(audio, language="ru-RU")
        except Exception:
            return ""

    @staticmethod
    def say(text: str, lang: str = 'ru') -> None:
        """
        🔊 ОЗВУЧКА ТЕКСТА (TTS) — ПРЕВРАЩАЕТ ТЕКСТ В РЕЧЬ

        Параметры:
            text (str): Текст для озвучивания
            lang (str): Язык ('ru' — русский, 'en' — английский, и т.д.)

        Пример:
            >>> Manager.say("Привет, я твой помощник!")
            >>> Manager.say("Hello, world!", lang='en')

        Примечание:
            Используется Google TTS и pydub. Требуется интернет.
            Временные файлы автоматически удаляются.
        """
        from gtts import gTTS
        from pydub import AudioSegment
        from pydub.playback import play

        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
                temp_file = fp.name
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_file)
            sound = AudioSegment.from_mp3(temp_file)
            play(sound)
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    @staticmethod
    def play_music(file_path: str) -> None:
        """
        🎵 ВОСПРОИЗВЕДЕНИЕ АУДИОФАЙЛА (MP3, WAV, OGG)

        Параметры:
            file_path (str): Полный путь к аудиофайлу

        Пример:
            >>> Manager.play_music("C:/Music/song.mp3")

        Примечание:
            Используется pygame.mixer. Функция блокирует выполнение до окончания трека.
        """
        import pygame
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Ошибка воспроизведения: {e}")

    # -------------------------------------------------------------------------
    # 📂 ФАЙЛЫ И ПУТИ
    # -------------------------------------------------------------------------

    @staticmethod
    def search_file_path(relative_path: str) -> str:
        """
        📁 ПОЛУЧЕНИЕ АБСОЛЮТНОГО ПУТИ К ФАЙЛУ ОТНОСИТЕЛЬНО ПАПКИ СКРИПТА

        Параметры:
            relative_path (str): Относительный путь (например, "config.json")

        Возвращает:
            str: Полный абсолютный путь

        Пример:
            >>> full = Manager.search_file_path("data/settings.json")
            >>> print(full)  # C:\\Projects\\script\\data\\settings.json

        Примечание:
            Удобно для доступа к файлам, расположенным рядом с исполняемым скриптом.
        """
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, relative_path)

    @staticmethod
    def open_file(relative_path: str) -> None:
        """
        🚀 ЗАПУСК PYTHON-СКРИПТА В НОВОМ ОКНЕ КОНСОЛИ (Windows)

        Параметры:
            relative_path (str): Путь к .py файлу относительно папки скрипта

        Пример:
            >>> Manager.open_file("bot.py")

        Внимание:
            Работает только в Windows. На других ОС выводит предупреждение.
        """
        if sys.platform == "win32":
            full = Manager.search_file_path(relative_path)
            os.system(f'start cmd /k python "{full}"')
        else:
            print("⚠️ open_file() поддерживается только в Windows")

    @staticmethod
    def search_and_open_youtube(query: str, max_results: int = 1) -> Union[str, bool]:
        """
        🔍 ПОИСК ВИДЕО НА YOUTUBE И ОТКРЫТИЕ В БРАУЗЕРЕ

        Параметры:
            query (str): Поисковый запрос (название видео, песни и т.д.)
            max_results (int): Количество результатов поиска (по умолчанию 1)

        Возвращает:
            str или False: URL открытого видео или False, если ничего не найдено

        Пример:
            >>> url = Manager.search_and_open_youtube("Morgenshtern Cadillac")
            >>> if url:
            ...     print(f"Открыто: {url}")

        Примечание:
            Требуется интернет и установленная библиотека youtube-search.
        """
        from youtube_search import YoutubeSearch
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        if results:
            video_url = f"https://youtube.com{results[0]['url_suffix']}"
            webbrowser.open(video_url)
            return video_url
        return False

    @staticmethod
    def load_json(relative_path: str) -> Optional[Dict]:
        """
        📂 ЗАГРУЗКА ДАННЫХ ИЗ JSON-ФАЙЛА

        Параметры:
            relative_path (str): Путь к JSON-файлу относительно папки скрипта

        Возвращает:
            dict или None: Содержимое файла в виде словаря, или None при ошибке

        Пример:
            >>> config = Manager.load_json("settings.json")
            >>> if config:
            ...     theme = config.get("theme", "light")
        """
        full = Manager.search_file_path(relative_path)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки JSON: {e}")
            return None

    @staticmethod
    def save_json(relative_path: str, data: Dict, mode: str = "w") -> bool:
        """
        💾 СОХРАНЕНИЕ ДАННЫХ В JSON-ФАЙЛ

        Параметры:
            relative_path (str): Путь к JSON-файлу относительно папки скрипта
            data (dict): Данные для сохранения
            mode (str): Режим записи ("w" — перезапись, "a" — добавление)

        Возвращает:
            bool: True при успехе, False при ошибке

        Пример:
            >>> settings = {"theme": "dark", "volume": 80}
            >>> Manager.save_json("settings.json", settings)
        """
        full = Manager.search_file_path(relative_path)
        try:
            with open(full, mode, encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения JSON: {e}")
            return False

    # -------------------------------------------------------------------------
    # ⏰ ВРЕМЯ И ДАТА
    # -------------------------------------------------------------------------

    @staticmethod
    def now(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        🕐 ТЕКУЩАЯ ДАТА И ВРЕМЯ В ЗАДАННОМ ФОРМАТЕ

        Параметры:
            format_str (str): Формат даты/времени (по умолчанию "ГГГГ-ММ-ДД ЧЧ:ММ:СС")

        Возвращает:
            str: Отформатированная строка

        Пример:
            >>> Manager.now("%H:%M")   # "15:30"
            >>> Manager.now("%d.%m.%Y") # "27.05.2026"
        """
        return datetime.now().strftime(format_str)

    @staticmethod
    def today() -> str:
        """
        📅 СЕГОДНЯШНЯЯ ДАТА В ФОРМАТЕ ГГГГ-ММ-ДД

        Возвращает:
            str: Дата, например "2026-05-27"

        Пример:
            >>> date = Manager.today()
            >>> backup_name = f"backup_{date}.json"
        """
        return datetime.now().strftime("%Y-%m-%d")

    # -------------------------------------------------------------------------
    # 🎲 СЛУЧАЙНОСТИ
    # -------------------------------------------------------------------------

    @staticmethod
    def randint(a: int, b: int) -> int:
        """
        🎲 СЛУЧАЙНОЕ ЦЕЛОЕ ЧИСЛО В ДИАПАЗОНЕ [a, b] (ВКЛЮЧИТЕЛЬНО)

        Параметры:
            a (int): Нижняя граница
            b (int): Верхняя граница

        Возвращает:
            int: Случайное число

        Пример:
            >>> dice = Manager.randint(1, 6)
        """
        return random.randint(a, b)

    @staticmethod
    def choice(seq: Union[List, Tuple, str]) -> Any:
        """
        🎲 СЛУЧАЙНЫЙ ЭЛЕМЕНТ ИЗ ПОСЛЕДОВАТЕЛЬНОСТИ

        Параметры:
            seq (list/tuple/str): Последовательность

        Возвращает:
            any: Случайный элемент

        Пример:
            >>> fruit = Manager.choice(["яблоко", "банан", "груша"])
        """
        return random.choice(seq)

    # -------------------------------------------------------------------------
    # 🌐 СЕТЬ
    # -------------------------------------------------------------------------

    @staticmethod
    def is_connected() -> bool:
        """
        🌐 ПРОВЕРКА НАЛИЧИЯ ИНТЕРНЕТ-СОЕДИНЕНИЯ

        Возвращает:
            bool: True, если интернет есть, иначе False

        Пример:
            >>> if Manager.is_connected():
            ...     weather = Manager.get_weather("Москва")
        """
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False

    @staticmethod
    def download_file(url: str, save_path: str) -> bool:
        """
        📥 СКАЧИВАНИЕ ФАЙЛА ИЗ ИНТЕРНЕТА

        Параметры:
            url (str): Прямая ссылка на файл
            save_path (str): Путь для сохранения (относительно папки скрипта)

        Возвращает:
            bool: True при успехе, False при ошибке

        Пример:
            >>> success = Manager.download_file("https://site.com/image.jpg", "images/photo.jpg")
        """
        import requests
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            full = Manager.search_file_path(save_path)
            with open(full, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False

    # -------------------------------------------------------------------------
    # 🛠️ ПРОЧЕЕ
    # -------------------------------------------------------------------------

    @staticmethod
    def load_env(env_path: Optional[str] = None) -> None:
        """
        🔧 ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ИЗ .env ФАЙЛА

        Параметры:
            env_path (str, optional): Путь к .env файлу. По умолчанию ~/.env

        Пример:
            >>> Manager.load_env()  # загрузит из домашней папки
            >>> Manager.load_env(".env")  # из текущей директории

        Примечание:
            Требуется установка python-dotenv. Если библиотека не найдена, выводится предупреждение.
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            print("⚠️ Библиотека python-dotenv не установлена. Пропускаем загрузку .env")
            return

        if env_path is None:
            env_path = Path.home() / ".env"
        else:
            env_path = Path(env_path)

        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Переменные загружены из {env_path}")
        else:
            print(f"⚠️ Файл {env_path} не найден.")

    @staticmethod
    def clear_console() -> None:
        """
        🧹 ОЧИСТКА ЭКРАНА КОНСОЛИ / ТЕРМИНАЛА

        Пример:
            >>> Manager.clear_console()
            >>> print("Новый чистый вывод!")

        Примечание:
            Работает и в Windows, и в Linux/macOS.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def wait(seconds: float, message: str = "Ждём...") -> None:
        """
        ⏳ ПАУЗА С ОТОБРАЖЕНИЕМ СООБЩЕНИЯ

        Параметры:
            seconds (float): Время задержки в секундах
            message (str): Сообщение, отображаемое во время ожидания

        Пример:
            >>> Manager.wait(3, "Загрузка данных...")
            >>> print("Готово!")
        """
        print(message)
        time.sleep(seconds)

    @staticmethod
    def beep(frequency: int = 1000, duration_ms: int = 500) -> None:
        """
        🔊 СИСТЕМНЫЙ ЗВУКОВОЙ СИГНАЛ (КРОССПЛАТФОРМЕННЫЙ)

        Параметры:
            frequency (int): Частота звука в герцах (только для Windows)
            duration_ms (int): Длительность сигнала в миллисекундах

        Пример:
            >>> Manager.beep(1000, 500)   # стандартный звук
            >>> Manager.beep(500, 200)    # низкий короткий сигнал

        Примечание:
            На Windows используется winsound.Beep, на Linux — терминальный beep (printf '\a'),
            на macOS — osascript beep.
        """
        import platform
        system = platform.system()
        if system == 'Windows':
            try:
                from winsound import Beep
                Beep(frequency, duration_ms)
            except Exception:
                print("❌ Не удалось воспроизвести звуковой сигнал")
        elif system == 'Linux':
            try:
                subprocess.run(['printf', '\a'], check=False)
                time.sleep(duration_ms / 1000.0)
            except Exception:
                print("❌ Не удалось воспроизвести звуковой сигнал")
        elif system == 'Darwin':
            try:
                subprocess.run(['osascript', '-e', f'beep {duration_ms//100}'], check=False)
            except Exception:
                print("❌ Не удалось воспроизвести звуковой сигнал")
        else:
            print("⚠️ Звуковой сигнал не поддерживается на этой ОС")


# =============================================================================
# КЛАСС GigaChat – ИИ ОТ СБЕРБАНКА
# =============================================================================

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


# =================================================================================================
# КЛАСС Voice – ГОЛОС: РАСПОЗНАВАНИЕ И СИНТЕЗ РЕЧИ (GOOGLE, VOSK, GIGAAM, WHISPER, SILERO, EDGE...)
# =================================================================================================

class Voice:
    """
    🎙️ ГОЛОС — РАСПОЗНАВАНИЕ (STT) И СИНТЕЗ (TTS) РЕЧИ В ОДНОМ КЛАССЕ

    Все методы статические. Движок можно выбрать параметром engine (общие функции
    say() и listen()) или вызвать его отдельную функцию: say_silero(), listen_vosk() и т.д.

    📌 РАСПОЗНАВАНИЕ РЕЧИ (STT):
        - google  — онлайн, Google Speech Recognition (как в Manager.listen_text)
        - vosk    — офлайн, лёгкий, потоковый, умеет ограничивать словарь (идеально для команд)
        - gigaam  — офлайн, Сбер GigaAM, один из лучших для русского (нужен torch)
        - whisper — офлайн, faster-whisper, много языков

    📌 СИНТЕЗ РЕЧИ (TTS):
        - gtts    — онлайн, Google TTS (как в Manager.say)
        - silero  — офлайн, нейросеть, лучший офлайн-голос для русского (нужен torch)
        - edge    — онлайн, нейроголоса Microsoft Edge (свои темп, тембр и громкость)
        - pyttsx3 — офлайн, голоса операционной системы (SAPI5 на Windows)

    📌 ТЕМП, ТЕМБР И ГРОМКОСТЬ ДЛЯ ЛЮБОГО ДВИЖКА:
        У каждой say_*() есть параметры speed (темп), pitch_shift (тембр в полутонах)
        и gain (громкость). Они применяются поверх готового звука, поэтому работают
        даже там, где у самого движка такой настройки нет (gTTS, pyttsx3, Silero).

    📌 ТРЕБОВАНИЯ (ставятся только под тот движок, который используешь):
        - Общее: numpy, soundfile, sounddevice (запись и воспроизведение), ffmpeg (темп и тембр)
        - google: SpeechRecognition + PyAudio | vosk: vosk | whisper: faster-whisper
        - gigaam: torch + gigaam (pip install https://github.com/salute-developers/GigaAM/archive/refs/heads/main.zip --no-deps)
        - gtts: gTTS | silero: torch | edge: edge-tts | pyttsx3: pyttsx3

    📌 ПРИМЕРЫ:
        >>> Voice.say("Привет, я Кеша!")                                    # gTTS, как Manager.say
        >>> Voice.say("Привет!", engine="silero", voice="aidar", pitch_shift=-2)
        >>> Voice.say_edge("Привет!", voice="ru-RU-DmitryNeural", rate=15)
        >>> text = Voice.listen(engine="gigaam", seconds=8)
        >>> cmd = Voice.listen_vosk(grammar=["включи свет", "выключи свет"])
        >>> text = Voice.transcribe_file("my_voice.wav", engine="whisper")
        >>> Voice.check()                                                   # что установлено
    """

    # -------------------------------------------------------------------------
    # ⚙️ НАСТРОЙКИ И СПРАВОЧНИКИ
    # -------------------------------------------------------------------------

    STT_ENGINES = ("google", "vosk", "gigaam", "whisper")
    TTS_ENGINES = ("gtts", "silero", "edge", "pyttsx3")

    DEFAULT_STT = "google"    # Движок распознавания по умолчанию (как в Manager.listen_text)
    DEFAULT_TTS = "gtts"      # Движок синтеза по умолчанию (как в Manager.say)

    CACHE_DIR = Path.home() / ".cache" / "help_manager" / "voice"   # Сюда скачиваются модели Silero

    SILERO_URL = "https://models.silero.ai/models/tts/ru/{model}.pt"
    SILERO_SPEAKERS = {
        "v5_6_ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
        "v5_5_ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
        "v5_4_ru": ["aidar", "baya", "kseniya", "xenia"],
        "v5_3_ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
        "v5_2_ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
        "v5_ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
        "v4_ru": ["aidar", "baya", "kseniya", "xenia", "eugene", "random"],
    }
    SILERO_RATES = ("x-slow", "slow", "medium", "fast", "x-fast")     # Допустимые rate в SSML <prosody>
    SILERO_PITCHES = ("x-low", "low", "medium", "high", "x-high")     # Допустимые pitch в SSML <prosody>

    GIGAAM_MODELS = (
        "v3_ctc", "v3_rnnt", "v3_e2e_ctc", "v3_e2e_rnnt",
        "v2_ctc", "v2_rnnt", "v1_ctc", "v1_rnnt",
        "multilingual_ctc", "multilingual_large_ctc",
    )   # v3_e2e_* сами ставят пунктуацию и нормализуют текст
    EDGE_RU_VOICES = ("ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural")

    _cache: Dict[Any, Any] = {}   # Кэш загруженных моделей (чтобы не грузить их на каждый вызов)

    # -------------------------------------------------------------------------
    # 🔧 ВНУТРЕННИЕ МЕТОДЫ
    # -------------------------------------------------------------------------

    @staticmethod
    def _import(module: str, pip_name: Optional[str] = None):
        """Импортирует библиотеку или подсказывает, что поставить (внутренний метод)."""
        import importlib
        try:
            return importlib.import_module(module)
        except ImportError as e:
            raise ImportError(
                f"❌ Не установлена библиотека '{module}'. Установи: pip install {pip_name or module}"
            ) from e

    @staticmethod
    def _ffmpeg() -> Optional[str]:
        """Путь к ffmpeg или None (внутренний метод)."""
        return shutil.which("ffmpeg")

    @staticmethod
    def _tmp(suffix: str = ".wav") -> str:
        """Создаёт пустой временный файл и возвращает путь (внутренний метод)."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="voice_")
        os.close(fd)
        return path

    @staticmethod
    def _remove(path: Optional[str]) -> None:
        """Безопасно удаляет файл (внутренний метод)."""
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass

    @staticmethod
    def _check_output(play: bool, save_path: Optional[str]) -> None:
        """Проверяет, что у синтеза есть хоть какой-то результат (внутренний метод)."""
        if not play and not save_path:
            raise ValueError("❌ Нечего делать: play=False и не указан save_path")

    @staticmethod
    def _read_audio(path: str):
        """Читает аудиофайл (wav, mp3, flac, ogg...) → (numpy float32, частота) (внутренний метод)."""
        np = Voice._import("numpy")
        try:
            sf = Voice._import("soundfile")
            data, sample_rate = sf.read(path, dtype="float32", always_2d=False)
            return data, int(sample_rate)
        except Exception:
            # Запасной путь: pydub + ffmpeg (экзотические форматы)
            from pydub import AudioSegment
            seg = AudioSegment.from_file(path)
            arr = np.array(seg.get_array_of_samples(), dtype=np.float32)
            arr /= float(1 << (8 * seg.sample_width - 1))
            if seg.channels > 1:
                arr = arr.reshape(-1, seg.channels)
            return arr, int(seg.frame_rate)

    @staticmethod
    def _write_audio(path: str, data, sample_rate: int) -> None:
        """Пишет numpy-массив в файл (формат по расширению) (внутренний метод)."""
        np = Voice._import("numpy")
        sf = Voice._import("soundfile")
        data = np.clip(np.asarray(data, dtype=np.float32), -1.0, 1.0)
        if path.lower().endswith(".wav"):
            sf.write(path, data, int(sample_rate), subtype="PCM_16")
        else:
            sf.write(path, data, int(sample_rate))

    @staticmethod
    def _resample(data, rate_from: int, rate_to: int):
        """Простая передискретизация (линейная, с усреднением при понижении) (внутренний метод)."""
        np = Voice._import("numpy")
        if rate_from == rate_to or len(data) == 0:
            return data
        ratio = rate_from / float(rate_to)
        width = int(round(ratio))
        if width > 1:
            kernel = np.ones(width, dtype=np.float32) / width

            def smooth(ch):
                return np.convolve(ch, kernel, mode="same")
        else:
            def smooth(ch):
                return ch
        n_out = max(1, int(round(len(data) / ratio)))
        positions = np.arange(n_out) * ratio
        grid = np.arange(len(data))
        if data.ndim == 1:
            return np.interp(positions, grid, smooth(data)).astype(np.float32)
        cols = [np.interp(positions, grid, smooth(data[:, c])) for c in range(data.shape[1])]
        return np.stack(cols, axis=1).astype(np.float32)

    @staticmethod
    def _time_stretch(data, sample_rate: int, tempo: float):
        """Меняет темп без смены высоты тона через ffmpeg atempo (внутренний метод)."""
        ffmpeg = Voice._ffmpeg()
        if not ffmpeg:
            print("⚠️ ffmpeg не найден: темп меняется вместе с высотой тона")
            return Voice._resample(data, sample_rate, int(round(sample_rate / tempo)))

        factors = []
        rest = tempo
        while rest > 2.0:
            factors.append(2.0)
            rest /= 2.0
        while rest < 0.5:
            factors.append(0.5)
            rest /= 0.5
        factors.append(rest)
        chain = ",".join(f"atempo={f:.5f}" for f in factors)

        src, dst = Voice._tmp(".wav"), Voice._tmp(".wav")
        try:
            Voice._write_audio(src, data, sample_rate)
            result = subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-i", src, "-filter:a", chain, dst],
                capture_output=True,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.decode("utf-8", "replace").strip() or "ffmpeg завершился с ошибкой")
            stretched, _ = Voice._read_audio(dst)
            return stretched
        finally:
            Voice._remove(src)
            Voice._remove(dst)

    @staticmethod
    def _apply_effects(path: str, speed: float = 1.0, pitch_shift: float = 0.0, gain: float = 1.0) -> str:
        """
        Применяет темп, тембр и громкость к аудиофайлу (внутренний метод).

        Возвращает путь к новому временному WAV или исходный путь, если эффекты не нужны.
        """
        if speed == 1.0 and pitch_shift == 0.0 and gain == 1.0:
            return path
        if speed <= 0:
            raise ValueError("❌ speed должен быть больше 0 (1.0 — обычный темп)")
        if gain < 0:
            raise ValueError("❌ gain не может быть отрицательным (1.0 — обычная громкость)")

        np = Voice._import("numpy")
        data, sample_rate = Voice._read_audio(path)

        factor = 2.0 ** (pitch_shift / 12.0)          # Во сколько раз меняется частота голоса
        if factor != 1.0:
            data = Voice._resample(data, sample_rate, int(round(sample_rate / factor)))
        tempo = speed / factor                         # Компенсируем длительность, изменённую тембром
        if abs(tempo - 1.0) > 1e-3:
            data = Voice._time_stretch(data, sample_rate, tempo)
        data = np.asarray(data, dtype=np.float32) * float(gain)

        out = Voice._tmp(".wav")
        Voice._write_audio(out, data, sample_rate)
        return out

    @staticmethod
    def _save_as(src: str, dst: str) -> None:
        """Сохраняет аудио в нужном формате по расширению dst (внутренний метод)."""
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        if os.path.splitext(src)[1].lower() == os.path.splitext(dst)[1].lower():
            shutil.copyfile(src, dst)
            return
        data, sample_rate = Voice._read_audio(src)
        try:
            Voice._write_audio(dst, data, sample_rate)
        except Exception:
            from pydub import AudioSegment
            fmt = os.path.splitext(dst)[1].lstrip(".").lower() or "wav"
            AudioSegment.from_file(src).export(dst, format=fmt)

    @staticmethod
    def _finalize(src: str, *, save_path: Optional[str], play: bool, speed: float,
                  pitch_shift: float, gain: float, block: bool) -> Optional[str]:
        """Эффекты → сохранение → воспроизведение → уборка временных файлов (внутренний метод)."""
        produced = [src]
        try:
            path = Voice._apply_effects(src, speed, pitch_shift, gain)
            if path != src:
                produced.append(path)
            if save_path:
                Voice._save_as(path, save_path)
            if play:
                Voice.play(path, block=block)
            return save_path
        finally:
            for item in produced:
                Voice._remove(item)

    @staticmethod
    def _edge_value(value: Union[str, int, float], unit: str, name: str) -> str:
        """Превращает число в строку формата edge-tts: 15 → '+15%' (внутренний метод)."""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float)):
            return f"{int(round(value)):+d}{unit}"
        raise TypeError(f"❌ {name}: ожидается число или строка вида '+10{unit}'")

    @staticmethod
    def _split_text(text: str, max_chars: int) -> List[str]:
        """Режет длинный текст на куски по предложениям (внутренний метод)."""
        import re
        text = text.strip()
        if len(text) <= max_chars:
            return [text]
        chunks, current = [], ""
        for sentence in re.split(r"(?<=[.!?…])\s+", text):
            while len(sentence) > max_chars:
                cut = sentence.rfind(" ", 0, max_chars)
                if cut <= 0:
                    cut = max_chars
                head, sentence = sentence[:cut], sentence[cut:].lstrip()
                if current:
                    chunks.append(current)
                    current = ""
                chunks.append(head)
            if not sentence:
                continue
            if current and len(current) + 1 + len(sentence) > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _split_audio(mono, sample_rate: int, max_seconds: float) -> List[Tuple[int, int]]:
        """Режет длинную запись на куски по самым тихим местам (внутренний метод)."""
        np = Voice._import("numpy")
        total = len(mono)
        max_len = int(max_seconds * sample_rate)
        if total <= max_len:
            return [(0, total)]
        frame = max(1, int(0.02 * sample_rate))
        window = int(2.0 * sample_rate)
        ranges, start = [], 0
        while total - start > max_len:
            hi = start + max_len
            lo = max(hi - window, start + frame)
            part = mono[lo:hi]
            frames = len(part) // frame
            if frames > 0:
                energy = (part[:frames * frame].reshape(frames, frame) ** 2).mean(axis=1)
                cut = lo + int(np.argmin(energy)) * frame + frame // 2
            else:
                cut = hi
            ranges.append((start, cut))
            start = cut
        ranges.append((start, total))
        return ranges

    @staticmethod
    def _to_mono_16k(path: str) -> str:
        """Конвертирует любой аудиофайл в временный WAV 16 кГц моно (удалять после использования)."""
        out = Voice._tmp(".wav")
        ffmpeg = Voice._ffmpeg()
        if ffmpeg:
            result = subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "wav", out],
                capture_output=True,
            )
            if result.returncode == 0 and os.path.getsize(out) > 44:
                return out
        data, sample_rate = Voice._read_audio(path)
        mono = data if data.ndim == 1 else data.mean(axis=1)
        Voice._write_audio(out, Voice._resample(mono, sample_rate, 16000), 16000)
        return out

    @staticmethod
    def _google_lang(language: str) -> str:
        """'ru' → 'ru-RU' для Google Speech Recognition (внутренний метод)."""
        short = {"ru": "ru-RU", "en": "en-US", "uk": "uk-UA", "de": "de-DE", "fr": "fr-FR",
                 "es": "es-ES", "it": "it-IT", "kk": "kk-KZ", "tr": "tr-TR", "pl": "pl-PL",
                 "zh": "zh-CN", "ja": "ja-JP"}
        return short.get(language.lower(), language)

    # ---------- Загрузка и кэш моделей ----------

    @staticmethod
    def _get_silero(model: str, device: str, num_threads: Optional[int]):
        """Загружает модель Silero TTS (скачивает при первом запуске) (внутренний метод)."""
        key = ("silero", model, str(device))
        if key in Voice._cache:
            return Voice._cache[key]
        torch = Voice._import("torch")
        package = Voice._import("torch.package", "torch")
        if num_threads:
            torch.set_num_threads(int(num_threads))

        if os.path.isfile(model):
            model_path = model
        else:
            Voice.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            model_path = str(Voice.CACHE_DIR / f"silero_{model}.pt")
            if not os.path.isfile(model_path):
                print(f"⏳ Скачиваю модель Silero '{model}' (один раз)...")
                part = model_path + ".part"
                torch.hub.download_url_to_file(Voice.SILERO_URL.format(model=model), part)
                os.replace(part, model_path)

        tts = package.PackageImporter(model_path).load_pickle("tts_models", "model")
        tts.to(torch.device(device))
        Voice._cache[key] = tts
        return tts

    @staticmethod
    def _get_gigaam(model: str, device: Optional[str], fp16_encoder: bool,
                    use_flash: bool, download_root: Optional[str]):
        """Загружает модель GigaAM (скачивает при первом запуске) (внутренний метод)."""
        key = ("gigaam", model, str(device))
        if key not in Voice._cache:
            gigaam = Voice._import(
                "gigaam",
                "https://github.com/salute-developers/GigaAM/archive/refs/heads/main.zip --no-deps",
            )
            print(f"⏳ Загружаю GigaAM '{model}' (первый раз скачивает веса)...")
            Voice._cache[key] = gigaam.load_model(
                model, fp16_encoder=fp16_encoder, use_flash=use_flash,
                device=device, download_root=download_root,
            )
        return Voice._cache[key]

    @staticmethod
    def _get_vosk(model: Optional[str], language: str):
        """Загружает модель Vosk: папку, имя для скачивания или модель по языку (внутренний метод)."""
        key = ("vosk", model or language)
        if key not in Voice._cache:
            vosk = Voice._import("vosk")
            vosk.SetLogLevel(-1)
            if model and os.path.isdir(model):
                Voice._cache[key] = vosk.Model(model_path=model)
            elif model:
                Voice._cache[key] = vosk.Model(model_name=model)
            else:
                Voice._cache[key] = vosk.Model(lang=language)
        return Voice._cache[key]

    @staticmethod
    def _get_whisper(model: str, device: str, compute_type: str, cpu_threads: int,
                     download_root: Optional[str]):
        """Загружает модель faster-whisper (внутренний метод)."""
        key = ("whisper", model, device, compute_type)
        if key not in Voice._cache:
            faster_whisper = Voice._import("faster_whisper", "faster-whisper")
            print(f"⏳ Загружаю Whisper '{model}' (первый раз скачивает веса)...")
            Voice._cache[key] = faster_whisper.WhisperModel(
                model, device=device, compute_type=compute_type,
                cpu_threads=cpu_threads, download_root=download_root,
            )
        return Voice._cache[key]

    @staticmethod
    def _get_pyttsx3(driver: Optional[str]):
        """Создаёт (один раз) движок pyttsx3 (внутренний метод)."""
        key = ("pyttsx3", driver)
        if key not in Voice._cache:
            pyttsx3 = Voice._import("pyttsx3")
            Voice._cache[key] = pyttsx3.init(driver)
        return Voice._cache[key]

    @staticmethod
    def _pick_pyttsx3_voice(engine, voice: str) -> str:
        """Ищет голос pyttsx3 по точному id или куску имени (внутренний метод)."""
        voices = engine.getProperty("voices")
        needle = str(voice).lower()
        for item in voices:
            if needle == str(item.id).lower():
                return item.id
        for item in voices:
            haystack = f"{item.name} {item.id} {getattr(item, 'languages', '')}".lower()
            if needle in haystack:
                return item.id
        names = ", ".join(str(v.name) for v in voices)
        raise ValueError(f"❌ Голос pyttsx3 '{voice}' не найден. Доступные: {names}")

    # -------------------------------------------------------------------------
    # 🧰 СЛУЖЕБНЫЕ: ПРОВЕРКА, НАСТРОЙКА, СПИСКИ ГОЛОСОВ
    # -------------------------------------------------------------------------

    @staticmethod
    def engines() -> Dict[str, Dict[str, bool]]:
        """
        🔍 КАКИЕ ДВИЖКИ И ИНСТРУМЕНТЫ УСТАНОВЛЕНЫ

        Возвращает:
            dict: {"stt": {...}, "tts": {...}, "tools": {...}} со значениями True/False

        Пример:
            >>> Voice.engines()["stt"]["vosk"]
            True

        Примечание:
            Проверяет только наличие библиотек, модели при этом не загружаются.
        """
        import importlib.util

        def has(*modules: str) -> bool:
            try:
                return all(importlib.util.find_spec(m) is not None for m in modules)
            except (ImportError, ValueError):
                return False

        return {
            "stt": {
                "google": has("speech_recognition"),
                "vosk": has("vosk"),
                "gigaam": has("gigaam", "torch"),
                "whisper": has("faster_whisper"),
            },
            "tts": {
                "gtts": has("gtts"),
                "silero": has("torch"),
                "edge": has("edge_tts"),
                "pyttsx3": has("pyttsx3"),
            },
            "tools": {
                "numpy": has("numpy"),
                "soundfile": has("soundfile"),
                "sounddevice": has("sounddevice"),
                "pydub": has("pydub"),
                "ffmpeg": Voice._ffmpeg() is not None,
            },
        }

    @staticmethod
    def check() -> None:
        """
        ✅ ВЫВЕСТИ В КОНСОЛЬ, ЧТО УСТАНОВЛЕНО И ЧЕГО НЕ ХВАТАЕТ

        Пример:
            >>> Voice.check()
        """
        titles = {"stt": "🎤 РАСПОЗНАВАНИЕ", "tts": "🔊 СИНТЕЗ", "tools": "🧰 ИНСТРУМЕНТЫ"}
        hints = {
            "google": "pip install SpeechRecognition pyaudio", "vosk": "pip install vosk",
            "gigaam": "pip install torch + GigaAM с GitHub", "whisper": "pip install faster-whisper",
            "gtts": "pip install gTTS", "silero": "pip install torch", "edge": "pip install edge-tts",
            "pyttsx3": "pip install pyttsx3", "numpy": "pip install numpy",
            "soundfile": "pip install soundfile", "sounddevice": "pip install sounddevice",
            "pydub": "pip install pydub", "ffmpeg": "установи ffmpeg и добавь в PATH",
        }
        for group, items in Voice.engines().items():
            print(f"\n{titles[group]}")
            for name, ok in items.items():
                print(f"  ✅ {name}" if ok else f"  ❌ {name} — {hints[name]}")

    @staticmethod
    def use(tts: Optional[str] = None, stt: Optional[str] = None) -> None:
        """
        🎛️ ВЫБРАТЬ ДВИЖКИ ПО УМОЛЧАНИЮ ДЛЯ say() И listen()

        Параметры:
            tts (str, optional): 'gtts', 'silero', 'edge' или 'pyttsx3'
            stt (str, optional): 'google', 'vosk', 'gigaam' или 'whisper'

        Исключения:
            ValueError: Если указан неизвестный движок.

        Пример:
            >>> Voice.use(tts="silero", stt="gigaam")
            >>> Voice.say("Теперь я говорю голосом Silero")
            >>> text = Voice.listen()
        """
        if tts is not None:
            if tts.lower() not in Voice.TTS_ENGINES:
                raise ValueError(f"❌ Неизвестный движок синтеза '{tts}'. Доступны: {', '.join(Voice.TTS_ENGINES)}")
            Voice.DEFAULT_TTS = tts.lower()
        if stt is not None:
            if stt.lower() not in Voice.STT_ENGINES:
                raise ValueError(f"❌ Неизвестный движок распознавания '{stt}'. Доступны: {', '.join(Voice.STT_ENGINES)}")
            Voice.DEFAULT_STT = stt.lower()

    @staticmethod
    def unload(engine: Optional[str] = None) -> None:
        """
        🧹 ВЫГРУЗИТЬ МОДЕЛИ ИЗ ПАМЯТИ

        Параметры:
            engine (str, optional): Какой движок выгрузить ('silero', 'gigaam', 'vosk', 'whisper', 'pyttsx3').
                                    Если не указан — выгружаются все.

        Пример:
            >>> Voice.unload("gigaam")
        """
        for key in list(Voice._cache.keys()):
            if engine is None or key[0] == engine:
                del Voice._cache[key]

    @staticmethod
    def list_voices(engine: Optional[str] = None, **options) -> List[str]:
        """
        📋 СПИСОК ДОСТУПНЫХ ГОЛОСОВ ДВИЖКА

        Параметры:
            engine (str, optional): 'gtts' (коды языков), 'silero', 'edge', 'pyttsx3'.
                                    По умолчанию — Voice.DEFAULT_TTS.
            **options: model='v5_6_ru' (для silero), locale='ru' (для edge), driver=None (для pyttsx3)

        Возвращает:
            List[str]: Имена голосов (значения для параметра voice)

        Пример:
            >>> Voice.list_voices("silero")
            ['aidar', 'baya', 'kseniya', 'xenia', 'eugene']
            >>> Voice.list_voices("edge", locale="ru")
            ['ru-RU-DmitryNeural', 'ru-RU-SvetlanaNeural']

        Примечание:
            Для 'edge' нужен интернет. Для 'silero' известные модели читаются без скачивания.
        """
        engine = (engine or Voice.DEFAULT_TTS).lower()
        if engine == "gtts":
            gtts_lang = Voice._import("gtts.lang", "gTTS")
            return sorted(gtts_lang.tts_langs().keys())
        if engine == "silero":
            model = options.get("model", "v5_6_ru")
            if model in Voice.SILERO_SPEAKERS:
                return list(Voice.SILERO_SPEAKERS[model])
            tts = Voice._get_silero(model, options.get("device", "cpu"), options.get("num_threads"))
            return sorted(tts.speakers)
        if engine == "edge":
            import asyncio
            edge_tts = Voice._import("edge_tts", "edge-tts")
            locale = str(options.get("locale", "ru")).lower()
            voices = asyncio.run(edge_tts.list_voices())
            return sorted(v["ShortName"] for v in voices if str(v.get("Locale", "")).lower().startswith(locale))
        if engine == "pyttsx3":
            tts = Voice._get_pyttsx3(options.get("driver"))
            return [str(v.name) for v in tts.getProperty("voices")]
        raise ValueError(f"❌ Неизвестный движок синтеза '{engine}'. Доступны: {', '.join(Voice.TTS_ENGINES)}")

    # -------------------------------------------------------------------------
    # 🔊 ВОСПРОИЗВЕДЕНИЕ
    # -------------------------------------------------------------------------

    @staticmethod
    def play(path: str, block: bool = True, device: Optional[int] = None) -> None:
        """
        ▶️ ВОСПРОИЗВЕДЕНИЕ АУДИОФАЙЛА (WAV, MP3, FLAC, OGG)

        Параметры:
            path (str): Путь к аудиофайлу
            block (bool): True — ждать конца звука, False — играть в фоне и сразу вернуться
            device (int, optional): Номер устройства вывода (см. sounddevice.query_devices())

        Исключения:
            FileNotFoundError: Если файла нет.

        Пример:
            >>> Voice.play("tts_out.wav")
            >>> Voice.play("music.mp3", block=False)
            >>> Voice.stop()

        Примечание:
            Если sounddevice не установлен, используется pydub (воспроизведение всегда блокирующее).
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Файл не найден: {path}")
        try:
            sd = Voice._import("sounddevice")
        except ImportError:
            sd = None
        if sd is not None:
            data, sample_rate = Voice._read_audio(path)
            sd.play(data, sample_rate, device=device)
            if block:
                sd.wait()
            return
        from pydub import AudioSegment
        from pydub.playback import play as pydub_play
        pydub_play(AudioSegment.from_file(path))

    @staticmethod
    def stop() -> None:
        """
        ⏹️ ОСТАНОВИТЬ ВОСПРОИЗВЕДЕНИЕ (для block=False)

        Пример:
            >>> Voice.say("Очень длинная речь...", block=False)
            >>> Voice.stop()
        """
        try:
            Voice._import("sounddevice").stop()
        except ImportError:
            pass

    # -------------------------------------------------------------------------
    # 🗣️ СИНТЕЗ РЕЧИ (TTS)
    # -------------------------------------------------------------------------

    @staticmethod
    def say(text: str, engine: Optional[str] = None, **options) -> Optional[str]:
        """
        🔊 ОЗВУЧКА ТЕКСТА ВЫБРАННЫМ ДВИЖКОМ (TTS)

        Параметры:
            text (str): Текст для озвучивания
            engine (str, optional): 'gtts', 'silero', 'edge' или 'pyttsx3'.
                                    По умолчанию — Voice.DEFAULT_TTS ('gtts', как в Manager.say).
            **options: Любые параметры выбранного say_*() (voice, speed, pitch_shift, save_path и т.д.)

        Возвращает:
            str или None: Путь сохранённого файла, если указан save_path

        Пример:
            >>> Voice.say("Привет, мир!")
            >>> Voice.say("Привет!", engine="silero", voice="xenia", speed=1.1)
            >>> Voice.say("Сохраню в файл", engine="edge", save_path="hello.mp3", play=False)

        Примечание:
            Параметры смотри в say_gtts(), say_silero(), say_edge(), say_pyttsx3().
        """
        engine = (engine or Voice.DEFAULT_TTS).lower()
        funcs = {
            "gtts": Voice.say_gtts,
            "silero": Voice.say_silero,
            "edge": Voice.say_edge,
            "pyttsx3": Voice.say_pyttsx3,
        }
        if engine not in funcs:
            raise ValueError(f"❌ Неизвестный движок синтеза '{engine}'. Доступны: {', '.join(Voice.TTS_ENGINES)}")
        return funcs[engine](text, **options)

    @staticmethod
    def say_gtts(text: str, lang: str = "ru", slow: bool = False, tld: str = "com",
                 lang_check: bool = True, timeout: Optional[float] = None, *,
                 play: bool = True, save_path: Optional[str] = None, speed: float = 1.0,
                 pitch_shift: float = 0.0, gain: float = 1.0, block: bool = True) -> Optional[str]:
        """
        🌐 СИНТЕЗ РЕЧИ ЧЕРЕЗ GOOGLE TTS (gTTS, ОНЛАЙН)

        Параметры:
            text (str): Текст для озвучивания
            lang (str): Язык ('ru', 'en', 'de'...). Список: Voice.list_voices("gtts")
            slow (bool): Медленное произношение
            tld (str): Домен Google ('com', 'co.uk', 'com.au'...) — меняет акцент
            lang_check (bool): Проверять, что язык поддерживается
            timeout (float, optional): Таймаут запроса в секундах
            play (bool): Проиграть звук
            save_path (str, optional): Сохранить в файл (.mp3 или .wav)
            speed (float): Темп поверх звука (1.0 — обычный, 1.2 — быстрее)
            pitch_shift (float): Тембр в полутонах (-3 — ниже, +3 — выше)
            gain (float): Громкость (1.0 — обычная, 0.5 — тише)
            block (bool): Ждать окончания звука (False — играть в фоне)

        Возвращает:
            str или None: Путь сохранённого файла, если указан save_path

        Пример:
            >>> Voice.say_gtts("Привет!")
            >>> Voice.say_gtts("Hello!", lang="en", tld="co.uk")
            >>> Voice.say_gtts("Низкий голос", pitch_shift=-4, save_path="low.mp3")

        Примечание:
            Требуется интернет. У gTTS один голос на язык, поэтому тембр и темп делаются эффектами.
        """
        Voice._check_output(play, save_path)
        gtts = Voice._import("gtts", "gTTS")
        tmp = Voice._tmp(".mp3")
        try:
            gtts.gTTS(text=text, lang=lang, slow=slow, tld=tld,
                      lang_check=lang_check, timeout=timeout).save(tmp)
        except Exception:
            Voice._remove(tmp)
            raise
        return Voice._finalize(tmp, save_path=save_path, play=play, speed=speed,
                               pitch_shift=pitch_shift, gain=gain, block=block)

    @staticmethod
    def say_silero(text: str, voice: str = "xenia", model: str = "v5_6_ru", sample_rate: int = 48000,
                   put_accent: bool = True, put_yo: bool = True, put_stress_homo: bool = True,
                   put_yo_homo: bool = True, ssml: bool = False, prosody_rate: Optional[str] = None,
                   prosody_pitch: Optional[str] = None, device: str = "cpu",
                   num_threads: Optional[int] = None, max_chars: int = 800, *,
                   play: bool = True, save_path: Optional[str] = None, speed: float = 1.0,
                   pitch_shift: float = 0.0, gain: float = 1.0, block: bool = True) -> Optional[str]:
        """
        🧠 СИНТЕЗ РЕЧИ НЕЙРОСЕТЬЮ SILERO (ОФЛАЙН, ЛУЧШИЙ ДЛЯ РУССКОГО)

        Параметры:
            text (str): Текст для озвучивания (или SSML, если ssml=True)
            voice (str): Голос: 'aidar', 'baya', 'kseniya', 'xenia', 'eugene' (зависит от модели)
            model (str): Версия модели ('v5_6_ru', 'v5_5_ru', 'v4_ru'...) или путь к .pt файлу
            sample_rate (int): Частота звука: 8000, 24000 или 48000
            put_accent (bool): Автоматически ставить ударения
            put_yo (bool): Автоматически ставить «ё»
            put_stress_homo (bool): Ударения в омографах (зАмок / замОк) по контексту
            put_yo_homo (bool): «ё» в омографах по контексту
            ssml (bool): True — text это готовый SSML (<speak>...</speak>)
            prosody_rate (str, optional): Темп силами модели: 'x-slow', 'slow', 'medium', 'fast', 'x-fast'
            prosody_pitch (str, optional): Тембр силами модели: 'x-low', 'low', 'medium', 'high', 'x-high'
            device (str): 'cpu' или 'cuda'
            num_threads (int, optional): Сколько потоков CPU использовать
            max_chars (int): Длинный текст режется на куски такого размера (по предложениям)
            play (bool): Проиграть звук
            save_path (str, optional): Сохранить в файл (.wav или .mp3)
            speed (float): Темп поверх звука (1.0 — обычный)
            pitch_shift (float): Тембр в полутонах поверх звука
            gain (float): Громкость (1.0 — обычная)
            block (bool): Ждать окончания звука (False — играть в фоне)

        Возвращает:
            str или None: Путь сохранённого файла, если указан save_path

        Исключения:
            ValueError: Если голос, частота или значения prosody недопустимы.

        Пример:
            >>> Voice.say_silero("Привет! Меня зовут Кеша.")
            >>> Voice.say_silero("Я бас", voice="aidar", prosody_pitch="x-low")
            >>> Voice.say_silero("Замок на двери", put_stress_homo=True, save_path="out.wav")
            >>> Voice.say_silero('<speak>Раз<break time="1s"/>два</speak>', ssml=True)

        Примечание:
            Первый запуск скачивает модель (~100 МБ) в ~/.cache/help_manager/voice.
            Можно вручную ставить ударения знаком «+» перед гласной: «з+амок».
            В режиме SSML флаги put_* не передаются. Нужен torch.
        """
        Voice._check_output(play, save_path)
        np = Voice._import("numpy")
        if sample_rate not in (8000, 24000, 48000):
            raise ValueError("❌ sample_rate для Silero: 8000, 24000 или 48000")
        if prosody_rate is not None and prosody_rate not in Voice.SILERO_RATES:
            raise ValueError(f"❌ prosody_rate: одно из {', '.join(Voice.SILERO_RATES)}")
        if prosody_pitch is not None and prosody_pitch not in Voice.SILERO_PITCHES:
            raise ValueError(f"❌ prosody_pitch: одно из {', '.join(Voice.SILERO_PITCHES)}")

        tts = Voice._get_silero(model, device, num_threads)
        speakers = getattr(tts, "speakers", None)
        if speakers and voice not in speakers:
            raise ValueError(f"❌ Голос '{voice}' не найден в модели {model}. Доступные: {', '.join(sorted(speakers))}")

        base = {"speaker": voice, "sample_rate": sample_rate}
        chunks = [text] if ssml else Voice._split_text(text, max_chars)
        parts = []
        for chunk in chunks:
            if ssml:
                kwargs = dict(base, ssml_text=chunk)
            elif prosody_rate or prosody_pitch:
                from xml.sax.saxutils import escape
                attrs = ""
                if prosody_rate:
                    attrs += f' rate="{prosody_rate}"'
                if prosody_pitch:
                    attrs += f' pitch="{prosody_pitch}"'
                kwargs = dict(base, ssml_text=f"<speak><prosody{attrs}>{escape(chunk)}</prosody></speak>")
            else:
                kwargs = dict(base, text=chunk, put_accent=put_accent, put_yo=put_yo,
                              put_stress_homo=put_stress_homo, put_yo_homo=put_yo_homo)
            audio = tts.apply_tts(**kwargs)
            parts.append(np.asarray(audio.numpy() if hasattr(audio, "numpy") else audio, dtype=np.float32))
            if len(chunks) > 1:
                parts.append(np.zeros(int(sample_rate * 0.1), dtype=np.float32))   # Короткая пауза между кусками

        tmp = Voice._tmp(".wav")
        try:
            Voice._write_audio(tmp, np.concatenate(parts), sample_rate)
        except Exception:
            Voice._remove(tmp)
            raise
        return Voice._finalize(tmp, save_path=save_path, play=play, speed=speed,
                               pitch_shift=pitch_shift, gain=gain, block=block)

    @staticmethod
    def say_edge(text: str, voice: str = "ru-RU-SvetlanaNeural", rate: Union[str, int] = "+0%",
                 pitch: Union[str, int] = "+0Hz", volume: Union[str, int] = "+0%",
                 proxy: Optional[str] = None, connect_timeout: int = 10, receive_timeout: int = 60, *,
                 play: bool = True, save_path: Optional[str] = None, speed: float = 1.0,
                 pitch_shift: float = 0.0, gain: float = 1.0, block: bool = True) -> Optional[str]:
        """
        🪟 СИНТЕЗ РЕЧИ НЕЙРОГОЛОСАМИ MICROSOFT EDGE (edge-tts, ОНЛАЙН)

        Параметры:
            text (str): Текст для озвучивания
            voice (str): Голос: 'ru-RU-SvetlanaNeural' (жен.), 'ru-RU-DmitryNeural' (муж.) и другие
            rate (str или int): Темп движка: 15 → '+15%', -20 → '-20%' или строка '+15%'
            pitch (str или int): Тембр движка в герцах: -10 → '-10Hz' или строка '+5Hz'
            volume (str или int): Громкость движка: 10 → '+10%', -30 → '-30%'
            proxy (str, optional): Адрес прокси, если нужен
            connect_timeout (int): Таймаут подключения, секунд
            receive_timeout (int): Таймаут получения данных, секунд
            play (bool): Проиграть звук
            save_path (str, optional): Сохранить в файл (.mp3 или .wav)
            speed (float): Дополнительный темп поверх звука (1.0 — обычный)
            pitch_shift (float): Дополнительный тембр в полутонах поверх звука
            gain (float): Дополнительная громкость (1.0 — обычная)
            block (bool): Ждать окончания звука (False — играть в фоне)

        Возвращает:
            str или None: Путь сохранённого файла, если указан save_path

        Пример:
            >>> Voice.say_edge("Привет!")
            >>> Voice.say_edge("Бодрее и ниже", voice="ru-RU-DmitryNeural", rate=20, pitch=-15)
            >>> print(Voice.list_voices("edge", locale="ru"))

        Примечание:
            Требуется интернет. Значения rate, pitch и volume у edge-tts обязательно со знаком (+/-).
        """
        Voice._check_output(play, save_path)
        edge_tts = Voice._import("edge_tts", "edge-tts")

        wanted = {
            "rate": Voice._edge_value(rate, "%", "rate"),
            "pitch": Voice._edge_value(pitch, "Hz", "pitch"),
            "volume": Voice._edge_value(volume, "%", "volume"),
            "proxy": proxy,
            "connect_timeout": connect_timeout,
            "receive_timeout": receive_timeout,
        }
        supported = inspect.signature(edge_tts.Communicate.__init__).parameters   # Старые версии без некоторых параметров
        kwargs = {k: v for k, v in wanted.items() if k in supported}

        tmp = Voice._tmp(".mp3")
        try:
            communicate = edge_tts.Communicate(text, voice, **kwargs)
            if hasattr(communicate, "save_sync"):
                communicate.save_sync(tmp)
            else:
                import asyncio
                asyncio.run(communicate.save(tmp))
            if os.path.getsize(tmp) == 0:
                raise RuntimeError("edge-tts вернул пустой файл (проверь интернет и имя голоса)")
        except Exception:
            Voice._remove(tmp)
            raise
        return Voice._finalize(tmp, save_path=save_path, play=play, speed=speed,
                               pitch_shift=pitch_shift, gain=gain, block=block)

    @staticmethod
    def say_pyttsx3(text: str, voice: Optional[str] = None, rate: Optional[int] = None,
                    volume: Optional[float] = None, driver: Optional[str] = None, *,
                    play: bool = True, save_path: Optional[str] = None, speed: float = 1.0,
                    pitch_shift: float = 0.0, gain: float = 1.0, block: bool = True) -> Optional[str]:
        """
        💻 СИНТЕЗ РЕЧИ ГОЛОСАМИ СИСТЕМЫ (pyttsx3, ОФЛАЙН)

        Параметры:
            text (str): Текст для озвучивания
            voice (str, optional): Id голоса или кусок его имени ('Irina', 'Pavel', 'russian')
            rate (int, optional): Темп движка в словах в минуту (обычно ~200)
            volume (float, optional): Громкость движка от 0.0 до 1.0
            driver (str, optional): Драйвер: 'sapi5' (Windows), 'nsss' (macOS), 'espeak' (Linux)
            play (bool): Проиграть звук
            save_path (str, optional): Сохранить в файл (.wav)
            speed (float): Темп поверх звука (1.0 — обычный)
            pitch_shift (float): Тембр в полутонах поверх звука (у самого pyttsx3 тембра нет)
            gain (float): Громкость поверх звука (1.0 — обычная)
            block (bool): Ждать окончания звука (при прямом проигрывании pyttsx3 всегда ждёт)

        Возвращает:
            str или None: Путь сохранённого файла, если указан save_path

        Пример:
            >>> Voice.say_pyttsx3("Привет!")
            >>> Voice.say_pyttsx3("Привет!", voice="Irina", rate=170)
            >>> print(Voice.list_voices("pyttsx3"))

        Примечание:
            Какие голоса есть, зависит от системы. Русские голоса Windows ставятся в
            «Параметры → Время и язык → Речь».
        """
        Voice._check_output(play, save_path)
        engine = Voice._get_pyttsx3(driver)
        if voice:
            engine.setProperty("voice", Voice._pick_pyttsx3_voice(engine, voice))
        if rate is not None:
            engine.setProperty("rate", int(rate))
        if volume is not None:
            engine.setProperty("volume", max(0.0, min(1.0, float(volume))))

        direct = play and not save_path and speed == 1.0 and pitch_shift == 0.0 and gain == 1.0
        if direct:
            engine.say(text)
            engine.runAndWait()
            return None

        tmp = Voice._tmp(".wav")
        try:
            engine.save_to_file(text, tmp)
            engine.runAndWait()
            if os.path.getsize(tmp) == 0:
                raise RuntimeError("pyttsx3 не создал аудиофайл")
        except Exception:
            Voice._remove(tmp)
            raise
        return Voice._finalize(tmp, save_path=save_path, play=play, speed=speed,
                               pitch_shift=pitch_shift, gain=gain, block=block)

    # -------------------------------------------------------------------------
    # 🎤 ЗАПИСЬ И РАСПОЗНАВАНИЕ РЕЧИ (STT)
    # -------------------------------------------------------------------------

    @staticmethod
    def record(seconds: float = 5.0, path: Optional[str] = None, sample_rate: int = 16000,
               input_device: Optional[int] = None, stop_on_silence: bool = False,
               silence_threshold: float = 0.01, silence_seconds: float = 1.0) -> str:
        """
        🔴 ЗАПИСЬ С МИКРОФОНА В WAV

        Параметры:
            seconds (float): Максимальная длительность записи
            path (str, optional): Куда сохранить. Если не указан — создаётся временный файл
            sample_rate (int): Частота (16000 подходит для распознавания)
            input_device (int, optional): Номер микрофона (см. sounddevice.query_devices())
            stop_on_silence (bool): Остановиться, когда фраза закончилась и наступила тишина
            silence_threshold (float): Громкость (0..1), ниже которой считается тишиной
            silence_seconds (float): Сколько секунд тишины после речи означают конец фразы

        Возвращает:
            str: Путь к записанному WAV (временный файл удаляй сам, если не указывал path)

        Пример:
            >>> wav = Voice.record(5, "my_voice.wav")
            >>> wav = Voice.record(15, stop_on_silence=True)   # до конца фразы, но не дольше 15 с

        Примечание:
            Если stop_on_silence=True, а речи не было, запись идёт все seconds секунд.
        """
        np = Voice._import("numpy")
        sd = Voice._import("sounddevice")
        step = 0.1
        block_size = max(1, int(sample_rate * step))
        total_blocks = max(1, int(round(seconds / step)))
        frames: List[Any] = []
        heard = False
        silent_for = 0.0

        with sd.InputStream(samplerate=sample_rate, channels=1, dtype="float32",
                            device=input_device, blocksize=block_size) as stream:
            for _ in range(total_blocks):
                data, _overflow = stream.read(block_size)
                frames.append(np.array(data, dtype=np.float32).reshape(-1))
                if stop_on_silence:
                    level = float(np.sqrt(np.mean(frames[-1] ** 2)))
                    if level >= silence_threshold:
                        heard = True
                        silent_for = 0.0
                    elif heard:
                        silent_for += step
                        if silent_for >= silence_seconds:
                            break

        out = path or Voice._tmp(".wav")
        Voice._write_audio(out, np.concatenate(frames), sample_rate)
        return out

    @staticmethod
    def listen(engine: Optional[str] = None, seconds: int = 5, **options) -> str:
        """
        🎤 РАСПОЗНАВАНИЕ РЕЧИ ВЫБРАННЫМ ДВИЖКОМ (STT)

        Параметры:
            engine (str, optional): 'google', 'vosk', 'gigaam' или 'whisper'.
                                    По умолчанию — Voice.DEFAULT_STT ('google', как в Manager.listen_text).
            seconds (int): Сколько секунд слушать
            **options: Любые параметры выбранного listen_*() (language, model, audio_path и т.д.)

        Возвращает:
            str: Распознанный текст или пустая строка, если ничего не услышано

        Пример:
            >>> text = Voice.listen()
            >>> text = Voice.listen("gigaam", seconds=8, model="v3_e2e_ctc")
            >>> text = Voice.listen("vosk", grammar=["включи свет", "выключи свет"])

        Примечание:
            Параметры смотри в listen_google(), listen_vosk(), listen_gigaam(), listen_whisper().
        """
        engine = (engine or Voice.DEFAULT_STT).lower()
        funcs = {
            "google": Voice.listen_google,
            "vosk": Voice.listen_vosk,
            "gigaam": Voice.listen_gigaam,
            "whisper": Voice.listen_whisper,
        }
        if engine not in funcs:
            raise ValueError(f"❌ Неизвестный движок распознавания '{engine}'. Доступны: {', '.join(Voice.STT_ENGINES)}")
        return funcs[engine](seconds=seconds, **options)

    @staticmethod
    def transcribe_file(path: str, engine: Optional[str] = None, **options) -> str:
        """
        📄 РАСПОЗНАВАНИЕ РЕЧИ ИЗ АУДИОФАЙЛА

        Параметры:
            path (str): Путь к аудиофайлу (wav, mp3, ogg, m4a...)
            engine (str, optional): 'google', 'vosk', 'gigaam' или 'whisper'
            **options: Параметры выбранного listen_*() (model, language и т.д.)

        Возвращает:
            str: Распознанный текст

        Исключения:
            FileNotFoundError: Если файла нет.

        Пример:
            >>> text = Voice.transcribe_file("my_voice.wav", engine="gigaam")
            >>> text = Voice.transcribe_file("interview.mp3", engine="whisper", model="small")

        Примечание:
            GigaAM сам режет записи длиннее 25 секунд на куски по паузам.
            Google подходит только для коротких записей (до ~1 минуты).
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Файл не найден: {path}")
        return Voice.listen(engine, audio_path=path, **options)

    @staticmethod
    def transcribe_words(path: str, engine: str = "gigaam", **options) -> List[Dict[str, Any]]:
        """
        ⏱️ РАСПОЗНАВАНИЕ С ТАЙМКОДАМИ КАЖДОГО СЛОВА

        Параметры:
            path (str): Путь к аудиофайлу
            engine (str): 'gigaam', 'vosk' или 'whisper' (у Google таймкодов нет)
            **options: Параметры выбранного listen_*() (model, language и т.д.)

        Возвращает:
            List[dict]: [{"word": "привет", "start": 0.52, "end": 0.91}, ...] (время в секундах)

        Пример:
            >>> for w in Voice.transcribe_words("my_voice.wav"):
            ...     print(f"{w['start']:.2f}–{w['end']:.2f} {w['word']}")
        """
        if engine.lower() not in ("gigaam", "vosk", "whisper"):
            raise ValueError("❌ Таймкоды слов умеют: gigaam, vosk, whisper")
        words: List[Dict[str, Any]] = []
        Voice.transcribe_file(path, engine=engine, words_out=words, **options)
        return words

    @staticmethod
    def listen_google(seconds: int = 5, language: str = "ru", adjust_noise: bool = True,
                      noise_duration: float = 1.0, timeout: Optional[float] = None,
                      phrase_time_limit: Optional[float] = None, energy_threshold: Optional[float] = None,
                      dynamic_energy: bool = True, pause_threshold: float = 0.8,
                      input_device: Optional[int] = None, key: Optional[str] = None,
                      audio_path: Optional[str] = None, raise_errors: bool = False) -> str:
        """
        🌐 РАСПОЗНАВАНИЕ РЕЧИ ЧЕРЕЗ GOOGLE (ОНЛАЙН)

        Параметры:
            seconds (int): Сколько секунд слушать (используется, если timeout/phrase_time_limit не заданы)
            language (str): Язык: 'ru', 'en' или полный код 'ru-RU', 'en-US'
            adjust_noise (bool): Подстроиться под фоновый шум перед записью
            noise_duration (float): Сколько секунд замерять шум
            timeout (float, optional): Сколько ждать начала речи (по умолчанию = seconds)
            phrase_time_limit (float, optional): Максимальная длина фразы (по умолчанию = seconds)
            energy_threshold (float, optional): Порог громкости для начала речи (по умолчанию авто)
            dynamic_energy (bool): Автоматически менять порог громкости
            pause_threshold (float): Сколько секунд тишины считается концом фразы
            input_device (int, optional): Номер микрофона
            key (str, optional): Свой ключ Google Speech API (по умолчанию общий)
            audio_path (str, optional): Распознать файл вместо микрофона
            raise_errors (bool): True — выбрасывать ошибки, False — печатать и вернуть ""

        Возвращает:
            str: Распознанный текст или пустая строка

        Пример:
            >>> text = Voice.listen_google(seconds=6)
            >>> text = Voice.listen_google(language="en", pause_threshold=1.2)

        Примечание:
            Требуется интернет и микрофон (SpeechRecognition + PyAudio).
            Тишина и непонятная речь дают пустую строку, а не ошибку.
        """
        sr = Voice._import("speech_recognition", "SpeechRecognition")
        lang = Voice._google_lang(language)
        wav = None
        try:
            recognizer = sr.Recognizer()
            if audio_path:
                wav = Voice._to_mono_16k(audio_path)
                with sr.AudioFile(wav) as source:
                    audio = recognizer.record(source)
            else:
                recognizer.dynamic_energy_threshold = dynamic_energy
                recognizer.pause_threshold = pause_threshold
                if energy_threshold is not None:
                    recognizer.energy_threshold = energy_threshold
                with sr.Microphone(device_index=input_device) as source:
                    if adjust_noise:
                        recognizer.adjust_for_ambient_noise(source, duration=noise_duration)
                    audio = recognizer.listen(
                        source,
                        timeout=timeout if timeout is not None else seconds,
                        phrase_time_limit=phrase_time_limit if phrase_time_limit is not None else seconds,
                    )
            return recognizer.recognize_google(audio, key=key, language=lang)
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            if raise_errors:
                raise
            print(f"❌ Ошибка Google STT: {e}")
            return ""
        finally:
            Voice._remove(wav)

    @staticmethod
    def listen_vosk(seconds: int = 5, model: Optional[str] = None, language: str = "ru",
                    sample_rate: int = 16000, input_device: Optional[int] = None,
                    grammar: Optional[List[str]] = None, max_alternatives: int = 0,
                    partial_callback: Optional[Callable[[str], None]] = None,
                    stop_on_phrase: bool = True, audio_path: Optional[str] = None,
                    words_out: Optional[List[Dict[str, Any]]] = None,
                    raise_errors: bool = False) -> str:
        """
        📦 РАСПОЗНАВАНИЕ РЕЧИ ЧЕРЕЗ VOSK (ОФЛАЙН, ПОТОКОВОЕ)

        Параметры:
            seconds (int): Максимум секунд прослушивания
            model (str, optional): Папка со скачанной моделью ИЛИ имя модели для автозагрузки
                                   ('vosk-model-small-ru-0.22', 'vosk-model-ru-0.42').
                                   Если не указан — берётся небольшая модель по языку.
            language (str): Язык для автоподбора модели ('ru', 'en'...)
            sample_rate (int): Частота микрофона (16000 подходит большинству моделей)
            input_device (int, optional): Номер микрофона
            grammar (list, optional): Список разрешённых фраз — Vosk распознаёт ТОЛЬКО их
                                      (точнее для команд). Неизвестное будет как '[unk]'.
            max_alternatives (int): Сколько вариантов распознавания учитывать (0 — один лучший)
            partial_callback (callable, optional): Функция, которой передаётся промежуточный текст по мере речи
            stop_on_phrase (bool): Вернуть результат сразу после первой законченной фразы
            audio_path (str, optional): Распознать файл вместо микрофона
            words_out (list, optional): Сюда добавятся слова с таймкодами {"word", "start", "end"}
            raise_errors (bool): True — выбрасывать ошибки, False — печатать и вернуть ""

        Возвращает:
            str: Распознанный текст или пустая строка

        Пример:
            >>> text = Voice.listen_vosk(seconds=8)
            >>> cmd = Voice.listen_vosk(grammar=["включи свет", "выключи свет", "[unk]"])
            >>> Voice.listen_vosk(partial_callback=lambda t: print("…", t))

        Примечание:
            Модели: https://alphacephei.com/vosk/models. Первый запуск с model=None или
            именем скачивает модель в ~/.cache/vosk.
        """
        vosk = Voice._import("vosk")

        def text_of(raw: str) -> str:
            data = json.loads(raw)
            if "text" in data:
                return data["text"]
            alternatives = data.get("alternatives") or [{}]
            return alternatives[0].get("text", "")

        def collect(raw: str) -> None:
            if words_out is not None:
                for item in json.loads(raw).get("result", []):
                    words_out.append({"word": item["word"], "start": item["start"], "end": item["end"]})

        wav = None
        try:
            vosk_model = Voice._get_vosk(model, language)
            rate = 16000 if audio_path else sample_rate
            if grammar:
                recognizer = vosk.KaldiRecognizer(vosk_model, rate, json.dumps(grammar, ensure_ascii=False))
            else:
                recognizer = vosk.KaldiRecognizer(vosk_model, rate)
            if words_out is not None:
                recognizer.SetWords(True)
            if max_alternatives > 0:
                recognizer.SetMaxAlternatives(int(max_alternatives))

            texts: List[str] = []

            if audio_path:
                import wave
                wav = Voice._to_mono_16k(audio_path)
                with wave.open(wav, "rb") as handle:
                    while True:
                        chunk = handle.readframes(4000)
                        if not chunk:
                            break
                        if recognizer.AcceptWaveform(chunk):
                            raw = recognizer.Result()
                            collect(raw)
                            if text_of(raw):
                                texts.append(text_of(raw))
                raw = recognizer.FinalResult()
                collect(raw)
                if text_of(raw):
                    texts.append(text_of(raw))
                return " ".join(texts)

            sd = Voice._import("sounddevice")
            block_size = max(1, int(sample_rate * 0.1))
            deadline = time.time() + seconds
            last_partial = ""
            with sd.RawInputStream(samplerate=sample_rate, blocksize=block_size, device=input_device,
                                   dtype="int16", channels=1) as stream:
                while time.time() < deadline:
                    data, _overflow = stream.read(block_size)
                    if recognizer.AcceptWaveform(bytes(data)):
                        raw = recognizer.Result()
                        collect(raw)
                        phrase = text_of(raw)
                        if phrase:
                            texts.append(phrase)
                            if stop_on_phrase:
                                return " ".join(texts)
                    elif partial_callback:
                        partial = json.loads(recognizer.PartialResult()).get("partial", "")
                        if partial and partial != last_partial:
                            last_partial = partial
                            partial_callback(partial)
            raw = recognizer.FinalResult()
            collect(raw)
            if text_of(raw):
                texts.append(text_of(raw))
            return " ".join(texts)
        except Exception as e:
            if raise_errors:
                raise
            print(f"❌ Ошибка Vosk: {e}")
            return ""
        finally:
            Voice._remove(wav)

    @staticmethod
    def listen_gigaam(seconds: int = 5, model: str = "v3_ctc", device: Optional[str] = None,
                      fp16_encoder: bool = True, use_flash: bool = False,
                      download_root: Optional[str] = None, stop_on_silence: bool = True,
                      silence_threshold: float = 0.01, silence_seconds: float = 1.0,
                      input_device: Optional[int] = None, audio_path: Optional[str] = None,
                      words_out: Optional[List[Dict[str, Any]]] = None,
                      raise_errors: bool = False) -> str:
        """
        🧠 РАСПОЗНАВАНИЕ РЕЧИ ЧЕРЕЗ GigaAM (СБЕР, ОФЛАЙН)

        Параметры:
            seconds (int): Максимум секунд записи с микрофона
            model (str): Модель: 'v3_ctc' (по умолчанию), 'v3_rnnt', 'v3_e2e_ctc' и 'v3_e2e_rnnt'
                         (с пунктуацией и нормализацией), 'v2_ctc', 'multilingual_ctc'...
                         Список: Voice.GIGAAM_MODELS. Можно указать путь к дообученному .ckpt
            device (str, optional): 'cpu' или 'cuda' (по умолчанию cuda, если есть)
            fp16_encoder (bool): Половинная точность энкодера (работает только на GPU)
            use_flash (bool): Flash Attention (нужна библиотека flash_attn и GPU)
            download_root (str, optional): Куда качать веса (по умолчанию ~/.cache/gigaam)
            stop_on_silence (bool): Остановить запись, когда фраза закончилась
            silence_threshold (float): Громкость (0..1), ниже которой считается тишиной
            silence_seconds (float): Сколько секунд тишины означают конец фразы
            input_device (int, optional): Номер микрофона
            audio_path (str, optional): Распознать файл вместо микрофона
            words_out (list, optional): Сюда добавятся слова с таймкодами {"word", "start", "end"}
            raise_errors (bool): True — выбрасывать ошибки, False — печатать и вернуть ""

        Возвращает:
            str: Распознанный текст или пустая строка

        Пример:
            >>> text = Voice.listen_gigaam(seconds=10)
            >>> text = Voice.listen_gigaam(model="v3_e2e_ctc")     # с пунктуацией
            >>> text = Voice.listen_gigaam(audio_path="my_voice.wav", device="cpu")

        Примечание:
            Нужны torch и пакет gigaam (версия 0.2.0 с GitHub, не с PyPI) и ffmpeg.
            Записи длиннее ~24 секунд режутся на куски по паузам автоматически.
        """
        path, is_temp = audio_path, False
        try:
            if not path:
                path = Voice.record(seconds, sample_rate=16000, input_device=input_device,
                                    stop_on_silence=stop_on_silence, silence_threshold=silence_threshold,
                                    silence_seconds=silence_seconds)
                is_temp = True
            gm = Voice._get_gigaam(model, device, fp16_encoder, use_flash, download_root)
            want_words = words_out is not None

            def unpack(result, offset: float) -> Tuple[str, List[Dict[str, Any]]]:
                text = getattr(result, "text", result)
                words = []
                for w in (getattr(result, "words", None) or []):
                    words.append({"word": w.text, "start": w.start + offset, "end": w.end + offset})
                return str(text).strip(), words

            def run(file_path: str):
                return gm.transcribe(file_path, word_timestamps=True) if want_words else gm.transcribe(file_path)

            data, sample_rate = Voice._read_audio(path)
            mono = data if data.ndim == 1 else data.mean(axis=1)
            if len(mono) / float(sample_rate) <= 24.0:
                text, words = unpack(run(path), 0.0)
            else:
                parts, words = [], []
                for start, end in Voice._split_audio(mono, sample_rate, 20.0):
                    piece = Voice._tmp(".wav")
                    try:
                        Voice._write_audio(piece, mono[start:end], sample_rate)
                        chunk_text, chunk_words = unpack(run(piece), start / float(sample_rate))
                    finally:
                        Voice._remove(piece)
                    if chunk_text:
                        parts.append(chunk_text)
                        words.extend(chunk_words)
                text = " ".join(parts)
            if words_out is not None:
                words_out.extend(words)
            return text
        except ImportError:
            raise
        except Exception as e:
            if raise_errors:
                raise
            print(f"❌ Ошибка GigaAM: {e}")
            return ""
        finally:
            if is_temp:
                Voice._remove(path)

    @staticmethod
    def listen_whisper(seconds: int = 5, model: str = "small", language: Optional[str] = "ru",
                       device: str = "auto", compute_type: str = "default", beam_size: int = 5,
                       vad_filter: bool = True, initial_prompt: Optional[str] = None,
                       temperature: float = 0.0, condition_on_previous_text: bool = False,
                       no_speech_threshold: float = 0.6, cpu_threads: int = 0,
                       download_root: Optional[str] = None, stop_on_silence: bool = True,
                       silence_threshold: float = 0.01, silence_seconds: float = 1.0,
                       input_device: Optional[int] = None, audio_path: Optional[str] = None,
                       words_out: Optional[List[Dict[str, Any]]] = None,
                       raise_errors: bool = False) -> str:
        """
        🌀 РАСПОЗНАВАНИЕ РЕЧИ ЧЕРЕЗ WHISPER (faster-whisper, ОФЛАЙН)

        Параметры:
            seconds (int): Максимум секунд записи с микрофона
            model (str): Размер модели: 'tiny', 'base', 'small', 'medium', 'large-v3' или путь к своей
            language (str, optional): Язык ('ru', 'en'...). None — определить автоматически
            device (str): 'auto', 'cpu' или 'cuda'
            compute_type (str): Точность: 'default', 'int8' (быстро на CPU), 'float16' (GPU)
            beam_size (int): Ширина поиска (больше — точнее, но медленнее)
            vad_filter (bool): Отрезать тишину перед распознаванием (меньше «галлюцинаций»)
            initial_prompt (str, optional): Подсказка со словами/именами, которые встретятся ("Кеша, Юсуф")
            temperature (float): 0.0 — самый точный результат
            condition_on_previous_text (bool): Учитывать предыдущий текст (на длинных записях может зацикливаться)
            no_speech_threshold (float): Порог, ниже которого фрагмент считается тишиной
            cpu_threads (int): Число потоков CPU (0 — авто)
            download_root (str, optional): Куда качать веса
            stop_on_silence (bool): Остановить запись, когда фраза закончилась
            silence_threshold (float): Громкость (0..1), ниже которой считается тишиной
            silence_seconds (float): Сколько секунд тишины означают конец фразы
            input_device (int, optional): Номер микрофона
            audio_path (str, optional): Распознать файл вместо микрофона
            words_out (list, optional): Сюда добавятся слова с таймкодами {"word", "start", "end"}
            raise_errors (bool): True — выбрасывать ошибки, False — печатать и вернуть ""

        Возвращает:
            str: Распознанный текст или пустая строка

        Пример:
            >>> text = Voice.listen_whisper(seconds=10)
            >>> text = Voice.listen_whisper(model="medium", compute_type="int8", initial_prompt="Кеша, Юсуф")
            >>> text = Voice.listen_whisper(audio_path="interview.mp3", language=None)

        Примечание:
            Первый запуск скачивает модель (small ≈ 500 МБ). Файлы любого формата читает
            сама библиотека, ffmpeg для этого не нужен.
        """
        path, is_temp = audio_path, False
        try:
            if not path:
                path = Voice.record(seconds, sample_rate=16000, input_device=input_device,
                                    stop_on_silence=stop_on_silence, silence_threshold=silence_threshold,
                                    silence_seconds=silence_seconds)
                is_temp = True
            wm = Voice._get_whisper(model, device, compute_type, cpu_threads, download_root)
            segments, _info = wm.transcribe(
                path, language=language, beam_size=beam_size, vad_filter=vad_filter,
                initial_prompt=initial_prompt, temperature=temperature,
                condition_on_previous_text=condition_on_previous_text,
                no_speech_threshold=no_speech_threshold, word_timestamps=words_out is not None,
            )
            texts = []
            for segment in segments:
                piece = segment.text.strip()
                if piece:
                    texts.append(piece)
                if words_out is not None:
                    for w in (segment.words or []):
                        words_out.append({"word": w.word.strip(), "start": w.start, "end": w.end})
            return " ".join(texts)
        except ImportError:
            raise
        except Exception as e:
            if raise_errors:
                raise
            print(f"❌ Ошибка Whisper: {e}")
            return ""
        finally:
            if is_temp:
                Voice._remove(path)

# =============================================================================
# КЛАСС GigaChat – ИИ ОТ СБЕРБАНКА
# =============================================================================


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
            >>> ai.chat("Что на фото?", images="photo.jpg", model="GigaChat-2-Max")
            >>> print(ai.last_usage)   # {'prompt_tokens': ..., 'completion_tokens': ..., ...}

        Примечание:
            Одно сообщение может содержать только одно изображение, поэтому несколько картинок
            уходят отдельными сообщениями (для нескольких изображений это не проверено на реальном API).
            Несколько документов за раз учитываются только при function_call='auto' — он ставится сам.
        """
        use_history = self.remember if history is None else history
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
            model (str, optional): Модель (если не «видит» картинку — попробуй более мощную, например 'GigaChat-2-Max')
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
            model (str, optional): Модель (по умолчанию self.model)

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
        payload = {"model": model or self.model, "function_call": "auto",
                   "messages": [{"role": "user", "content": text}]}
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


# =============================================================================
# КЛАСС FolderUtils – РАБОТА С ФАЙЛОВОЙ СИСТЕМОЙ (РАСШИРЕННАЯ ВЕРСИЯ)
# =============================================================================

class FolderUtils:
    """
    📁 УТИЛИТЫ ДЛЯ РАБОТЫ С ФАЙЛОВОЙ СИСТЕМОЙ

    Все методы статические. Позволяют создавать, копировать, перемещать,
    переименовывать, искать и получать информацию о файлах и папках.

    📌 ПРИМЕРЫ:
        >>> FolderUtils.create("my_project/data")
        >>> FolderUtils.rename("old.txt", "new.txt")
        >>> FolderUtils.safe_move("file.txt", "backup/file.txt", overwrite=True)
        >>> FolderUtils.move_files("src", "dst", "*.py", recursive=True)
        >>> all_py = FolderUtils.find_files(".", ".py")
        >>> size = FolderUtils.get_size("my_project")
    """

    # -------------------------------------------------------------------------
    # 📂 СОЗДАНИЕ И УДАЛЕНИЕ
    # -------------------------------------------------------------------------

    @staticmethod
    def create(path: str) -> bool:
        """
        📂 СОЗДАНИЕ ПАПКИ (И ПРОМЕЖУТОЧНЫХ, ПРИ НЕОБХОДИМОСТИ)

        Параметры:
            path (str): Путь к новой папке

        Возвращает:
            bool: True, если папка создана; False, если уже существует

        Пример:
            >>> FolderUtils.create("backups/2024/январь")
        """
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"📂 Папка создана: {path}")
            return True
        else:
            print(f"📂 Папка уже существует: {path}")
            return False

    @staticmethod
    def delete(path: str) -> bool:
        """
        🗑️ УДАЛЕНИЕ ПАПКИ СО ВСЕМ СОДЕРЖИМЫМ (ОСТОРОЖНО!)

        Параметры:
            path (str): Путь к папке

        Возвращает:
            bool: True при успехе, False при ошибке или отсутствии папки
        """
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                print(f"🗑️ Папка удалена: {path}")
                return True
            else:
                print(f"❌ Папка не найдена: {path}")
                return False
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            return False

    # -------------------------------------------------------------------------
    # 📦 ПЕРЕМЕЩЕНИЕ И КОПИРОВАНИЕ
    # -------------------------------------------------------------------------

    @staticmethod
    def move(src: str, dst: str) -> bool:
        """
        📦 ПЕРЕМЕЩЕНИЕ ФАЙЛА ИЛИ ПАПКИ (без проверок, просто перемещает)

        Параметры:
            src (str): Исходный путь
            dst (str): Путь назначения

        Возвращает:
            bool: True при успехе
        """
        try:
            shutil.move(src, dst)
            print(f"📦 Перемещено: {src} → {dst}")
            return True
        except Exception as e:
            print(f"❌ Ошибка перемещения: {e}")
            return False

    @staticmethod
    def copy(src: str, dst: str) -> bool:
        """
        📋 КОПИРОВАНИЕ ФАЙЛА ИЛИ ПАПКИ (ПЕРЕЗАПИСЬ СУЩЕСТВУЮЩЕГО)

        Параметры:
            src (str): Исходный путь
            dst (str): Путь назначения

        Возвращает:
            bool: True при успехе

        Примечание:
            Для папок используется copytree с перезаписью (dirs_exist_ok=True для Python 3.8+).
        """
        try:
            if os.path.isdir(src):
                if sys.version_info >= (3, 8):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"📋 Скопировано: {src} → {dst}")
            return True
        except Exception as e:
            print(f"❌ Ошибка копирования: {e}")
            return False

    @staticmethod
    def rename(src: str, new_name: str) -> bool:
        """
        📝 ПЕРЕИМЕНОВАНИЕ ФАЙЛА ИЛИ ПАПКИ (без перемещения в другой каталог)

        Параметры:
            src (str): Полный путь к файлу или папке.
            new_name (str): Новое имя (только имя, без пути).

        Возвращает:
            bool: True при успехе, False при ошибке.

        Пример:
            >>> FolderUtils.rename("C:/data/old.txt", "new.txt")
        """
        try:
            dirname = os.path.dirname(src)
            new_path = os.path.join(dirname, new_name)
            os.rename(src, new_path)
            print(f"📝 Переименовано: {src} → {new_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка переименования: {e}")
            return False

    @staticmethod
    def safe_move(src: str, dst: str, overwrite: bool = False, create_dst_dir: bool = True) -> bool:
        """
        📦 БЕЗОПАСНОЕ ПЕРЕМЕЩЕНИЕ ФАЙЛА ИЛИ ПАПКИ (с проверкой перезаписи и созданием папки назначения)

        Параметры:
            src (str): Исходный путь.
            dst (str): Путь назначения (может быть как новым именем, так и папкой).
            overwrite (bool): Если True, перезаписывать существующий файл/папку.
                              Если False, при конфликте добавляет суффикс "_copy".
            create_dst_dir (bool): Если True, создаёт родительские папки назначения.

        Возвращает:
            bool: True при успехе, False при ошибке.

        Пример:
            >>> FolderUtils.safe_move("data.txt", "backup/data.txt", overwrite=True)
            >>> FolderUtils.safe_move("project", "archive/project", overwrite=False)
        """
        try:
            src = os.path.abspath(src)
            dst = os.path.abspath(dst)

            # Определяем, является ли dst папкой (если существует)
            if os.path.exists(dst) and os.path.isdir(dst):
                # Если dst - папка, то перемещаем внутрь с сохранением имени
                dst_path = os.path.join(dst, os.path.basename(src))
            else:
                dst_path = dst

            # Создаём родительские папки для dst_path, если нужно
            if create_dst_dir:
                dst_dir = os.path.dirname(dst_path)
                if dst_dir and not os.path.exists(dst_dir):
                    os.makedirs(dst_dir, exist_ok=True)

            # Обработка конфликта, если файл уже существует
            if os.path.exists(dst_path):
                if overwrite:
                    # Если папка, удаляем её (осторожно!)
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                else:
                    # Добавляем суффикс "_copy" к имени
                    base, ext = os.path.splitext(dst_path)
                    counter = 1
                    while True:
                        new_dst = f"{base}_copy{counter}{ext}"
                        if not os.path.exists(new_dst):
                            dst_path = new_dst
                            break
                        counter += 1
                    print(f"⚠️ Конфликт, сохранено как: {dst_path}")

            # Перемещение
            shutil.move(src, dst_path)
            print(f"📦 Перемещено: {src} → {dst_path}")
            return True

        except Exception as e:
            print(f"❌ Ошибка безопасного перемещения: {e}")
            return False

    @staticmethod
    def move_files(src_dir: str, dst_dir: str, pattern: Optional[str] = None,
                   recursive: bool = False) -> int:
        """
        📁 ГРУППОВОЕ ПЕРЕМЕЩЕНИЕ ФАЙЛОВ ПО МАСКЕ

        Параметры:
            src_dir (str): Исходная папка.
            dst_dir (str): Папка назначения (будет создана, если не существует).
            pattern (str, optional): Маска файлов (например, "*.txt", "data_*.csv").
                                    Если None, перемещаются все файлы.
            recursive (bool): Если True, обрабатывает вложенные папки рекурсивно.

        Возвращает:
            int: Количество перемещённых файлов.

        Пример:
            >>> FolderUtils.move_files("downloads", "archive", "*.pdf")
            >>> FolderUtils.move_files("src", "backup", "*.py", recursive=True)
        """
        import fnmatch

        try:
            src_dir = os.path.abspath(src_dir)
            dst_dir = os.path.abspath(dst_dir)

            if not os.path.isdir(src_dir):
                raise NotADirectoryError(f"Исходная папка не существует: {src_dir}")

            os.makedirs(dst_dir, exist_ok=True)

            count = 0
            # Рекурсивный или нерекурсивный обход
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    # Проверка маски
                    if pattern is not None:
                        if not fnmatch.fnmatch(file, pattern):
                            continue

                    src_path = os.path.join(root, file)
                    # Если recursive=False, пропускаем файлы в подпапках
                    if not recursive and root != src_dir:
                        continue

                    # Относительный путь для сохранения структуры (при recursive=True)
                    rel_path = os.path.relpath(root, src_dir) if recursive else ""
                    dst_path = os.path.join(dst_dir, rel_path, file) if rel_path else os.path.join(dst_dir, file)

                    # Создаём папку назначения для файла
                    dst_subdir = os.path.dirname(dst_path)
                    if dst_subdir:
                        os.makedirs(dst_subdir, exist_ok=True)

                    shutil.move(src_path, dst_path)
                    count += 1
                    print(f"   → {src_path} -> {dst_path}")

            print(f"📁 Перемещено файлов: {count}")
            return count

        except Exception as e:
            print(f"❌ Ошибка группового перемещения: {e}")
            return 0

    @staticmethod
    def move_folder(src: str, dst: str, overwrite: bool = False) -> bool:
        """
        📂 ПЕРЕМЕЩЕНИЕ ЦЕЛОЙ ПАПКИ (с контролем перезаписи)

        Параметры:
            src (str): Исходный путь к папке.
            dst (str): Путь назначения (новая папка или родительская папка).
            overwrite (bool): Если True, перезаписывает существующую папку.

        Возвращает:
            bool: True при успехе, False при ошибке.

        Пример:
            >>> FolderUtils.move_folder("project_old", "project_new", overwrite=True)
        """
        try:
            src = os.path.abspath(src)
            dst = os.path.abspath(dst)

            if not os.path.isdir(src):
                raise NotADirectoryError(f"Исходная папка не существует: {src}")

            # Если dst уже существует как папка, перемещаем внутрь
            if os.path.exists(dst) and os.path.isdir(dst):
                # Если dst - папка, перемещаем src внутрь
                dst_path = os.path.join(dst, os.path.basename(src))
            else:
                dst_path = dst

            # Если папка назначения уже существует и overwrite=True, удаляем её
            if os.path.exists(dst_path):
                if overwrite:
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                else:
                    raise FileExistsError(f"Папка назначения уже существует: {dst_path}")

            # Перемещаем (shutil.move работает и с папками)
            shutil.move(src, dst_path)
            print(f"📂 Папка перемещена: {src} → {dst_path}")
            return True

        except Exception as e:
            print(f"❌ Ошибка перемещения папки: {e}")
            return False

    # -------------------------------------------------------------------------
    # 🔍 ПОИСК И ОБХОД
    # -------------------------------------------------------------------------

    @staticmethod
    def find_files(directory: str, extension: Optional[str] = None) -> List[str]:
        """
        🔍 ПОИСК ФАЙЛОВ В ПАПКЕ И ВЛОЖЕННЫХ ПАПКАХ

        Параметры:
            directory (str): Папка для поиска
            extension (str, optional): Фильтр по расширению (например, ".py")

        Возвращает:
            list[str]: Список полных путей к найденным файлам

        Пример:
            >>> py_files = FolderUtils.find_files("src", ".py")
        """
        result = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if extension is None or file.endswith(extension):
                    result.append(os.path.join(root, file))
        print(f"🔍 Найдено {len(result)} файлов" + (f" с расширением {extension}" if extension else ""))
        return result

    @staticmethod
    def find_folders(directory: str) -> List[str]:
        """
        📁 ПОИСК ВСЕХ ПОДПАПОК В УКАЗАННОЙ ДИРЕКТОРИИ

        Параметры:
            directory (str): Папка для поиска

        Возвращает:
            list[str]: Список путей к подпапкам
        """
        result = []
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                result.append(os.path.join(root, d))
        print(f"📁 Найдено {len(result)} подпапок")
        return result

    # -------------------------------------------------------------------------
    # ℹ️ ИНФОРМАЦИЯ О ФАЙЛАХ И ПУТЯХ
    # -------------------------------------------------------------------------

    @staticmethod
    def current_dir() -> str:
        """
        📍 ВОЗВРАЩАЕТ ТЕКУЩУЮ РАБОЧУЮ ДИРЕКТОРИЮ

        Возвращает:
            str: Полный путь
        """
        return os.getcwd()

    @staticmethod
    def get_filename(path: str) -> str:
        """
        📄 ИЗВЛЕЧЕНИЕ ИМЕНИ ФАЙЛА ИЗ ПОЛНОГО ПУТИ

        Параметры:
            path (str): Полный путь

        Возвращает:
            str: Имя файла с расширением
        """
        return os.path.basename(path)

    @staticmethod
    def get_extension(path: str) -> str:
        """
        🔤 ИЗВЛЕЧЕНИЕ РАСШИРЕНИЯ ФАЙЛА (С ТОЧКОЙ)

        Параметры:
            path (str): Путь к файлу

        Возвращает:
            str: Расширение, например ".txt"
        """
        return os.path.splitext(path)[1]

    @staticmethod
    def get_filename_without_ext(path: str) -> str:
        """
        📄 ИМЯ ФАЙЛА БЕЗ РАСШИРЕНИЯ

        Параметры:
            path (str): Путь к файлу

        Возвращает:
            str: Имя без расширения
        """
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def get_parent(path: str) -> str:
        """
        📂 РОДИТЕЛЬСКАЯ ПАПКА

        Параметры:
            path (str): Путь к файлу или папке

        Возвращает:
            str: Путь к родительской папке
        """
        return os.path.dirname(path)

    @staticmethod
    def get_size(path: str) -> int:
        """
        📏 РАЗМЕР ФАЙЛА ИЛИ ПАПКИ В БАЙТАХ

        Параметры:
            path (str): Путь к файлу или папке

        Возвращает:
            int: Размер в байтах
        """
        total = 0
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        return total

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        📊 ФОРМАТИРОВАНИЕ РАЗМЕРА В ЧИТАЕМЫЙ ВИД (B, KB, MB, GB, TB)

        Параметры:
            size_bytes (int): Размер в байтах

        Возвращает:
            str: Например, "2.5 MB"
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def exists(path: str) -> bool:
        """❓ ПРОВЕРКА СУЩЕСТВОВАНИЯ ФАЙЛА ИЛИ ПАПКИ"""
        return os.path.exists(path)

    @staticmethod
    def is_file(path: str) -> bool:
        """📄 ПРОВЕРКА, ЯВЛЯЕТСЯ ЛИ ПУТЬ ФАЙЛОМ"""
        return os.path.isfile(path)

    @staticmethod
    def is_folder(path: str) -> bool:
        """📁 ПРОВЕРКА, ЯВЛЯЕТСЯ ЛИ ПУТЬ ПАПКОЙ"""
        return os.path.isdir(path)

    @staticmethod
    def list_contents(directory: str) -> Dict[str, List[str]]:
        """
        📋 ВОЗВРАЩАЕТ ФАЙЛЫ И ПАПКИ В УКАЗАННОЙ ДИРЕКТОРИИ

        Параметры:
            directory (str): Путь к папке

        Возвращает:
            dict: {"files": [...], "folders": [...]}
        """
        files = []
        folders = []
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    files.append(item)
                elif os.path.isdir(full_path):
                    folders.append(item)
        except Exception as e:
            print(f"❌ Ошибка чтения папки: {e}")
        return {"files": files, "folders": folders}

# =============================================================================
# КЛАСС Console – РАБОТА С КОНСОЛЬЮ
# =============================================================================

class Console:
    """
    🖥️ РАБОТА С КОНСОЛЬЮ / ТЕРМИНАЛОМ

    Статические методы для цветного вывода, управления курсором, прогресс-баров,
    а также скрытия/показа окна консоли (Windows).

    📌 ПРИМЕРЫ:
        >>> Console.success("Файл сохранён!")
        >>> Console.progress_bar(100, "Загрузка")
        >>> w, h = Console.size()
    """

    # -------------------------------------------------------------------------
    # СКРЫТИЕ / ПОКАЗ КОНСОЛИ (WINDOWS)
    # -------------------------------------------------------------------------

    @staticmethod
    def hide() -> None:
        """
        👻 СКРЫТЬ ОКНО КОНСОЛИ (Windows)

        Перезапускает скрипт в фоновом режиме (pythonw.exe).
        """
        if sys.platform == "win32" and '--hidden' not in sys.argv:
            pythonw_path = sys.executable.replace('python.exe', 'pythonw.exe')
            if os.path.exists(pythonw_path):
                subprocess.Popen(
                    [pythonw_path] + sys.argv + ['--hidden'],
                    creationflags=0x00000008 | 0x08000000,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
                sys.exit(0)

    @staticmethod
    def show() -> None:
        """
        📺 ПОКАЗАТЬ КОНСОЛЬ (Windows)

        Создаёт новую консоль и привязывает к ней процесс.
        На других ОС выводит предупреждение.
        """
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32')
            kernel32.AllocConsole()
        else:
            print("⚠️ Console.show() поддерживается только в Windows")

    # -------------------------------------------------------------------------
    # ЦВЕТНОЙ ТЕКСТ
    # -------------------------------------------------------------------------

    @staticmethod
    def color(text: str, fg: Optional[str] = None, bg: Optional[str] = None, style: Optional[str] = None) -> str:
        """
        🎨 ОКРАШИВАНИЕ ТЕКСТА ANSI-ЦВЕТАМИ ДЛЯ КОНСОЛИ

        Параметры:
            text (str): Текст
            fg (str): Цвет текста ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', ...)
            bg (str): Цвет фона ('bg_red', 'bg_green', ...)
            style (str): Стиль ('bold', 'underline', 'italic', 'blink')

        Возвращает:
            str: Строка с ANSI-кодами

        Пример:
            >>> print(Console.color("Ошибка!", "red", style="bold"))
        """
        colors = {
            'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
            'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37',
            'bright_black': '90', 'bright_red': '91', 'bright_green': '92',
            'bright_yellow': '93', 'bright_blue': '94', 'bright_magenta': '95',
            'bright_cyan': '96', 'bright_white': '97',
            'bg_black': '40', 'bg_red': '41', 'bg_green': '42', 'bg_yellow': '43',
            'bg_blue': '44', 'bg_magenta': '45', 'bg_cyan': '46', 'bg_white': '47',
            'bg_bright_black': '100', 'bg_bright_red': '101', 'bg_bright_green': '102',
            'bg_bright_yellow': '103', 'bg_bright_blue': '104', 'bg_bright_magenta': '105',
            'bg_bright_cyan': '106', 'bg_bright_white': '107',
            'bold': '1', 'dim': '2', 'italic': '3', 'underline': '4',
            'blink': '5', 'reverse': '7', 'hidden': '8', 'strikethrough': '9'
        }
        codes = []
        if fg and fg in colors:
            codes.append(colors[fg])
        if bg and bg in colors:
            codes.append(colors[bg])
        if style and style in colors:
            codes.append(colors[style])
        if codes:
            return f'\033[{";".join(codes)}m{text}\033[0m'
        return text

    # -------------------------------------------------------------------------
    # УПРАВЛЕНИЕ КУРСОРОМ
    # -------------------------------------------------------------------------

    @staticmethod
    def clear() -> None:
        """🧹 ОЧИСТКА ВСЕГО ЭКРАНА КОНСОЛИ"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def move_to(x: int, y: int) -> None:
        """
        ➡️ ПЕРЕМЕЩЕНИЕ КУРСОРА В ПОЗИЦИЮ (x, y)

        Параметры:
            x (int): Столбец (1 — левый)
            y (int): Строка (1 — верхняя)
        """
        sys.stdout.write(f'\033[{y};{x}H')
        sys.stdout.flush()

    @staticmethod
    def move_up(n: int = 1) -> None:
        """⬆️ ПЕРЕМЕЩЕНИЕ КУРСОРА ВВЕРХ НА n СТРОК"""
        sys.stdout.write(f'\033[{n}A')
        sys.stdout.flush()

    @staticmethod
    def move_down(n: int = 1) -> None:
        """⬇️ ПЕРЕМЕЩЕНИЕ КУРСОРА ВНИЗ НА n СТРОК"""
        sys.stdout.write(f'\033[{n}B')
        sys.stdout.flush()

    @staticmethod
    def hide_cursor() -> None:
        """🙈 СКРЫТЬ КУРСОР"""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

    @staticmethod
    def show_cursor() -> None:
        """👁️ ПОКАЗАТЬ КУРСОР"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    @staticmethod
    def save_pos() -> None:
        """💾 СОХРАНИТЬ ТЕКУЩУЮ ПОЗИЦИЮ КУРСОРА"""
        sys.stdout.write('\033[s')
        sys.stdout.flush()

    @staticmethod
    def restore_pos() -> None:
        """🔄 ВОССТАНОВИТЬ СОХРАНЁННУЮ ПОЗИЦИЮ"""
        sys.stdout.write('\033[u')
        sys.stdout.flush()

    # -------------------------------------------------------------------------
    # ПРОЧИЕ УТИЛИТЫ
    # -------------------------------------------------------------------------

    @staticmethod
    def size() -> Tuple[int, int]:
        """
        📏 РАЗМЕР КОНСОЛИ (ШИРИНА, ВЫСОТА) В СИМВОЛАХ

        Возвращает:
            tuple: (columns, lines)
        """
        try:
            return os.get_terminal_size().columns, os.get_terminal_size().lines
        except Exception:
            return 80, 24

    @staticmethod
    def center(text: str) -> str:
        """
        🎯 ЦЕНТРИРОВАНИЕ ТЕКСТА ПО ШИРИНЕ КОНСОЛИ

        Параметры:
            text (str): Текст

        Возвращает:
            str: Текст, дополненный пробелами
        """
        w, _ = Console.size()
        return text.center(w)

    @staticmethod
    def progress_bar(total: int, prefix: str = "", suffix: str = "", length: int = 50, fill: str = "█") -> None:
        """
        📊 АНИМИРОВАННЫЙ ПРОГРЕСС-БАР В КОНСОЛИ

        Параметры:
            total (int): Общее количество шагов
            prefix (str): Текст перед баром
            suffix (str): Текст после бара
            length (int): Длина бара в символах
            fill (str): Символ заполнения
        """
        for i in range(total + 1):
            percent = i / total
            filled = int(length * percent)
            bar = fill * filled + "░" * (length - filled)
            sys.stdout.write(f"\r{prefix} [{bar}] {percent:.1%} {suffix}")
            sys.stdout.flush()
            if i < total:
                time.sleep(0.05)
        print()

    # -------------------------------------------------------------------------
    # БЫСТРЫЕ СООБЩЕНИЯ
    # -------------------------------------------------------------------------

    @staticmethod
    def success(text: str) -> None:
        """✅ ЗЕЛЁНОЕ СООБЩЕНИЕ ОБ УСПЕХЕ"""
        print(Console.color(f"✓ {text}", "green"))

    @staticmethod
    def error(text: str) -> None:
        """❌ КРАСНОЕ СООБЩЕНИЕ ОБ ОШИБКЕ"""
        print(Console.color(f"✗ {text}", "red"))

    @staticmethod
    def warning(text: str) -> None:
        """⚠️ ЖЁЛТОЕ ПРЕДУПРЕЖДЕНИЕ"""
        print(Console.color(f"⚠ {text}", "yellow"))

    @staticmethod
    def info(text: str) -> None:
        """ℹ️ ГОЛУБОЕ ИНФОРМАЦИОННОЕ СООБЩЕНИЕ"""
        print(Console.color(f"ℹ {text}", "cyan"))

    @staticmethod
    def header(text: str, symbol: str = "=") -> None:
        """
        📌 КРАСИВЫЙ ЗАГОЛОВОК НА ВСЮ ШИРИНУ КОНСОЛИ

        Параметры:
            text (str): Текст заголовка
            symbol (str): Символ для линии (по умолчанию "=")
        """
        w, _ = Console.size()
        line = symbol * w
        print(Console.color(line, "blue", style="bold"))
        print(Console.color(text.center(w), "blue", style="bold"))
        print(Console.color(line, "blue", style="bold"))


# =============================================================================
# КЛАСС BazaDB – УНИВЕРСАЛЬНАЯ РАБОТА С SQLite
# =============================================================================

class BazaDB:
    """
    🗄️ ПРОСТАЯ РАБОТА С БАЗОЙ ДАННЫХ SQLite

    Класс позволяет создавать таблицы, добавлять, искать, обновлять и удалять записи.
    Все колонки имеют тип TEXT, автоматически добавляется первичный ключ 'id'.

    📌 ПРИМЕР:
        >>> db = BazaDB("mybase.db")
        >>> db.create_table("users", ["name", "age"])
        >>> db.insert("users", {"name": "Юсуф", "age": "12"})
        >>> users = db.get_all("users")
        >>> db.close()
    """

    def __init__(self, db_name: str):
        """
        🚀 ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ

        Параметры:
            db_name (str): Имя файла базы данных (или ":memory:" для RAM)
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        print(f"✅ Подключено к базе: {db_name}")

    def create_table(self, table_name: str, columns: List[str], drop_if_exists: bool = False) -> None:
        """
        📦 СОЗДАНИЕ ТАБЛИЦЫ

        Параметры:
            table_name (str): Имя таблицы
            columns (list): Список имён колонок (без 'id')
            drop_if_exists (bool): Удалить таблицу, если она уже существует
        """
        if drop_if_exists:
            self.cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        cols = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        for col in columns:
            cols += f", {col} TEXT"
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({cols})')
        self.conn.commit()
        print(f"   📦 Таблица '{table_name}' создана")

    def insert(self, table_name: str, data: Dict) -> int:
        """
        ➕ ДОБАВЛЕНИЕ ЗАПИСИ В ТАБЛИЦУ

        Параметры:
            table_name (str): Имя таблицы
            data (dict): Словарь {колонка: значение}

        Возвращает:
            int: ID добавленной записи
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        self.cursor.execute(query, values)
        self.conn.commit()
        last_id = self.cursor.lastrowid
        print(f"   ➕ Добавлена запись ID={last_id} в '{table_name}'")
        return last_id

    def get_all(self, table_name: str) -> List[Dict]:
        """
        📋 ПОЛУЧИТЬ ВСЕ ЗАПИСИ ИЗ ТАБЛИЦЫ

        Параметры:
            table_name (str): Имя таблицы

        Возвращает:
            list[dict]: Список словарей с данными (пустой список, если таблица пуста)
        """
        self.cursor.execute(f'SELECT * FROM {table_name}')
        rows = self.cursor.fetchall()
        if not rows:
            print(f"   📋 Таблица '{table_name}' пуста")
            return []
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in self.cursor.fetchall()]
        result = [dict(zip(columns, row)) for row in rows]
        print(f"   📋 Получено {len(result)} записей из '{table_name}'")
        return result

    def find(self, table_name: str, column: str, value: str) -> List[Dict]:
        """
        🔍 ПОИСК ПО ТОЧНОМУ ЗНАЧЕНИЮ

        Параметры:
            table_name (str): Имя таблицы
            column (str): Имя колонки
            value (str): Точное значение для поиска

        Возвращает:
            list[dict]: Найденные записи
        """
        query = f'SELECT * FROM {table_name} WHERE {column} = ?'
        self.cursor.execute(query, (value,))
        rows = self.cursor.fetchall()
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in self.cursor.fetchall()]
        result = [dict(zip(columns, row)) for row in rows]
        print(f"   🔍 Найдено {len(result)} записей")
        return result

    def search(self, table_name: str, column: str, text: str) -> List[Dict]:
        """
        🔎 ПОИСК ПО ПОДСТРОКЕ (LIKE)

        Параметры:
            table_name (str): Имя таблицы
            column (str): Имя колонки
            text (str): Подстрока для поиска

        Возвращает:
            list[dict]: Найденные записи
        """
        query = f'SELECT * FROM {table_name} WHERE {column} LIKE ?'
        self.cursor.execute(query, (f'%{text}%',))
        rows = self.cursor.fetchall()
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in self.cursor.fetchall()]
        result = [dict(zip(columns, row)) for row in rows]
        print(f"   🔎 Найдено {len(result)} записей")
        return result

    def update(self, table_name: str, id: int, data: Dict) -> bool:
        """
        ✏️ ОБНОВЛЕНИЕ ЗАПИСИ ПО ID

        Параметры:
            table_name (str): Имя таблицы
            id (int): ID записи
            data (dict): Словарь {колонка: новое_значение}

        Возвращает:
            bool: True, если запись обновлена, иначе False
        """
        set_clause = ', '.join([f'{col} = ?' for col in data])
        values = tuple(data.values()) + (id,)
        query = f'UPDATE {table_name} SET {set_clause} WHERE id = ?'
        self.cursor.execute(query, values)
        self.conn.commit()
        if self.cursor.rowcount:
            print(f"   ✏️ Обновлена запись ID={id}")
            return True
        print(f"   ❌ Запись ID={id} не найдена")
        return False

    def delete(self, table_name: str, id: int) -> bool:
        """
        🗑️ УДАЛЕНИЕ ЗАПИСИ ПО ID

        Параметры:
            table_name (str): Имя таблицы
            id (int): ID записи

        Возвращает:
            bool: True, если удалена, иначе False
        """
        self.cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (id,))
        self.conn.commit()
        if self.cursor.rowcount:
            print(f"   🗑️ Удалена запись ID={id}")
            return True
        print(f"   ❌ Запись ID={id} не найдена")
        return False

    def clear_table(self, table_name: str) -> None:
        """🧹 УДАЛЕНИЕ ВСЕХ ЗАПИСЕЙ ИЗ ТАБЛИЦЫ (СТРУКТУРА СОХРАНЯЕТСЯ)"""
        self.cursor.execute(f'DELETE FROM {table_name}')
        self.conn.commit()
        print(f"   🧹 Таблица '{table_name}' очищена")

    def drop_table(self, table_name: str) -> None:
        """💥 ПОЛНОЕ УДАЛЕНИЕ ТАБЛИЦЫ"""
        self.cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        self.conn.commit()
        print(f"   💥 Таблица '{table_name}' удалена")

    def stats(self, table_name: str) -> Dict[str, Any]:
        """
        📊 СТАТИСТИКА ПО ТАБЛИЦЕ

        Параметры:
            table_name (str): Имя таблицы

        Возвращает:
            dict: {"total": количество записей, "columns": список колонок}
        """
        self.cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        total = self.cursor.fetchone()[0]
        self.cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in self.cursor.fetchall()]
        print(f"\n📊 Статистика '{table_name}':")
        print(f"   Записей: {total}")
        print(f"   Колонки: {', '.join(columns)}")
        return {"total": total, "columns": columns}

    def show_tables(self) -> None:
        """📁 ПОКАЗАТЬ ВСЕ ТАБЛИЦЫ В БАЗЕ ДАННЫХ"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        print("\n📋 Таблицы в базе:")
        for t in tables:
            print(f"   📁 {t[0]}")

    def close(self) -> None:
        """🔌 ЗАКРЫТЬ СОЕДИНЕНИЕ С БАЗОЙ ДАННЫХ"""
        self.conn.close()
        print("🔌 Соединение закрыто")


# =============================================================================
# КЛАСС Music – МУЗЫКАЛЬНЫЙ ПЛЕЕР (ЯНДЕКС.МУЗЫКА + VLC)
# =============================================================================

import vlc
from yandex_music import Client

class Music:
    """
    🎵 МУЗЫКАЛЬНЫЙ ПЛЕЕР С ПОДДЕРЖКОЙ ЯНДЕКС.МУЗЫКИ И VLC

    Позволяет искать и воспроизводить треки, управлять очередью, громкостью,
    а также загружать избранное (кэш на 2 часа).

    📌 ТРЕБОВАНИЯ:
        - Токен Яндекс.Музыки (получить по ссылке: https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)
        - Установленная библиотека python-vlc и yandex-music

    📌 ПРИМЕР:
        >>> player = Music(token="y0_...")  # или через переменную окружения YANDEX_MUSIC_TOKEN
        >>> player.play("Imagine Dragons")
        >>> player.pause()
        >>> player.play_my_wave(limit=15)
        >>> player.add_to_queue("Miyagi - Captain")
        >>> player.next()
    """

    def __init__(self, token: Optional[str] = None):
        """
        Инициализация плеера.

        Параметры:
            token (str, optional): OAuth-токен Яндекс.Музыки.
                                   Если не указан, берётся из переменной окружения YANDEX_MUSIC_TOKEN.
        """
        self.token = token or os.getenv("YANDEX_MUSIC_TOKEN")
        if not self.token:
            raise ValueError("❌ Токен Яндекс.Музыки не найден! Передайте token=... или установите переменную окружения YANDEX_MUSIC_TOKEN")

        self.client = Client(self.token).init()
        self.player = None
        self.current_track = None
        self._is_playing = False
        self.paused = False
        self.volume_level = 50
        self.queue = []
        self.queue_index = 0

        # Кэши
        self._cache = {}               # URL треков (3 часа)
        self._fav_cache = []           # Список избранного
        self._fav_cache_time = 0       # Время последней загрузки избранного
        self._fav_cache_ttl = 7200     # 2 часа

        self.vlc_instance = vlc.Instance('--quiet')
        self._cache_file = "track_cache.json"
        self._load_cache()
        print("✅ Музыкальный плеер готов")

    # ---------- Внутренние методы ----------
    def _load_cache(self) -> None:
        """Загружает кэш URL треков из файла (удаляет записи старше 3 часов)"""
        if os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    raw_cache = json.load(f)
                now = time.time()
                self._cache = {}
                for query, data in raw_cache.items():
                    if isinstance(data, dict) and now - data.get('timestamp', 0) < 10800:
                        self._cache[query] = data['url']
                print(f"📦 Загружен кэш треков: {len(self._cache)} записей")
            except Exception:
                self._cache = {}

    def _save_cache(self) -> None:
        """Сохраняет кэш URL треков в файл"""
        try:
            data_to_save = {}
            now = time.time()
            for query, url in self._cache.items():
                data_to_save[query] = {'url': url, 'timestamp': now}
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить кэш треков: {e}")

    def _get_track_url(self, query: str, use_cache: bool = True) -> Optional[str]:
        """
        Получает прямую ссылку на MP3 трека через поиск или из кэша.

        Параметры:
            query (str): Название трека (например "Miyagi - Captain")
            use_cache (bool): Использовать ли кэш

        Возвращает:
            str или None: URL трека или None, если не найден
        """
        if use_cache and query in self._cache:
            return self._cache[query]

        search = self.client.search(query)
        if not search.tracks or not search.tracks.results:
            return None

        track = search.tracks.results[0]
        try:
            tracks_result = self.client.tracks([track.id])
            if not tracks_result:
                return None
            full_track = tracks_result[0]
        except (IndexError, AttributeError):
            return None

        url = None
        try:
            info = full_track.get_download_info()
            if info and len(info) > 0:
                url = info[0].get_direct_link()
        except Exception:
            pass
        if not url:
            try:
                url = full_track.download_url
            except Exception:
                pass

        if use_cache and url:
            self._cache[query] = url
            self._save_cache()
        return url

    def _play_url(self, url: str, track_name: str) -> None:
        """Воспроизводит URL через VLC"""
        if self.player:
            self.player.stop()
        self.player = self.vlc_instance.media_player_new()
        media = self.vlc_instance.media_new(url)
        self.player.set_media(media)
        self.player.play()
        self.player.audio_set_volume(self.volume_level)
        self._is_playing = True
        self.paused = False
        self.current_track = track_name
        print(f"▶️ Сейчас играет: {track_name}")

    def _wait_for_end(self, timeout: int = 60) -> None:
        """
        Ожидает окончания трека с таймаутом.

        Параметры:
            timeout (int): Максимальное время ожидания в секундах
        """
        if not self.player:
            return
        start = time.time()
        while time.time() - start < timeout:
            state = self.player.get_state()
            if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
                break
            time.sleep(0.3)
        else:
            print("⚠️ Таймаут ожидания окончания трека")
        time.sleep(0.2)

    # ---------- Работа с избранным (кэш 2 часа) ----------
    def _load_favorites(self, force: bool = False) -> None:
        """
        Загружает список избранных треков во внутренний кэш.
        Повторная загрузка происходит, только если кэш устарел (старше 2 часов) или force=True.

        Параметры:
            force (bool): Принудительно обновить кэш
        """
        now = time.time()
        if not force and self._fav_cache and (now - self._fav_cache_time) < self._fav_cache_ttl:
            print(f"   → Избранное из кэша (загружено {int((now - self._fav_cache_time)/60)} мин назад)")
            return

        print("   Загрузка избранного (может занять время)...")
        self._fav_cache = []
        try:
            likes = self.client.users_likes_tracks()
            if not likes:
                print("   ⚠️ Избранное пусто.")
                self._fav_cache_time = now
                return
            for like in likes:
                try:
                    track = like.fetch_track()
                    if not track:
                        continue
                    artist_name = track.artists[0].name if track.artists else "Unknown"
                    name = f"{track.title} — {artist_name}"
                    self._fav_cache.append({'name': name, 'track_id': track.id})
                except Exception:
                    continue
            self._fav_cache_time = now
            print(f"      ✅ Загружено избранных треков: {len(self._fav_cache)} (кэш на 2 часа)")
        except Exception as e:
            print(f"      ❌ Ошибка загрузки избранного: {e}")
            self._fav_cache = []
            self._fav_cache_time = now

    # ---------- Базовые методы управления ----------
    def play(self, query: str, wait: bool = True) -> bool:
        """
        Воспроизводит трек по названию (очищает очередь)

        Параметры:
            query (str): Название трека
            wait (bool): Ожидать окончания трека

        Возвращает:
            bool: True при успехе
        """
        url = self._get_track_url(query, use_cache=True)
        if not url:
            print(f"❌ Не найден: {query}")
            return False
        self.queue = [{'name': query, 'url': url}]
        self.queue_index = 0
        self._play_url(url, query)
        if wait:
            self._wait_for_end()
        return True

    def pause(self) -> None:
        """Пауза / возобновление воспроизведения"""
        if self.player:
            if self._is_playing:
                self.player.pause()
                self._is_playing = False
                self.paused = True
                print("⏸️ Пауза")
            else:
                self.player.play()
                self._is_playing = True
                self.paused = False
                print("▶️ Продолжение")

    def stop(self) -> None:
        """Останавливает воспроизведение и сбрасывает текущий трек"""
        if self.player:
            self.player.stop()
            self._is_playing = False
            self.paused = False
            self.current_track = None
            print("⏹️ Остановлено")

    def next(self, wait: bool = True) -> bool:
        """
        Переключает на следующий трек в очереди

        Параметры:
            wait (bool): Ожидать окончания трека

        Возвращает:
            bool: True, если переключение удалось
        """
        if not self.queue or self.queue_index + 1 >= len(self.queue):
            self.stop()
            print("⏹️ Это был последний трек в очереди")
            return False
        self.queue_index += 1
        track = self.queue[self.queue_index]
        self._play_url(track['url'], track['name'])
        if wait:
            self._wait_for_end()
        return True

    def prev(self, wait: bool = True) -> bool:
        """Переключает на предыдущий трек в очереди"""
        if not self.queue or self.queue_index <= 0:
            print("⏮️ Это первый трек в очереди")
            return False
        self.queue_index -= 1
        track = self.queue[self.queue_index]
        self._play_url(track['url'], track['name'])
        if wait:
            self._wait_for_end()
        return True

    def volume(self, level: int) -> None:
        """
        Устанавливает громкость (0–100)

        Параметры:
            level (int): Уровень громкости
        """
        self.volume_level = max(0, min(100, level))
        if self.player:
            self.player.audio_set_volume(self.volume_level)
        print(f"🔊 Громкость: {self.volume_level}%")

    def volume_up(self, step: int = 10) -> None:
        """Увеличивает громкость на step"""
        self.volume(self.volume_level + step)

    def volume_down(self, step: int = 10) -> None:
        """Уменьшает громкость на step"""
        self.volume(self.volume_level - step)

    # ---------- Очередь ----------
    def add_to_queue(self, query: str) -> bool:
        """
        Добавляет трек в конец очереди

        Параметры:
            query (str): Название трека

        Возвращает:
            bool: True при успехе
        """
        url = self._get_track_url(query, use_cache=True)
        if not url:
            print(f"❌ Не найден: {query}")
            return False
        self.queue.append({'name': query, 'url': url})
        print(f"➕ В очередь добавлен: {query}")
        return True

    def show_queue(self) -> None:
        """Показывает текущую очередь в консоли"""
        if not self.queue:
            print("📭 Очередь пуста")
            return
        print(f"\n📋 ОЧЕРЕДЬ ({len(self.queue)} треков):")
        for i, track in enumerate(self.queue):
            mark = "▶️" if i == self.queue_index else "  "
            print(f"   {mark} {i+1}. {track['name']}")

    def clear_queue(self) -> None:
        """Очищает очередь"""
        self.queue = []
        self.queue_index = 0
        print("🧹 Очередь очищена")

    # ---------- Скачивание избранного (упрощённая версия) ----------
    def download_favorites(self, folder_path: Optional[str] = None, delay: float = 1.0) -> int:
        """
        💾 СКАЧИВАНИЕ ВСЕХ ТРЕКОВ ИЗ ИЗБРАННОГО

        Параметры:
            folder_path (str, optional): Папка для сохранения. По умолчанию "./YandexMusic"
            delay (float): Задержка между скачиваниями (секунды)

        Возвращает:
            int: Количество скачанных треков

        Пример:
            >>> player = Music(token="y0_...")
            >>> player.download_favorites("C:/Music", delay=1.0)
        """
        import requests
        from pathlib import Path
        
        # Папка для сохранения
        if folder_path is None:
            download_folder = Path.cwd() / "YandexMusic"
        else:
            download_folder = Path(folder_path)
        download_folder.mkdir(parents=True, exist_ok=True)
        
        # Загружаем список избранного
        print(f"📥 Загрузка избранного в {download_folder}...")
        self._load_favorites(force=True)
        
        if not self._fav_cache:
            print("❌ Избранное пусто")
            return 0
        
        total = len(self._fav_cache)
        downloaded = 0
        
        for i, item in enumerate(self._fav_cache, 1):
            track_name = item['name']
            print(f"[{i}/{total}] 📥 {track_name}")
            
            # Получаем URL трека
            url = self._get_track_url(track_name, use_cache=False)
            if not url:
                print(f"   ❌ Не найден")
                continue
            
            # Скачиваем
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Безопасное имя файла
                safe_name = track_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '_').replace('*', '_')
                file_path = download_folder / f"{safe_name}.mp3"
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ Сохранён: {file_path.name}")
                downloaded += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
            
            # Задержка
            if i < total:
                time.sleep(delay)
        
        print(f"\n✅ Скачано {downloaded} из {total} треков в {download_folder}")
        return downloaded

    def _rate_limit(self) -> None:
        """
        Внутренний метод для ограничения частоты запросов к API
        (не более 30 запросов в секунду, запас относительно лимита 50/сек)
        """
        if not hasattr(self, '_last_request_time'):
            self._last_request_time = 0
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.033:  # ~30 запросов в секунду
            time.sleep(0.033 - elapsed)
        self._last_request_time = time.time()

    # ---------- Моя волна (только избранное) ----------
    def play_my_wave(self, limit: int = 20, wait: bool = True) -> bool:
        """
        🌊 МОЯ ВОЛНА: проигрывает случайные треки из избранного (кэш 2 часа)

        Параметры:
            limit (int): Максимальное количество треков
            wait (bool): Ожидать окончания первого трека

        Возвращает:
            bool: True при успехе
        """
        try:
            print(f"🎵 Формирую «Мою волну» (до {limit} треков)…")
            self.queue = []
            self._load_favorites(force=False)
            if not self._fav_cache:
                print("❌ Избранное пусто, нечего играть.")
                return False

            # Случайная выборка
            indices = list(range(len(self._fav_cache)))
            random.shuffle(indices)
            added = 0
            used_ids = set()
            for idx in indices:
                if added >= limit:
                    break
                item = self._fav_cache[idx]
                if item['track_id'] in used_ids:
                    continue
                used_ids.add(item['track_id'])
                url = self._get_track_url(item['name'], use_cache=True)
                if url:
                    self.queue.append({'name': item['name'], 'url': url})
                    added += 1

            print(f"   → Добавлено треков из избранного: {added}")

            if not self.queue:
                print("❌ Не удалось собрать ни одного трека.")
                return False

            self.queue_index = 0
            self._play_url(self.queue[0]['url'], self.queue[0]['name'])
            print(f"✅ Готовая «Моя волна» содержит {len(self.queue)} треков (все из избранного)")
            if wait:
                self._wait_for_end()
            return True
        except Exception as e:
            print(f"❌ Ошибка в play_my_wave: {e}")
            return False

    # ---------- Избранное ----------
    def play_favorites(self, limit: int = 10, wait: bool = True) -> bool:
        """
        ❤️ ВОСПРОИЗВЕДЕНИЕ ИЗБРАННЫХ ТРЕКОВ (случайные)

        Параметры:
            limit (int): Количество треков
            wait (bool): Ожидать окончания первого трека

        Возвращает:
            bool: True при успехе
        """
        try:
            print("🎵 Загружаю избранные треки...")
            self._load_favorites(force=False)
            if not self._fav_cache:
                print("❌ Нет избранных треков.")
                return False

            sample = random.sample(self._fav_cache, min(limit, len(self._fav_cache)))
            self.queue = []
            for item in sample:
                url = self._get_track_url(item['name'], use_cache=True)
                if not url:
                    url = self._get_track_url(item['name'], use_cache=False)
                if url:
                    self.queue.append({'name': item['name'], 'url': url})

            if not self.queue:
                print("❌ Не удалось загрузить треки из избранного")
                return False

            self.queue_index = 0
            self._play_url(self.queue[0]['url'], self.queue[0]['name'])
            print(f"✅ Загружено {len(self.queue)} избранных треков")
            if wait:
                self._wait_for_end()
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def play_liked_tracks(self, limit: int = 10, wait: bool = True) -> bool:
        """Алиас для play_favorites (обратная совместимость)"""
        return self.play_favorites(limit, wait)

    # ---------- Плейлисты ----------
    def search_playlist(self, query: str, limit: int = 10, wait: bool = True) -> bool:
        """
        🔍 ПОИСК ПЛЕЙЛИСТА И ВОСПРОИЗВЕДЕНИЕ ЕГО ПЕРВЫХ ТРЕКОВ

        Параметры:
            query (str): Название плейлиста
            limit (int): Максимальное количество треков
            wait (bool): Ожидать окончания первого трека

        Возвращает:
            bool: True при успехе
        """
        try:
            print(f"🔍 Ищу плейлист: {query}")
            search = self.client.search(query)
            if not search.playlists or not search.playlists.results:
                print("❌ Плейлист не найден")
                return False

            playlist = search.playlists.results[0]
            print(f"✅ Найден плейлист: {playlist.title}")

            tracks_data = playlist.fetch_tracks()
            self.queue = []
            for item in list(tracks_data)[:limit]:
                try:
                    track = item.track if hasattr(item, 'track') else item
                    artist_name = track.artists[0].name if track.artists else "Unknown"
                    name = f"{track.title} — {artist_name}"
                    url = self._get_track_url(name, use_cache=True)
                    if url:
                        self.queue.append({'name': name, 'url': url})
                except Exception:
                    continue

            if not self.queue:
                print("❌ Не удалось загрузить треки из плейлиста")
                return False

            self.queue_index = 0
            self._play_url(self.queue[0]['url'], self.queue[0]['name'])
            print(f"✅ Загружено {len(self.queue)} треков из «{playlist.title}»")
            if wait:
                self._wait_for_end()
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def mood(self, mood_name: str, limit: int = 5, wait: bool = True) -> bool:
        """
        🎭 МУЗЫКА ПО НАСТРОЕНИЮ (ищет плейлист, при неудаче — Моя волна)

        Параметры:
            mood_name (str): Настроение ('happy', 'sad', 'energy', 'calm')
            limit (int): Количество треков
            wait (bool): Ожидать окончания первого трека

        Возвращает:
            bool: True при успехе
        """
        print(f"🎭 Включаю музыку под настроение: {mood_name}")
        result = self.search_playlist(mood_name, limit, wait)
        if not result:
            print(f"⚠️ Плейлист '{mood_name}' не загрузился, включаю Мою волну")
            result = self.play_my_wave(limit, wait)
        return result

    # ---------- Информационные методы ----------
    def is_now_playing(self) -> bool:
        """Возвращает True, если трек играет (не на паузе)"""
        return self._is_playing

    def get_current_track(self) -> Optional[str]:
        """Возвращает название текущего трека или None"""
        return self.current_track

    def get_volume(self) -> int:
        """Возвращает текущий уровень громкости (0–100)"""
        return self.volume_level

    def get_queue_length(self) -> int:
        """Возвращает количество треков в очереди"""
        return len(self.queue)

# =============================================================================
# КЛАСС Face – РАСПОЗНАВАНИЕ ЛИЦ И ЭМОЦИЙ
# =============================================================================

class Face:
    """
    🧠 РАСПОЗНАВАНИЕ ЛИЦ И ЭМОЦИЙ ЧЕРЕЗ ВЕБ-КАМЕРУ

    Позволяет определять эмоции (happy, sad, angry, etc.) и улыбку,
    а также автоматически включать музыку под настроение.

    📌 ТРЕБОВАНИЯ:
        - opencv-python
        - deepface (для эмоций)
        - веб-камера

    📌 ПРИМЕР:
        >>> emotion = Face.detect_emotion()
        >>> if emotion == 'happy':
        ...     print("Вы счастливы!")
        >>> Face.music_by_mood()
    """

    @staticmethod
    def detect_emotion() -> Optional[str]:
        """
        🎭 ОПРЕДЕЛЕНИЕ ЭМОЦИИ ПО ЛИЦУ В КАДРЕ

        Возвращает:
            str или None: 'happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral' или None
        """
        import cv2
        from deepface import DeepFace

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("❌ Не удалось получить кадр с камеры")
            return None

        try:
            result = DeepFace.analyze(img_path=frame, actions=['emotion'], enforce_detection=False, silent=True)
            return result[0]['dominant_emotion']
        except Exception as e:
            print(f"❌ Ошибка DeepFace: {e}")
            return None

    @staticmethod
    def detect_smile() -> bool:
        """
        😁 ОБНАРУЖЕНИЕ УЛЫБКИ

        Возвращает:
            bool: True, если улыбка обнаружена
        """
        import cv2

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            smiles = smile_cascade.detectMultiScale(roi, 1.8, 20)
            if len(smiles) > 0:
                return True
        return False

    @staticmethod
    def music_by_mood(music_instance: Optional['Music'] = None) -> None:
        """
        🎵 АВТОМАТИЧЕСКИЙ ЗАПУСК МУЗЫКИ ПО НАСТРОЕНИЮ

        Параметры:
            music_instance (Music, optional): Экземпляр плеера. Если не передан, создаётся новый.
        """
        emotion = Face.detect_emotion()
        if not emotion:
            print("Не удалось определить эмоцию")
            return

        mood_map = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'energy',
            'surprise': 'happy',
            'fear': 'calm',
            'neutral': 'calm'
        }
        if music_instance is None:
            music_instance = Music()
        music_instance.mood(mood_map.get(emotion, 'calm'))


# =============================================================================
# КЛАСС Auto – АВТОМАТИЗАЦИЯ КЛАВИАТУРЫ И МЫШИ
# =============================================================================

class Auto:
    """
    🖱️ АВТОМАТИЗАЦИЯ КЛАВИАТУРЫ И МЫШИ (pyautogui + keyboard)

    Все методы статические. Позволяют эмулировать нажатия клавиш, клики мыши,
    движение курсора, скроллинг, создавать скриншоты и системные уведомления.

    📌 ПРИМЕРЫ:
        >>> Auto.click(100, 200)
        >>> Auto.write("Привет!")
        >>> Auto.press('enter')
        >>> Auto.screenshot("screen.png")
    """

    # ==================== КЛАВИАТУРА ====================
    @staticmethod
    def key_down(key: str) -> None:
        """⬇️ ЗАЖАТЬ КЛАВИШУ"""
        import keyboard
        keyboard.press(key)

    @staticmethod
    def key_up(key: str) -> None:
        """⬆️ ОТПУСТИТЬ КЛАВИШУ"""
        import keyboard
        keyboard.release(key)

    @staticmethod
    def press(key: str, duration: float = 0.05) -> None:
        """⌨️ НАЖАТЬ И ОТПУСТИТЬ КЛАВИШУ"""
        import keyboard
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)

    @staticmethod
    def is_pressed(key: str) -> bool:
        """❓ ПРОВЕРИТЬ, ЗАЖАТА ЛИ КЛАВИША"""
        import keyboard
        return keyboard.is_pressed(key)

    @staticmethod
    def write(text: str, delay: float = 0.05) -> None:
        """📝 НАПЕЧАТАТЬ ТЕКСТ (С ЗАДЕРЖКОЙ МЕЖДУ СИМВОЛАМИ)"""
        import keyboard
        for ch in text:
            keyboard.write(ch)
            time.sleep(delay)

    # ==================== МЫШЬ ====================
    @staticmethod
    def mouse_down(button: str = 'left') -> None:
        """🖱️⬇️ ЗАЖАТЬ КНОПКУ МЫШИ (left/right/middle)"""
        import pyautogui
        pyautogui.mouseDown(button=button)

    @staticmethod
    def mouse_up(button: str = 'left') -> None:
        """🖱️⬆️ ОТПУСТИТЬ КНОПКУ МЫШИ"""
        import pyautogui
        pyautogui.mouseUp(button=button)

    @staticmethod
    def click(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> None:
        """🖱️ КЛИК МЫШЬЮ (можно передать координаты или кортеж)"""
        import pyautogui
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button, clicks=clicks)
        elif isinstance(x, (tuple, list)) and len(x) >= 2:
            pyautogui.click(x[0], x[1], button=button, clicks=clicks)
        elif x is None and y is None:
            pyautogui.click(button=button, clicks=clicks)
        else:
            raise ValueError("Передайте и x, и y, или кортеж (x, y), или ничего")

    @staticmethod
    def double_click(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left') -> None:
        """🖱️🖱️ ДВОЙНОЙ КЛИК"""
        Auto.click(x, y, button, clicks=2)

    @staticmethod
    def move(x: Union[int, Tuple[int, int]], y: Optional[int] = None, duration: float = 0.0) -> None:
        """➡️ ПЕРЕМЕСТИТЬ КУРСОР (плавно, если duration > 0)"""
        import pyautogui
        if isinstance(x, (tuple, list)) and len(x) >= 2:
            pyautogui.moveTo(x[0], x[1], duration=duration)
        elif y is not None:
            pyautogui.moveTo(x, y, duration=duration)
        else:
            print("⚠️ Координаты не указаны")

    @staticmethod
    def scroll(amount: int, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """🖱️🔄 ПРОКРУТКА (amount > 0 — вверх, < 0 — вниз)"""
        import pyautogui
        pyautogui.scroll(amount, x, y)

    @staticmethod
    def drag(start_x: int, start_y: int, end_x: int, end_y: int, button: str = 'left', duration: float = 0.5) -> None:
        """🖱️↔️ ПЕРЕТАСКИВАНИЕ ОБЪЕКТА"""
        import pyautogui
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)

    # ==================== ПРОЧЕЕ ====================
    @staticmethod
    def screenshot(save_path: str = "screen.png") -> None:
        """
        📸 СКРИНШОТ ВСЕГО ЭКРАНА (сохраняется в текущую рабочую папку)

        Параметры:
            save_path (str): Имя файла или путь
        """
        import pyautogui
        full = os.path.join(os.getcwd(), save_path)
        img = pyautogui.screenshot()
        img.save(full)
        print(f"📸 Скриншот сохранён: {full}")

    @staticmethod
    def notify(title: str, message: str, timeout: int = 5) -> None:
        """
        🔔 СИСТЕМНОЕ УВЕДОМЛЕНИЕ (правый нижний угол)

        Параметры:
            title (str): Заголовок
            message (str): Текст
            timeout (int): Время показа в секундах
        """
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=timeout)
        except Exception:
            print(f"⚠️ {title}: {message}")


# =============================================================================
# КЛАСС Web – БРАУЗЕР И ПОИСК
# =============================================================================

class Web:
    """
    🌐 ОТКРЫТИЕ ССЫЛОК И ПОИСК В ЯНДЕКСЕ / YOUTUBE

    Все методы статические. Открывают URL в браузере по умолчанию.

    📌 ПРИМЕРЫ:
        >>> Web.open("https://google.com")
        >>> Web.search("погода Москва")
        >>> Web.youtube("python уроки")
    """

    @staticmethod
    def open(url: str) -> None:
        """🌐 ОТКРЫТЬ URL В БРАУЗЕРЕ"""
        webbrowser.open(url)
        print(f"🌐 Открыто: {url}")

    @staticmethod
    def search(query: str) -> None:
        """🔍 ПОИСК В ЯНДЕКСЕ"""
        url = f"https://yandex.ru/search/?text={quote(query)}"
        webbrowser.open(url)
        print(f"🔍 Поиск: {query}")

    @staticmethod
    def youtube(query: str) -> None:
        """🎬 ПОИСК НА YOUTUBE"""
        url = f"https://www.youtube.com/results?search_query={quote(query)}"
        webbrowser.open(url)
        print(f"🎬 YouTube: {query}")


# =============================================================================
# КЛАСС System – СИСТЕМНЫЕ КОМАНДЫ (Windows)
# =============================================================================

class System:
    """
    💻 СИСТЕМНЫЕ КОМАНДЫ (только Windows)

    ⚠️ Будьте осторожны: shutdown и restart реально выключают / перезагружают компьютер.

    📌 ПРИМЕРЫ:
        >>> System.shutdown(10)   # выключение через 10 секунд
        >>> System.lock()         # блокировка экрана
    """

    @staticmethod
    def shutdown(delay: int = 0) -> None:
        """🔌 ВЫКЛЮЧЕНИЕ КОМПЬЮТЕРА (Windows)"""
        if delay > 0:
            print(f"⚠️ Выключение через {delay} секунд...")
            time.sleep(delay)
        os.system("shutdown /s /t 0")
        print("🔌 Выключение...")

    @staticmethod
    def restart(delay: int = 0) -> None:
        """🔄 ПЕРЕЗАГРУЗКА (Windows)"""
        if delay > 0:
            print(f"⚠️ Перезагрузка через {delay} секунд...")
            time.sleep(delay)
        os.system("shutdown /r /t 0")
        print("🔄 Перезагрузка...")

    @staticmethod
    def sleep() -> None:
        """💤 СПЯЩИЙ РЕЖИМ (Windows)"""
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        print("💤 Спящий режим")

    @staticmethod
    def lock() -> None:
        """🔒 БЛОКИРОВКА ЭКРАНА (Windows)"""
        os.system("rundll32.exe user32.dll,LockWorkStation")
        print("🔒 Экран заблокирован")


# =============================================================================
# КЛАСС Info – ИНФОРМАЦИЯ О СИСТЕМЕ
# =============================================================================

class Info:
    """
    ℹ️ ИНФОРМАЦИЯ О СИСТЕМЕ (ОС, батарея, CPU, RAM)

    Все методы статические. Для работы некоторых требуется psutil.

    📌 ПРИМЕРЫ:
        >>> battery, plugged = Info.battery()
        >>> cpu_load = Info.cpu()
        >>> used, total = Info.ram()
    """

    @staticmethod
    def battery() -> Tuple[Optional[float], Optional[bool]]:
        """
        🔋 УРОВЕНЬ ЗАРЯДА БАТАРЕИ И СТАТУС ПОДКЛЮЧЕНИЯ К СЕТИ

        Возвращает:
            tuple: (процент заряда, подключена ли зарядка) или (None, None) при ошибке
        """
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent, battery.power_plugged
        except Exception:
            pass
        return None, None

    @staticmethod
    def os() -> str:
        """🖥️ ТИП ОПЕРАЦИОННОЙ СИСТЕМЫ ('win32', 'linux', 'darwin')"""
        return sys.platform

    @staticmethod
    def cpu() -> Optional[float]:
        """🧠 ЗАГРУЗКА ПРОЦЕССОРА В ПРОЦЕНТАХ (измеряется 1 секунду)"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except Exception:
            return None

    @staticmethod
    def ram() -> Tuple[Optional[int], Optional[int]]:
        """
        💾 ИСПОЛЬЗОВАНИЕ ОПЕРАТИВНОЙ ПАМЯТИ (МБ)

        Возвращает:
            tuple: (использовано МБ, всего МБ) или (None, None)
        """
        try:
            import psutil
            mem = psutil.virtual_memory()
            return mem.used // (1024 * 1024), mem.total // (1024 * 1024)
        except Exception:
            return None, None


# =============================================================================
# КЛАСС ThreadManager – УПРАВЛЕНИЕ ПОТОКАМИ (С ПОДДЕРЖКОЙ STOP_EVENT)
# =============================================================================

class ThreadManager:
    """
    🧵 УПРАВЛЕНИЕ ФОНОВЫМИ ПОТОКАМИ

    Позволяет запускать функции в отдельных потоках, останавливать их по сигналу
    (если функция принимает параметр stop_event) и отслеживать состояние.

    📌 ПРИМЕР:
        >>> def worker(stop_event):
        ...     while not stop_event.is_set():
        ...         print("Работаю...")
        ...         time.sleep(1)
        >>> tm = ThreadManager()
        >>> tid = tm.start(worker)
        >>> time.sleep(5)
        >>> tm.stop(tid)
    """

    def __init__(self):
        self.threads = {}
        self.stop_events = {}

    def start(self, target: Callable, args: tuple = (), name: Optional[str] = None, daemon: bool = True) -> str:
        """
        ▶️ ЗАПУСК ПОТОКА

        Параметры:
            target (callable): Функция, которая будет выполнена в потоке.
            args (tuple): Кортеж аргументов для target.
            name (str, optional): Имя потока.
            daemon (bool): Фоновый поток (завершится при выходе из программы).

        Возвращает:
            str: ID потока (имя).

        Примечание:
            Если target принимает параметр `stop_event`, он будет передан автоматически.
            Это позволяет организовать мягкую остановку потока.
        """
        stop_event = threading.Event()
        thread_id = name or f"Thread_{len(self.threads) + 1}"

        # Проверяем сигнатуру функции
        sig = inspect.signature(target)
        accepts_stop = any(param.name == 'stop_event' for param in sig.parameters.values())

        def wrapper():
            if accepts_stop:
                target(*args, stop_event=stop_event)
            else:
                target(*args)

        thread = threading.Thread(target=wrapper, name=thread_id, daemon=daemon)
        self.threads[thread_id] = thread
        self.stop_events[thread_id] = stop_event
        thread.start()
        print(f"✅ Поток '{thread_id}' запущен")
        return thread_id

    def stop(self, thread_id: str) -> bool:
        """
        ⏹️ ОСТАНОВИТЬ ПОТОК (установкой флага stop_event)

        Параметры:
            thread_id (str): ID потока

        Возвращает:
            bool: True, если поток найден и остановлен, иначе False
        """
        if thread_id in self.stop_events:
            self.stop_events[thread_id].set()
            print(f"⏹️ Поток '{thread_id}' остановлен")
            return True
        print(f"❌ Поток '{thread_id}' не найден")
        return False

    def stop_all(self) -> None:
        """⏹️⏹️ ОСТАНОВИТЬ ВСЕ ПОТОКИ"""
        for tid in self.stop_events:
            self.stop_events[tid].set()
        print(f"⏹️ Остановлено {len(self.stop_events)} потоков")

    def is_alive(self, thread_id: str) -> bool:
        """❓ ПРОВЕРИТЬ, АКТИВЕН ЛИ ПОТОК"""
        return thread_id in self.threads and self.threads[thread_id].is_alive()

    def list_threads(self) -> List[str]:
        """📋 СПИСОК АКТИВНЫХ ПОТОКОВ (их имена)"""
        return [name for name, t in self.threads.items() if t.is_alive()]

    def active_count(self) -> int:
        """🔢 ОБЩЕЕ КОЛИЧЕСТВО АКТИВНЫХ ПОТОКОВ В ПРОГРАММЕ"""
        return threading.active_count()

# =============================================================================
# КЛАСС ScreenReader – РАСПОЗНАВАНИЕ ЭКРАНА
# =============================================================================

class ScreenReader:
    """
    🖥️ РАСПОЗНАВАНИЕ ЭКРАНА (OCR, поиск изображений, цвета)

    Требует установки: opencv-python, pillow, easyocr, mss, numpy.

    📌 ПРИМЕРЫ:
        >>> pos = ScreenReader.find_image("button.png")
        >>> if pos: Auto.click(pos)
        >>> result = ScreenReader.find_text_coordinates("Принять")
        >>> if result['found']: Auto.click(result['x'], result['y'])
    """
    _ocr_reader = None  # Кэш EasyOCR

    @classmethod
    def _get_ocr_reader(cls, languages):
        if cls._ocr_reader is None:
            import easyocr
            cls._ocr_reader = easyocr.Reader(languages)
        return cls._ocr_reader

    @staticmethod
    def find_image(template_path: str, confidence: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        🔍 ПОИСК ИЗОБРАЖЕНИЯ НА ЭКРАНЕ

        Параметры:
            template_path (str): Путь к изображению-шаблону
            confidence (float): Порог совпадения (0.7–0.95)
            region (tuple, optional): (x, y, width, height) — область поиска

        Возвращает:
            tuple (x, y) или None: Координаты центра найденного изображения
        """
        import cv2
        import numpy as np
        import pyautogui

        screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)
        if template is None:
            print(f"❌ Не удалось загрузить {template_path}")
            return None

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            if region:
                center_x += region[0]
                center_y += region[1]
            print(f"✅ Изображение найдено в ({center_x}, {center_y}) (совпадение: {max_val:.2f})")
            return (center_x, center_y)
        else:
            print(f"❌ Изображение не найдено (совпадение: {max_val:.2f})")
            return None

    @staticmethod
    def find_color(target_color: Tuple[int, int, int], tolerance: int = 30, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        🎨 ПОИСК ПИКСЕЛЯ ЗАДАННОГО ЦВЕТА НА ЭКРАНЕ

        Параметры:
            target_color (tuple): (R, G, B)
            tolerance (int): Допустимое отклонение
            region (tuple, optional): Область поиска

        Возвращает:
            tuple (x, y) или None
        """
        import pyautogui
        import numpy as np
        screenshot = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()
        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0
        img = np.array(screenshot)
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                pixel = img[y, x][:3]
                if all(abs(pixel[i] - target_color[i]) <= tolerance for i in range(3)):
                    result_x = x + offset_x
                    result_y = y + offset_y
                    print(f"✅ Цвет найден в ({result_x}, {result_y})")
                    return (result_x, result_y)
        print(f"❌ Цвет {target_color} не найден")
        return None

    @staticmethod
    def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
        """
        🎨 ПОЛУЧИТЬ ЦВЕТ ПИКСЕЛЯ В КООРДИНАТАХ

        Возвращает:
            tuple: (R, G, B)
        """
        import pyautogui
        pixel = pyautogui.pixel(x, y)
        print(f"🖱️ Цвет в ({x}, {y}): {pixel}")
        return pixel

    @staticmethod
    def find_text_coordinates(search_text: str, languages: List[str] = ['en', 'ru'],
                              monitor_index: int = 1, confidence_threshold: float = 0.5,
                              partial_match: bool = True) -> Dict[str, Any]:
        """
        📖 ПОИСК ТЕКСТА НА ЭКРАНЕ С ПОМОЩЬЮ OCR (EASYOCR)

        Параметры:
            search_text (str): Искомый текст
            languages (list): Языки ('en', 'ru')
            monitor_index (int): Индекс монитора
            confidence_threshold (float): Минимальная уверенность (0..1)
            partial_match (bool): Искать частичное совпадение

        Возвращает:
            dict: {'found': bool, 'x': int, 'y': int, 'confidence': float, ...}
        """
        import mss
        import numpy as np
        from PIL import Image

        reader = ScreenReader._get_ocr_reader(languages)
        with mss.mss() as sct:
            monitor = sct.monitors[monitor_index]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img_array = np.array(img)

        results = reader.readtext(img_array, detail=1, text_threshold=0.7)
        best_match = None
        for bbox, text, confidence in results:
            text_lower = text.lower()
            if partial_match:
                match = search_text in text_lower
            else:
                match = search_text == text_lower
            if match and confidence >= confidence_threshold:
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                center_x = int(sum(x_coords) / len(x_coords))
                center_y = int(sum(y_coords) / len(y_coords))
                if best_match is None or confidence > best_match['confidence']:
                    best_match = {
                        'found': True,
                        'x': center_x,
                        'y': center_y,
                        'confidence': confidence,
                        'matched_text': text,
                        'bbox': bbox
                    }
        if best_match:
            return best_match
        return {'found': False, 'error': f'Текст "{search_text}" не найден'}

    @staticmethod
    def wait_for_image(template_path: str, timeout: int = 30, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """⏳ ЖДАТЬ ПОЯВЛЕНИЯ ИЗОБРАЖЕНИЯ НА ЭКРАНЕ"""
        start = time.time()
        while time.time() - start < timeout:
            pos = ScreenReader.find_image(template_path, confidence)
            if pos:
                print(f"✅ Изображение появилось через {time.time() - start:.1f} сек")
                return pos
            time.sleep(0.5)
        print(f"❌ Изображение не появилось за {timeout} сек")
        return None

    @staticmethod
    def highlight_image(template_path: str, confidence: float = 0.8,
                        duration: int = 2000, color: str = 'lime', thickness: int = 4) -> Optional[Tuple[int, int]]:
        """
        🟩 ВЫДЕЛИТЬ НАЙДЕННОЕ ИЗОБРАЖЕНИЕ РАМКОЙ

        Параметры:
            template_path: Путь к шаблону
            confidence: Порог совпадения
            duration: Время показа рамки (мс)
            color: Цвет рамки
            thickness: Толщина линии
        """
        import cv2
        import numpy as np
        import pyautogui
        import tkinter as tk

        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path)
        if template is None:
            print(f"❌ Не найден файл: {template_path}")
            return None

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < confidence:
            print(f"❌ Изображение не найдено (совпадение {max_val:.2f})")
            return None

        h, w = template.shape[:2]
        x, y = max_loc
        print(f"✅ Найдено: ({x}, {y}) размер {w}x{h} (совпадение {max_val:.2f})")

        root = tk.Tk()
        root.overrideredirect(True)
        root.lift()
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-transparentcolor", "white")
        canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0, bg='white')
        canvas.pack()
        canvas.create_rectangle(0, 0, w-1, h-1, outline=color, width=thickness)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.after(duration, root.destroy)
        root.mainloop()
        return (x, y)


# =============================================================================
# КЛАСС Clipboard – БУФЕР ОБМЕНА
# =============================================================================

class Clipboard:
    """
    📋 РАБОТА С БУФЕРОМ ОБМЕНА (копирование / вставка)

    Требуется pyperclip.

    📌 ПРИМЕР:
        >>> Clipboard.copy("Привет!")
        >>> text = Clipboard.paste()
    """

    @staticmethod
    def copy(text: str) -> None:
        """📋📤 КОПИРОВАТЬ ТЕКСТ В БУФЕР"""
        import pyperclip
        pyperclip.copy(text)

    @staticmethod
    def paste() -> str:
        """📋📥 ВСТАВИТЬ ТЕКСТ ИЗ БУФЕРА"""
        import pyperclip
        return pyperclip.paste()


# =============================================================================
# КЛАСС MathHelper – МАТЕМАТИЧЕСКИЕ УТИЛИТЫ
# =============================================================================

class MathHelper:
    """
    🧮 ПРОСТЫЕ МАТЕМАТИЧЕСКИЕ ОПЕРАЦИИ (факториал, среднее, медиана, перевод систем)

    📌 ПРИМЕРЫ:
        >>> MathHelper.factorial(5)          # 120
        >>> MathHelper.mean([1,2,3,4,5])      # 3.0
        >>> MathHelper.median([1,2,3,4])      # 2.5
        >>> MathHelper.to_binary(42)          # '101010'
        >>> MathHelper.school_round(3.5)      # 4.0
    """

    @staticmethod
    def factorial(n: int) -> int:
        return math.factorial(n)

    @staticmethod
    def mean(numbers: List[float]) -> float:
        return sum(numbers) / len(numbers)

    @staticmethod
    def median(numbers: List[float]) -> float:
        return statistics.median(numbers)

    @staticmethod
    def to_binary(n: int) -> str:
        return bin(n)[2:]

    @staticmethod
    def to_hex(n: int) -> str:
        return hex(n)[2:]

    @staticmethod
    def school_round(number: float, digits: int = 0) -> float:
        """Школьное округление (3.5 → 4)"""
        multiplier = 10 ** digits
        return (number * multiplier + 0.5 * (1 if number >= 0 else -1)) // 1 * (1 / multiplier)


# =============================================================================
# КЛАСС FileUtils – ПРОСТЫЕ ОПЕРАЦИИ С ТЕКСТОВЫМИ ФАЙЛАМИ
# =============================================================================

class FileUtils:
    """
    📄 ЧТЕНИЕ, ЗАПИСЬ И ПОДСЧЁТ СТРОК В ТЕКСТОВЫХ ФАЙЛАХ

    📌 ПРИМЕРЫ:
        >>> content = FileUtils.read_text("notes.txt")
        >>> FileUtils.write_text("hello.txt", "Привет!")
        >>> lines = FileUtils.count_lines("log.txt")
    """

    @staticmethod
    def read_text(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_text(path: str, content: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def count_lines(path: str) -> int:
        with open(path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)

# =============================================================================
# КЛАСС ImageUtils – РАБОТА С ИЗОБРАЖЕНИЯМИ (Pillow) - продолжение
# =============================================================================

class ImageUtils:
    """
    🖼️ ИЗМЕНЕНИЕ РАЗМЕРА, ОБРЕЗКА, ПОВОРОТ ИЗОБРАЖЕНИЙ

    Требует Pillow.

    📌 ПРИМЕРЫ:
        >>> ImageUtils.resize("input.jpg", "small.jpg", 100, 100)
        >>> ImageUtils.crop("photo.jpg", "face.jpg", 100, 50, 300, 300)
        >>> ImageUtils.rotate("photo.jpg", "rotated.jpg", 90)
    """

    @staticmethod
    def resize(input_path: str, output_path: str, width: int, height: int) -> None:
        """
        📏 ИЗМЕНЕНИЕ РАЗМЕРА ИЗОБРАЖЕНИЯ

        Параметры:
            input_path (str): Путь к исходному изображению
            output_path (str): Путь для сохранения результата
            width (int): Новая ширина в пикселях
            height (int): Новая высота в пикселях

        Пример:
            >>> ImageUtils.resize("photo.jpg", "photo_small.jpg", 200, 150)
        """
        from PIL import Image
        img = Image.open(input_path)
        img = img.resize((width, height))
        img.save(output_path)
        print(f"✅ Изображение изменено: {output_path} ({width}x{height})")

    @staticmethod
    def crop(input_path: str, output_path: str, left: int, top: int, right: int, bottom: int) -> None:
        """
        ✂️ ОБРЕЗКА ИЗОБРАЖЕНИЯ

        Параметры:
            input_path (str): Путь к исходному изображению
            output_path (str): Путь для сохранения результата
            left (int): Левая граница обрезки
            top (int): Верхняя граница обрезки
            right (int): Правая граница обрезки
            bottom (int): Нижняя граница обрезки

        Пример:
            >>> ImageUtils.crop("photo.jpg", "face.jpg", 100, 50, 300, 300)
        """
        from PIL import Image
        img = Image.open(input_path)
        cropped = img.crop((left, top, right, bottom))
        cropped.save(output_path)
        print(f"✅ Изображение обрезано: {output_path}")

    @staticmethod
    def rotate(input_path: str, output_path: str, degrees: int) -> None:
        """
        🔄 ПОВОРОТ ИЗОБРАЖЕНИЯ

        Параметры:
            input_path (str): Путь к исходному изображению
            output_path (str): Путь для сохранения результата
            degrees (int): Угол поворота в градусах

        Пример:
            >>> ImageUtils.rotate("photo.jpg", "photo_90.jpg", 90)
        """
        from PIL import Image
        img = Image.open(input_path)
        rotated = img.rotate(degrees, expand=True)
        rotated.save(output_path)
        print(f"✅ Изображение повёрнуто на {degrees}°: {output_path}")


# =============================================================================
# КЛАСС PDFUtils – ИЗВЛЕЧЕНИЕ ТЕКСТА ИЗ PDF
# =============================================================================

class PDFUtils:
    """
    📑 ИЗВЛЕЧЕНИЕ ТЕКСТА ИЗ PDF-ФАЙЛОВ (PyPDF2)

    Требует установки: pip install PyPDF2

    📌 ПРИМЕР:
        >>> text = PDFUtils.extract_text("document.pdf")
        >>> print(text[:500])  # первые 500 символов
    """

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        📄 ИЗВЛЕЧЕНИЕ ВСЕГО ТЕКСТА ИЗ PDF-ФАЙЛА

        Параметры:
            pdf_path (str): Путь к PDF-файлу

        Возвращает:
            str: Извлечённый текст (страницы разделены символами новой строки)

        Пример:
            >>> text = PDFUtils.extract_text("report.pdf")
            >>> print(f"В документе {len(text)} символов")

        Примечание:
            Не все PDF-файлы содержат извлекаемый текст (отсканированные страницы не распознаются).
        """
        import PyPDF2
        text_parts = []
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    else:
                        print(f"⚠️ Страница {page_num} не содержит извлекаемого текста")
            result = '\n'.join(text_parts)
            print(f"✅ Извлечено {len(result)} символов из {len(reader.pages)} страниц")
            return result
        except Exception as e:
            print(f"❌ Ошибка извлечения текста из PDF: {e}")
            return ""


# =============================================================================
# КЛАСС PasswordGen – ГЕНЕРАТОР ПАРОЛЕЙ
# =============================================================================

class PasswordGen:
    """
    🔐 ГЕНЕРАЦИЯ СЛУЧАЙНЫХ ПАРОЛЕЙ

    Позволяет генерировать надёжные пароли с настраиваемой длиной и сложностью.

    📌 ПРИМЕРЫ:
        >>> pwd1 = PasswordGen.generate()               # 12 символов, цифры и спецсимволы
        >>> pwd2 = PasswordGen.generate(16)             # 16 символов
        >>> pwd3 = PasswordGen.generate(8, False)       # только буквы, длина 8
        >>> pwd4 = PasswordGen.generate(10, True, False) # буквы и цифры, без спецсимволов
    """

    @staticmethod
    def generate(length: int = 12, use_digits: bool = True, use_special: bool = True) -> str:
        """
        🔑 ГЕНЕРАЦИЯ СЛУЧАЙНОГО ПАРОЛЯ

        Параметры:
            length (int): Длина пароля (по умолчанию 12)
            use_digits (bool): Включать ли цифры 0-9 (по умолчанию True)
            use_special (bool): Включать ли спецсимволы !@#$%^&* (по умолчанию True)

        Возвращает:
            str: Сгенерированный пароль

        Пример:
            >>> pwd = PasswordGen.generate(16, True, True)
            >>> print(pwd)  # "aB3$xK9@mP2qL8#n"
        """
        chars = string.ascii_letters
        if use_digits:
            chars += string.digits
        if use_special:
            chars += "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(length))
        print(f"🔐 Сгенерирован пароль длиной {length} символов")
        return password


# =============================================================================
# КЛАСС UnitConverter – КОНВЕРТАЦИЯ ЕДИНИЦ ИЗМЕРЕНИЯ
# =============================================================================

class UnitConverter:
    """
    📏 КОНВЕРТАЦИЯ ТЕМПЕРАТУРЫ, РАССТОЯНИЯ, ВЕСА

    Все методы статические. Поддерживает преобразование между Цельсием/Фаренгейтом,
    километрами/милями и килограммами/фунтами.

    📌 ПРИМЕРЫ:
        >>> UnitConverter.celsius_to_fahrenheit(0)   # 32.0
        >>> UnitConverter.km_to_miles(10)            # 6.21371
        >>> UnitConverter.kg_to_lbs(5)               # 11.0231
    """

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """
        🌡️ КОНВЕРТАЦИЯ: ЦЕЛЬСИЙ → ФАРЕНГЕЙТ

        Формула: °F = °C × 9/5 + 32

        Параметры:
            celsius (float): Температура в градусах Цельсия

        Возвращает:
            float: Температура в градусах Фаренгейта

        Пример:
            >>> UnitConverter.celsius_to_fahrenheit(100)  # 212.0 (кипение воды)
            >>> UnitConverter.celsius_to_fahrenheit(37)   # 98.6 (температура тела)
        """
        return celsius * 9/5 + 32

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """
        🌡️ КОНВЕРТАЦИЯ: ФАРЕНГЕЙТ → ЦЕЛЬСИЙ

        Формула: °C = (°F - 32) × 5/9

        Параметры:
            fahrenheit (float): Температура в градусах Фаренгейта

        Возвращает:
            float: Температура в градусах Цельсия

        Пример:
            >>> UnitConverter.fahrenheit_to_celsius(32)   # 0.0 (замерзание воды)
            >>> UnitConverter.fahrenheit_to_celsius(212)  # 100.0 (кипение воды)
        """
        return (fahrenheit - 32) * 5/9

    @staticmethod
    def km_to_miles(km: float) -> float:
        """
        🛣️ КОНВЕРТАЦИЯ: КИЛОМЕТРЫ → МИЛИ

        1 километр = 0.621371 мили

        Параметры:
            km (float): Расстояние в километрах

        Возвращает:
            float: Расстояние в милях

        Пример:
            >>> UnitConverter.km_to_miles(10)   # 6.21371
            >>> UnitConverter.km_to_miles(42.195)  # 26.218 (марафон)
        """
        return km * 0.621371

    @staticmethod
    def miles_to_km(miles: float) -> float:
        """
        🛣️ КОНВЕРТАЦИЯ: МИЛИ → КИЛОМЕТРЫ

        1 миля = 1.60934 километра

        Параметры:
            miles (float): Расстояние в милях

        Возвращает:
            float: Расстояние в километрах

        Пример:
            >>> UnitConverter.miles_to_km(10)   # 16.0934
        """
        return miles / 0.621371

    @staticmethod
    def kg_to_lbs(kg: float) -> float:
        """
        ⚖️ КОНВЕРТАЦИЯ: КИЛОГРАММЫ → ФУНТЫ

        1 килограмм = 2.20462 фунта

        Параметры:
            kg (float): Вес в килограммах

        Возвращает:
            float: Вес в фунтах

        Пример:
            >>> UnitConverter.kg_to_lbs(5)    # 11.0231
            >>> UnitConverter.kg_to_lbs(70)   # 154.3234
        """
        return kg * 2.20462

    @staticmethod
    def lbs_to_kg(lbs: float) -> float:
        """
        ⚖️ КОНВЕРТАЦИЯ: ФУНТЫ → КИЛОГРАММЫ

        1 фунт = 0.453592 килограмма

        Параметры:
            lbs (float): Вес в фунтах

        Возвращает:
            float: Вес в килограммах

        Пример:
            >>> UnitConverter.lbs_to_kg(10)   # 4.5359
        """
        return lbs / 2.20462

# =============================================================================
# КЛАСС ImportManager – УПРОЩЁННАЯ РАБОТА С ИМПОРТАМИ
# =============================================================================

class ImportManager:
    """
    📦 УПРАВЛЕНИЕ ИМПОРТАМИ С ПОДДЕРЖКОЙ АБСОЛЮТНЫХ ПУТЕЙ

    Предоставляет статические методы для:
        - Добавления каталогов в sys.path
        - Импорта модулей по полному пути к файлу
        - Получения абсолютного пути относительно вызывающего скрипта
        - Временного добавления путей (контекстный менеджер)

    📌 ПРИМЕРЫ:
        >>> # Добавить папку в sys.path
        >>> ImportManager.add_path("C:/my_libs")
        >>> 
        >>> # Импортировать модуль из произвольного файла
        >>> my_module = ImportManager.import_module("C:/project/utils.py")
        >>> 
        >>> # Получить абсолютный путь относительно текущего скрипта
        >>> abs_path = ImportManager.get_absolute_path("data/config.json")
        >>> 
        >>> # Временно добавить путь
        >>> with ImportManager.temp_path("C:/temp_libs"):
        ...     import temp_module
    """

    _original_path = None

    @staticmethod
    def add_path(path: str) -> None:
        """
        ➕ ДОБАВЛЯЕТ КАТАЛОГ В sys.path (если его там ещё нет)

        Параметры:
            path (str): Путь к каталогу (абсолютный или относительный)
        """
        abs_path = os.path.abspath(path)
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            print(f"📂 Добавлен путь в sys.path: {abs_path}")

    @staticmethod
    def remove_path(path: str) -> None:
        """
        ➖ УДАЛЯЕТ КАТАЛОГ ИЗ sys.path

        Параметры:
            path (str): Путь к каталогу
        """
        abs_path = os.path.abspath(path)
        if abs_path in sys.path:
            sys.path.remove(abs_path)
            print(f"🗑️ Удалён путь из sys.path: {abs_path}")

    @staticmethod
    def import_module(file_path: str, module_name: Optional[str] = None):
        """
        📥 ИМПОРТИРУЕТ МОДУЛЬ ПО ПОЛНОМУ ПУТИ К ФАЙЛУ

        Параметры:
            file_path (str): Полный путь к .py файлу
            module_name (str, optional): Имя модуля (если не указано, берётся из имени файла)

        Возвращает:
            module: Загруженный модуль

        Пример:
            >>> utils = ImportManager.import_module("C:/project/utils.py")
            >>> utils.some_function()
        """
        import importlib.util
        file_path = os.path.abspath(file_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        if module_name is None:
            module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Не удалось создать spec для {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Добавляем модуль в sys.modules, чтобы он был доступен по имени
        sys.modules[module_name] = module
        print(f"✅ Импортирован модуль: {module_name} из {file_path}")
        return module

    @staticmethod
    def get_absolute_path(relative_path: str, stack_level: int = 1) -> str:
        """
        📂 ВОЗВРАЩАЕТ АБСОЛЮТНЫЙ ПУТЬ ОТНОСИТЕЛЬНО ВЫЗЫВАЮЩЕГО СКРИПТА

        Параметры:
            relative_path (str): Относительный путь (например, "data/config.json")
            stack_level (int): Уровень в стеке вызовов (1 — вызывающий скрипт, 2 — его вызывающий и т.д.)

        Возвращает:
            str: Абсолютный путь

        Пример:
            # В файле my_script.py:
            >>> config_path = ImportManager.get_absolute_path("config.json")
            >>> print(config_path)  # C:/my_project/config.json
        """
        # Получаем файл вызывающего скрипта
        frame = inspect.stack()[stack_level]
        caller_file = frame.filename
        caller_dir = os.path.dirname(os.path.abspath(caller_file))
        return os.path.join(caller_dir, relative_path)

    @staticmethod
    def get_caller_dir(stack_level: int = 1) -> str:
        """
        📁 ВОЗВРАЩАЕТ ПАПКУ ВЫЗЫВАЮЩЕГО СКРИПТА

        Параметры:
            stack_level (int): Уровень в стеке вызовов

        Возвращает:
            str: Путь к папке вызывающего скрипта
        """
        frame = inspect.stack()[stack_level]
        caller_file = frame.filename
        return os.path.dirname(os.path.abspath(caller_file))

    @staticmethod
    def temp_path(path: str):
        """
        ⏳ КОНТЕКСТНЫЙ МЕНЕДЖЕР ДЛЯ ВРЕМЕННОГО ДОБАВЛЕНИЯ ПУТИ В sys.path

        Параметры:
            path (str): Путь для временного добавления

        Пример:
            >>> with ImportManager.temp_path("C:/temp_libs"):
            ...     import temp_module
        """
        class TempPathManager:
            def __enter__(self):
                ImportManager.add_path(path)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                ImportManager.remove_path(path)

        return TempPathManager()

    @staticmethod
    def import_from_folder(folder_path: str, module_name: str):
        """
        📁 ИМПОРТ:ИРУЕТ МОДУЛЬ ИЗ УКАЗАННОЙ ПАПКИ (без добавления в sys.path)

        Параметры
            folder_path (str): Путь к папке с модулем
            module_name (str): Имя модуля (без .py)

        Возвращает:
            module: Загруженный модуль

        Пример:
            >>> my_mod = ImportManager.import_from_folder("C:/my_package", "mymodule")
        """
        file_path = os.path.join(folder_path, f"{module_name}.py")
        return ImportManager.import_module(file_path, module_name)

    @staticmethod
    def import_relative(relative_path: str, base_file: Optional[str] = None):
        """
        📥 ИМПОРТ МОДУЛЯ ОТНОСИТЕЛЬНО ЗАДАННОГО ФАЙЛА (или вызывающего скрипта)

        Параметры:
            relative_path (str): Путь относительно base_file (или вызывающего скрипта)
            base_file (str, optional): Базовый файл (если не указан, используется вызывающий скрипт)

        Возвращает:
            module: Загруженный модуль

        Пример:
            # В my_script.py:
            >>> utils = ImportManager.import_relative("../../utils/helper.py")
        """
        if base_file is None:
            base_file = inspect.stack()[1].filename
        base_dir = os.path.dirname(os.path.abspath(base_file))
        abs_path = os.path.normpath(os.path.join(base_dir, relative_path))
        return ImportManager.import_module(abs_path)


# =============================================================================
# ТОЧКА ВХОДА ПРИ ЗАПУСКЕ ФАЙЛА НАПРЯМУЮ
# =============================================================================

if __name__ == "__main__":
    """
    Блок для тестирования модуля при его прямом запуске.
    При импорте модуля этот код не выполняется.
    """
    print("=" * 70)
    print("📦 МОДУЛЬ HELP_MANAGER v1.1.0")
    print("=" * 70)
    print("✅ Модуль успешно загружен!")
    print()
    print("📌 БЫСТРЫЕ ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:")
    print()
    print("  # Голос и звук")
    print("  Manager.say('Привет, мир!')")
    print()
    print("  # Погода")
    print("  weather = Manager.get_weather('Москва')")
    print("  print(weather['Температура'])")
    print()
    print("  # Музыка")
    print("  player = Music(token='your_token')")
    print("  player.play('Imagine Dragons')")
    print()
    print("  # Автоматизация")
    print("  Auto.click(500, 300)")
    print("  Auto.screenshot('screen.png')")
    print()
    print("  # Консоль")
    print("  Console.success('Операция выполнена!')")
    print("  Console.progress_bar(100, 'Загрузка')")
    print()
    print("  # База данных")
    print("  db = BazaDB('test.db')")
    print("  db.create_table('users', ['name', 'age'])")
    print("  db.insert('users', {'name': 'Юсуф', 'age': '12'})")
    print()
    print("  # ИИ (GigaChat)")
    print("  ai = GigaChat(client_id='...', client_secret='...')")
    print("  answer = ai.chat('Расскажи шутку')")
    print()
    print("  # Импорты")
    print("  ImportManager.add_path('C:/my_libs')")
    print("  my_module = ImportManager.import_module('C:/project/utils.py')")
    print("  with ImportManager.temp_path('C:/temp'):")
    print("      import temp_module")
    print()
    print("=" * 70)
    print("📖 Подробная документация: https://pypi.org/project/pycraft-tools/")
    print("=" * 70) 