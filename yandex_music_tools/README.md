# 🎵 yandex_music_tools — Яндекс.Музыка (PyCraft Tools)

Небольшая обёртка над пакетом [`yandex-music`](https://pypi.org/project/yandex-music/): получить список «Мне нравится» и скачать все треки в папку.

> ⚠️ Скачивайте только то, что вам доступно по вашей подписке, и только для личного использования.

## 🚀 Установка

```bash
pip install pycraft-tools[yandex_music_tools]   # модуль + yandex-music
```

## 🔑 Токен

Передайте токен в конструктор или задайте переменную окружения `YANDEX_MUSIC_TOKEN` (удобно держать её в `.env`). Без токена будет `YandexMusicError`.

## 💻 Пример

```python
from yandex_music_tools import YandexMusic

ym = YandexMusic()                       # токен из YANDEX_MUSIC_TOKEN
likes = ym.likes()                       # список лайкнутых треков
print(len(likes))

downloaded, failed = ym.download_likes(output_dir="./YandexMusic", delay=1.0, retries=3)
print(f"Скачано: {downloaded}, ошибок: {failed}")
```

| Метод | Что делает |
|---|---|
| `YandexMusic(token=None, proxy=None)` | подключение; `proxy` выставляет `HTTP_PROXY` и `HTTPS_PROXY` |
| `likes()` | понравившиеся треки |
| `download_likes(output_dir, delay, retries)` | скачивает в `Артисты - Название.mp3`, уже скачанные пропускает, возвращает `(скачано, ошибок)` |

## ⚠️ Ограничения

- Задержка `delay` между треками нужна, чтобы Яндекс не ограничил запросы.
- Из имени файла убираются символы, недопустимые в Windows.
- Это неофициальный клиент: API Яндекс.Музыки может измениться.
