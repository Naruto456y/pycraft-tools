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
            api_key = "28c9d95c5e0b423d23e81c1d43c10cf0"

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

class GigaChat:
    """
    🤖 ИНТЕГРАЦИЯ С GigaChat (СБЕР) ДЛЯ ОБЩЕНИЯ И ОЧИСТКИ РЕЧИ

    Класс позволяет отправлять запросы к нейросети GigaChat, а также
    автоматически исправлять распознанную речь (убирать заикания, слова-паразиты).

    📌 ПРИМЕР:
        >>> ai = GigaChat(client_id="your_id", client_secret="your_secret")
        >>> answer = ai.chat("Как дела?")
        >>> cleaned = ai.clean_speech("я э-э-э хочу пиццу")

    🎯 ОСНОВНЫЕ МЕТОДЫ:
        - chat(): общение с ИИ
        - clean_speech(): очистка речи от шумов и повторов
    """

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, verify_ssl: bool = True):
        """
        Инициализация клиента GigaChat.

        Параметры:
            client_id (str, optional): ID клиента из кабинета разработчика Сбера.
                                       По умолчанию берётся из переменной окружения GIGACHAT_CLIENT_ID.
            client_secret (str, optional): Секрет клиента.
                                           По умолчанию из переменной окружения GIGACHAT_CLIENT_SECRET.
            verify_ssl (bool): Проверять SSL-сертификаты (True — безопасно, False — только для отладки).

        Исключения:
            ValueError: Если client_id или client_secret не указаны и не найдены в окружении.
        """
        self.client_id = client_id or os.environ.get("GIGACHAT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("GIGACHAT_CLIENT_SECRET")
        self.verify_ssl = verify_ssl
        self._token = None

        if not self.client_id or not self.client_secret:
            raise ValueError("Токены не найдены. Передайте client_id/client_secret или задайте переменные окружения GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET.")

    def _get_token(self) -> None:
        """Получает токен доступа к API GigaChat (внутренний метод)."""
        import base64
        import uuid
        from urllib.parse import urlencode
        import requests
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded}",
            "RqUID": str(uuid.uuid4()),
        }
        data = {"scope": "GIGACHAT_API_PERS"}

        resp = requests.post(url, headers=headers, data=urlencode(data),
                             verify=self.verify_ssl, timeout=30)
        if resp.status_code == 200:
            self._token = resp.json().get("access_token")
        else:
            raise Exception(f"Ошибка получения токена: {resp.status_code} - {resp.text}")

    def chat(self, user_text: str, system_text: str = "", temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        💬 ОТПРАВКА СООБЩЕНИЯ НЕЙРОСЕТИ И ПОЛУЧЕНИЕ ОТВЕТА

        Параметры:
            user_text (str): Текст пользователя
            system_text (str): Системный промпт (инструкция для модели)
            temperature (float): Креативность (0.0 — точный, 1.0 — творческий)
            max_tokens (int): Максимальная длина ответа в токенах

        Возвращает:
            str: Ответ нейросети

        Пример:
            >>> ai = GigaChat()
            >>> reply = ai.chat("Напиши стих про Python", temperature=0.8)
            >>> print(reply)
        """
        import requests
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if not self._token:
            self._get_token()

        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": user_text})

        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}"
        }
        payload = {
            "model": "GigaChat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        resp = requests.post(url, headers=headers, json=payload,
                             verify=self.verify_ssl, timeout=30)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"GigaChat API error {resp.status_code}: {resp.text}")

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
            max_tokens=200
        )


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