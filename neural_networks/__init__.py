"""Нейросети (локальные модели). Тяжёлые зависимости импортируются лениво."""


def __getattr__(name):
    if name in ("GigaAMRecognizer", "normalize"):
        from . import gigaam
        return getattr(gigaam, name)
    raise AttributeError(name)


__all__ = ["GigaAMRecognizer", "normalize"]
