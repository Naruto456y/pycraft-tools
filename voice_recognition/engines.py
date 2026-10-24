"""Движки распознавания речи с единым интерфейсом."""
import time
from abc import ABC, abstractmethod


class Engine(ABC):
    name = ""

    @abstractmethod
    def listen(self, timeout=5, phrase_limit=5) -> str:
        """Слушает микрофон, возвращает текст в нижнем регистре ('' если не распознано)."""


class GoogleEngine(Engine):
    name = "google"

    def __init__(self, language="ru-RU"):
        import speech_recognition as sr
        self._sr = sr
        self.language = language
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 400
        self.rec.pause_threshold = 0.8
        self.rec.dynamic_energy_threshold = True
        self._last = 0
        self.adjust()

    def adjust(self):
        try:
            with self._sr.Microphone() as src:
                self.rec.adjust_for_ambient_noise(src, duration=2)
                self._last = time.time()
        except Exception as e:
            print("[google]", e)

    def listen(self, timeout=5, phrase_limit=5):
        try:
            if time.time() - self._last > 1800:
                self.adjust()
            with self._sr.Microphone() as src:
                audio = self.rec.listen(src, timeout=timeout, phrase_time_limit=phrase_limit)
            return self.rec.recognize_google(audio, language=self.language).lower().strip()
        except Exception:
            return ""


class VoskEngine(Engine):
    name = "vosk"

    def __init__(self, **kwargs):
        from .vosk_engine import VoskRecognizer
        self._rec = VoskRecognizer(**kwargs)

    def listen(self, timeout=5, phrase_limit=5):
        return (self._rec.listen(timeout=timeout, phrase_time_limit=phrase_limit) or "").lower().strip()


class GigaAMEngine(Engine):
    name = "gigaam"

    def __init__(self, **kwargs):
        try:
            from neural_networks.gigaam import GigaAMRecognizer
        except ImportError:
            from ..neural_networks.gigaam import GigaAMRecognizer
        self._rec = GigaAMRecognizer(**kwargs)

    def listen(self, timeout=5, phrase_limit=5):
        # Для микрофона с GigaAM используйте recognize(pcm_bytes) / recognize_file().
        raise NotImplementedError("GigaAMEngine принимает аудио: recognize(pcm_bytes) / recognize_file(path)")

    def recognize(self, pcm_bytes, **kw):
        return self._rec.recognize(pcm_bytes, **kw)

    def recognize_file(self, path, **kw):
        return self._rec.recognize_file(path, **kw)
