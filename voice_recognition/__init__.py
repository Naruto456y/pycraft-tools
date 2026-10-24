"""Распознавание речи с выбором движка: google, vosk, gigaam.

    from libraries.voice_recognition import create_recognizer
    rec = create_recognizer("vosk", model_name="small")
    text = rec.listen()
"""
from .engines import Engine, GoogleEngine, VoskEngine, GigaAMEngine

ENGINES = {"google": GoogleEngine, "vosk": VoskEngine, "gigaam": GigaAMEngine}


def create_recognizer(engine="google", **kwargs):
    try:
        cls = ENGINES[engine.lower()]
    except KeyError:
        raise ValueError(f"Неизвестный движок {engine!r}. Доступны: {', '.join(ENGINES)}") from None
    return cls(**kwargs)


__all__ = ["create_recognizer", "ENGINES", "Engine", "GoogleEngine", "VoskEngine", "GigaAMEngine"]
