"""Яндекс.Музыка. Назван yandex_music_tools, чтобы не затенять пакет yandex_music."""
from .downloader import YandexMusic, YandexMusicError

__all__ = ["YandexMusic", "YandexMusicError"]
