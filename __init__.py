"""Личные библиотеки. Подпакеты импортируются лениво, чтобы не тянуть тяжёлые зависимости."""
import importlib

_PACKAGES = ("yandex_smart_home", "yandex_alice", "makerzoid_robot", "yandex_music_tools",
             "voice_recognition", "ai_modules", "mosru_diary")


def __getattr__(name):
    if name in _PACKAGES:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(name)


__all__ = list(_PACKAGES)
