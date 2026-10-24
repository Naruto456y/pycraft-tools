"""Скачивание избранных треков Яндекс.Музыки (пакет yandex-music)."""
import os
import time
from pathlib import Path
from typing import Optional


class YandexMusicError(Exception):
    pass


class YandexMusic:
    """Обёртка над yandex_music.Client.

    Токен берётся из аргумента или переменной окружения YANDEX_MUSIC_TOKEN.
    """

    def __init__(self, token: Optional[str] = None, proxy: Optional[str] = None):
        token = token or os.getenv("YANDEX_MUSIC_TOKEN")
        if not token:
            raise YandexMusicError("Не указан токен (аргумент или YANDEX_MUSIC_TOKEN)")
        try:
            from yandex_music import Client
        except ImportError as e:
            raise YandexMusicError("Установите: pip install yandex-music") from e
        if proxy:
            os.environ["HTTP_PROXY"] = os.environ["HTTPS_PROXY"] = proxy
        self.client = Client(token).init()

    def likes(self):
        return self.client.users_likes_tracks() or []

    @staticmethod
    def _filename(track) -> str:
        artists = ", ".join(a.name for a in track.artists) if track.artists else "Unknown"
        name = f"{artists} - {track.title}.mp3"
        return "".join(c for c in name if c not in r'<>:"/\|?*')

    def download_likes(self, output_dir="./YandexMusic", delay=1.0, retries=3):
        """Скачивает избранное. Возвращает (скачано, ошибок)."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        likes = self.likes()
        downloaded = failed = 0
        for idx, like in enumerate(likes, 1):
            try:
                track = like.fetch_track()
                if not track:
                    failed += 1
                    continue
                path = out / self._filename(track)
                if path.exists():
                    continue
                print(f"[{idx}/{len(likes)}] {path.stem}")
                for attempt in range(retries):
                    try:
                        track.download(path)
                        downloaded += 1
                        break
                    except Exception:
                        if attempt == retries - 1:
                            raise
                        time.sleep(delay)
                time.sleep(delay)
            except Exception as e:
                print(f"[{idx}/{len(likes)}] ошибка: {e}")
                failed += 1
        return downloaded, failed
