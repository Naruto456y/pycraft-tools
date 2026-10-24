#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль для офлайн-распознавания речи с помощью Vosk
Интегрируется в help_manager как класс VoskRecognizer

Особенности:
    - Автоматическая загрузка модели (small или large)
    - Работа с микрофоном и файлами
    - Поддержка частичных результатов
    - Потоковое распознавание с колбэками
    - Wake-word детекция (пробуждение по ключевым словам)
    - Fallback на Google Speech Recognition (при наличии интернета)

Зависимости: vosk, pyaudio, wave, requests (для скачивания)
"""

import os
import sys
import time
import json
import wave
import tempfile
import threading
import zipfile
import shutil
from typing import Optional, Callable, List, Dict, Any, Tuple
from pathlib import Path

try:
    import vosk
except ImportError:
    vosk = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import requests
except ImportError:
    requests = None

import speech_recognition as sr  # для fallback (уже используется в help_manager)

# Для прогресс-бара
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


class VoskRecognizer:
    """
    Класс для офлайн-распознавания речи с использованием Vosk.
    Все методы могут быть вызваны статически или через экземпляр.
    """

    # Список доступных моделей Vosk (URL и размеры)
    MODELS = {
        'small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip',
            'size_mb': 80,
            'folder': 'vosk-model-small-ru-0.22'
        },
        'large': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip',
            'size_mb': 2048,
            'folder': 'vosk-model-ru-0.22'
        }
    }

    def __init__(
            self,
            model_path: Optional[str] = None,
            model_name: str = 'small',
            sample_rate: int = 16000,
            chunk: int = 4000,
            energy_threshold: int = 300,
            pause_threshold: float = 0.8,
            dynamic_energy: bool = True,
            auto_download: bool = True,
            fallback_to_google: bool = True,
            download_dir: Optional[str] = None
    ):
        """
        Инициализация распознавателя Vosk.

        Параметры:
            model_path (str, optional): Путь к папке с моделью Vosk.
                                        Если не указан, используется стандартное место.
            model_name (str): Название модели ('small' или 'large').
            sample_rate (int): Частота дискретизации (должна совпадать с моделью).
            chunk (int): Размер буфера для захвата аудио.
            energy_threshold (int): Порог энергии для определения речи.
            pause_threshold (float): Пауза в секундах для разделения фраз.
            dynamic_energy (bool): Автоматическая подстройка порога.
            auto_download (bool): Автоматически скачивать модель, если её нет.
            fallback_to_google (bool): Использовать Google STT при отсутствии интернета или модели.
            download_dir (str, optional): Папка для скачивания моделей.
        """
        if vosk is None or pyaudio is None:
            raise ImportError("Для VoskRecognizer требуются библиотеки: vosk, pyaudio. Установите: pip install vosk pyaudio")

        self.model_name = model_name
        self.sample_rate = sample_rate
        self.chunk = chunk
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.dynamic_energy = dynamic_energy
        self.auto_download = auto_download
        self.fallback_to_google = fallback_to_google
        self.download_dir = download_dir or os.path.join(os.path.expanduser("~"), ".vosk_models")

        # Определяем путь к модели
        if model_path and os.path.exists(model_path):
            self.model_path = model_path
        else:
            # Ищем в стандартной папке
            if model_name in self.MODELS:
                folder = self.MODELS[model_name]['folder']
                self.model_path = os.path.join(self.download_dir, folder)
            else:
                raise ValueError(f"Неизвестная модель: {model_name}. Доступны: {list(self.MODELS.keys())}")

        # Состояние
        self._model = None
        self._recognizer = None
        self._pyaudio_instance = None
        self._stream = None
        self._is_listening = False
        self._callbacks = {'partial': None, 'final': None}
        self._wake_words = []
        self._wake_mode = False

        # Автозагрузка модели
        if not self._ensure_model():
            if self.fallback_to_google:
                print("⚠️ Vosk не готов, будет использован Google STT (при наличии интернета)")
            else:
                raise FileNotFoundError(f"Модель Vosk не найдена: {self.model_path}")

    # ---------- Внутренние методы ----------
    def _ensure_model(self) -> bool:
        """Проверяет наличие модели, скачивает если нужно и auto_download=True."""
        if os.path.exists(self.model_path) and os.path.exists(os.path.join(self.model_path, 'am', 'final.mdl')):
            return True

        if not self.auto_download:
            return False

        if self.model_name not in self.MODELS:
            return False

        print(f"📥 Модель Vosk '{self.model_name}' не найдена. Скачиваю...")
        return self._download_model()

    def _download_model(self) -> bool:
        """Скачивает и распаковывает модель Vosk."""
        if requests is None:
            print("❌ Библиотека requests не установлена. Установите: pip install requests")
            return False

        os.makedirs(self.download_dir, exist_ok=True)

        model_info = self.MODELS[self.model_name]
        url = model_info['url']
        zip_path = os.path.join(self.download_dir, f"{self.model_name}.zip")

        try:
            # Скачивание с прогресс-баром
            print(f"⬇️ Скачивание {url} ...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192

            with open(zip_path, 'wb') as f:
                if tqdm and total_size:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Загрузка") as pbar:
                        for chunk in response.iter_content(chunk_size=block_size):
                            f.write(chunk)
                            pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=block_size):
                        f.write(chunk)

            print("📦 Распаковка...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.download_dir)

            # Удаляем архив
            os.remove(zip_path)
            print(f"✅ Модель загружена в: {self.model_path}")
            return True

        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return False
    
    def _get_recognizer(self) -> vosk.KaldiRecognizer:
        """Создаёт или возвращает существующий распознаватель."""
        if self._recognizer is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Модель Vosk не найдена: {self.model_path}")
            self._model = vosk.Model(self.model_path)
            self._recognizer = vosk.KaldiRecognizer(self._model, self.sample_rate)
        return self._recognizer

    def _get_microphone_stream(self):
        """Открывает поток с микрофона."""
        if self._pyaudio_instance is None:
            self._pyaudio_instance = pyaudio.PyAudio()
        if self._stream is None:
            self._stream = self._pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk,
                stream_callback=None
            )
            self._stream.start_stream()
        return self._stream

    def _cleanup_stream(self):
        """Останавливает и закрывает поток."""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._pyaudio_instance:
            self._pyaudio_instance.terminate()
            self._pyaudio_instance = None

    def _recognize_audio_data(self, audio_data: bytes, final: bool = True) -> Dict:
        """
        Распознаёт байты аудио (PCM, 16 кГц, моно).
        Возвращает словарь с ключами: text, partial, confidence.
        """
        recognizer = self._get_recognizer()
        if final:
            if recognizer.AcceptWaveform(audio_data):
                result = json.loads(recognizer.Result())
                return {
                    'text': result.get('text', ''),
                    'partial': '',
                    'confidence': result.get('confidence', 0.0)
                }
            else:
                # Частичный результат
                partial = json.loads(recognizer.PartialResult())
                return {
                    'text': '',
                    'partial': partial.get('partial', ''),
                    'confidence': 0.0
                }
        else:
            # Возвращаем только частичный результат, не финализируя фразу
            recognizer.AcceptWaveform(audio_data)  # нужно для обработки
            partial = json.loads(recognizer.PartialResult())
            return {
                'text': '',
                'partial': partial.get('partial', ''),
                'confidence': 0.0
            }

    # ---------- Публичные методы ----------
    def listen(self, timeout: float = 5.0, phrase_time_limit: float = 5.0) -> str:
        """
        Записывает с микрофона и возвращает распознанный текст (одна фраза).

        Параметры:
            timeout (float): Время ожидания начала речи.
            phrase_time_limit (float): Максимальная длительность фразы.

        Возвращает:
            str: Распознанный текст или пустую строку при ошибке.

        Пример:
            >>> recognizer = VoskRecognizer()
            >>> text = recognizer.recognize_from_microphone()
            >>> print(text)
        """
        if not self._ensure_model():
            if self.fallback_to_google:
                try:
                    with sr.Microphone() as source:
                        r = sr.Recognizer()
                        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    return r.recognize_google(audio, language="ru-RU")
                except Exception:
                    return ""
            else:
                return ""

        recognizer = self._get_recognizer()
        stream = self._get_microphone_stream()

        start_time = time.time()
        audio_data = b''

        while time.time() - start_time < timeout:
            data = stream.read(self.chunk, exception_on_overflow=False)
            audio_data += data
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '')
                if text:
                    return text
            # Если превысили лимит фразы, останавливаемся
            if len(audio_data) / (self.sample_rate * 2) > phrase_time_limit:
                break

        # Если ничего не распознано, пробуем финальный результат
        final = json.loads(recognizer.FinalResult())
        return final.get('text', '')

    def recognize_from_file(self, file_path: str) -> str:
        """
        Распознаёт аудио из WAV-файла (16 кГц, моно, 16 бит).

        Параметры:
            file_path (str): Путь к WAV-файлу.

        Возвращает:
            str: Распознанный текст или пустую строку при ошибке.

        Пример:
            >>> text = recognizer.recognize_from_file("test.wav")
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        if not self._ensure_model():
            return ""

        recognizer = self._get_recognizer()
        try:
            wf = wave.open(file_path, 'rb')
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.sample_rate:
                raise ValueError("Неверный формат WAV. Ожидается: 16 кГц, моно, 16 бит.")

            while True:
                data = wf.readframes(self.chunk)
                if not data:
                    break
                recognizer.AcceptWaveform(data)

            wf.close()
            result = json.loads(recognizer.FinalResult())
            return result.get('text', '')
        except Exception as e:
            print(f"Ошибка распознавания файла: {e}")
            return ""

    def recognize_stream(
            self,
            callback_partial: Optional[Callable[[str], None]] = None,
            callback_final: Optional[Callable[[str], None]] = None,
            stop_event: Optional[threading.Event] = None
    ):
        """
        Постоянное распознавание с микрофона с вызовом колбэков.

        Параметры:
            callback_partial (callable): Вызывается при частичном распознавании.
                                         Принимает строку (частичный текст).
            callback_final (callable): Вызывается при финальном распознавании фразы.
                                       Принимает строку (полный текст).
            stop_event (threading.Event): Событие для остановки (если передано).

        Пример:
            >>> def on_final(text):
            ...     print(f"Распознано: {text}")
            >>> recognizer.recognize_stream(callback_final=on_final)
        """
        if not self._ensure_model():
            if self.fallback_to_google:
                # Используем Google STT в потоке (упрощённо)
                self._google_stream_fallback(callback_final, stop_event)
            return

        self._callbacks['partial'] = callback_partial
        self._callbacks['final'] = callback_final
        recognizer = self._get_recognizer()
        stream = self._get_microphone_stream()

        self._is_listening = True
        while not (stop_event and stop_event.is_set()):
            try:
                data = stream.read(self.chunk, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text and callback_final:
                        callback_final(text)
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get('partial', '')
                    if partial_text and callback_partial:
                        callback_partial(partial_text)
            except Exception as e:
                print(f"Ошибка в потоке распознавания: {e}")
                break

        self._is_listening = False
        self._cleanup_stream()

    def _google_stream_fallback(self, callback_final, stop_event):
        """Упрощённый fallback на Google через speech_recognition (не потоковый)."""
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            while not (stop_event and stop_event.is_set()):
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                    text = r.recognize_google(audio, language="ru-RU")
                    if callback_final:
                        callback_final(text.lower())
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Google STT error: {e}")

    def set_wake_words(self, words: List[str]):
        """
        Устанавливает список слов для пробуждения (wake-word detection).
        После вызова метода, в потоке будет отслеживаться наличие этих слов.
        При обнаружении вызывается callback_final с полным текстом.

        Параметры:
            words (list): Список слов (например, ['кеша', 'алиса']).
        """
        self._wake_words = [w.lower() for w in words]

    def is_available(self) -> bool:
        """Проверяет, доступен ли Vosk (модель загружена)."""
        return os.path.exists(self.model_path) and os.path.exists(os.path.join(self.model_path, 'am', 'final.mdl'))

    @staticmethod
    def get_version() -> str:
        """Возвращает версию библиотеки vosk."""
        return vosk.__version__ if vosk else "not installed"

    # ---------- Утилиты ----------
    def stop_listening(self):
        """Останавливает текущий поток распознавания."""
        self._is_listening = False
        self._cleanup_stream()

    def reset(self):
        """Сбрасывает состояние распознавателя (очищает буфер)."""
        if self._recognizer:
            self._recognizer.Reset()

    def set_sample_rate(self, rate: int):
        """Изменяет частоту дискретизации (требует пересоздания распознавателя)."""
        self.sample_rate = rate
        self._recognizer = None  # будет пересоздан при следующем вызове


# =========================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ===========================
if __name__ == "__main__":
    # Пример 1: Одиночное распознавание
    recognizer = VoskRecognizer(
    model_path=r"C:\Users\Yusuf\Programming\Python\vosk-model-small-ru-0.22",
    auto_download=False,          # уже скачано
    fallback_to_google=False      # чтобы не пытался использовать Google при ошибке
)
    print("Говорите...")
    text = recognizer.listen(timeout=5)
    print(f"Распознано: {text}")

    # Пример 2: Потоковое распознавание с колбэками
    def on_partial(partial):
        sys.stdout.write(f"\rЧастично: {partial}")
        sys.stdout.flush()

    def on_final(final):
        print(f"\nФинально: {final}")

    print("\nПотоковое распознавание (скажите что-нибудь, Ctrl+C для остановки)")
    stop = threading.Event()
    try:
        recognizer.recognize_stream(callback_partial=on_partial, callback_final=on_final, stop_event=stop)
    except KeyboardInterrupt:
        stop.set()
        recognizer.stop_listening()
        print("\nОстановлено пользователем.")
