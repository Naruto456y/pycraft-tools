"""Клиенты нейросетей: пока GigaChat (Сбер), другие провайдеры добавляются отдельными файлами."""
from .gigachat import GigaChat, GigaChatError

__all__ = ["GigaChat", "GigaChatError"]
