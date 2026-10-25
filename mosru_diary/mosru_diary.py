#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
📘 MOSRU_DIARY.PY — ДНЕВНИК МЭШ (school.mos.ru) ДЛЯ PYCRAFT TOOLS
================================================================================
Читает электронный дневник МЭШ: домашние задания (с вложениями), расписание
с временем уроков, оценки и средний балл, рейтинг, посещаемость, каникулы и
учебные дни, питание, события школы, контрольные, проекты.

Только ЧТЕНИЕ: ничего не отмечается, не отправляется и не меняется.
Логин, пароль и SMS модуль не вводит и не хранит: первый вход вы делаете
сами в окне браузера (MosRuDiary.login()), дальше работает по куки профиля.

Версия: 0.1.0
Автор: Юсуф
================================================================================
"""

import argparse
import base64
import html
import json
import re
import subprocess
import sys
import textwrap
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import unquote, urlsplit, parse_qs

import requests

__version__ = "0.1.0"
__all__ = ["MosRuDiary", "MosRuError", "LoginRequired"]

BASE = "https://school.mos.ru"
HOMEWORK_PAGE = f"{BASE}/diary/homeworks/homeworks/"
# Заголовки, которые портал реально требует; остальные браузерные не нужны.
KEEP_HEADERS = ("authorization", "profile-id", "profile-type", "x-mes-roleid",
                "x-mes-subsystem", "accept", "content-type")
EXPIRY_MARGIN = 10 * 60          # обновляем токен за 10 минут до конца
MAX_FILE_BYTES = 25 * 1024 * 1024
DAY_NAMES = ("пн", "вт", "ср", "чт", "пт", "сб", "вс")
BROWSER_CANDIDATES = (
    r"C:\Program Files\Yandex\YandexBrowser\Application\browser.exe",
    r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

DateLike = Union[date, str, None]


class MosRuError(Exception):
    """Ошибка работы с порталом МЭШ."""


class LoginRequired(MosRuError):
    """В профиле браузера нет живого входа: нужен ручной вход (login())."""


def _to_date(value: DateLike, default: Optional[date] = None) -> date:
    if value is None:
        return default or date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _shape(value: Any, depth: int = 0) -> Any:
    """Структура JSON без значений (для отладки и разведки новых методов)."""
    if depth > 5:
        return "…"
    if isinstance(value, dict):
        return {k: _shape(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [f"len={len(value)}", _shape(value[0], depth + 1)] if value else []
    return type(value).__name__


class MosRuDiary:
    """
    📘 КЛИЕНТ ДНЕВНИКА МЭШ — чтение данных ученика без открытия браузера.

    Как это работает:
        1. Данные берутся обычными GET-запросами (requests). Нужен только токен
           (JWT на 24 часа), он лежит локально в <data_dir>/mesh_auth.json.
        2. Когда токен кончился, на несколько секунд запускается браузер с
           сохранённым профилем (<data_dir>/yandex_profile): портал сам выдаёт
           новый токен, а кнопка «Войти» нажимается автоматически (по куки).
        3. Если вход в профиле протух, поднимается LoginRequired: вызовите
           login() и войдите вручную один раз.

    📌 ПРИМЕР:
        >>> from mosru_diary import MosRuDiary
        >>> d = MosRuDiary(data_dir=r"C:\\Users\\Me\\.session")
        >>> for hw in d.homework(days=7):
        ...     print(hw["date"], hw["subject"], hw["homework"])
        >>> print(d.marks_summary()["overall"]["average"])
        >>> print(d.school_day_status())      # {'school_day': False, 'reason': 'каникулы'}
    """

    def __init__(self, data_dir: Union[str, Path, None] = None,
                 browser_path: Optional[str] = None, cdp_port: int = 9222,
                 profile_name: str = "yandex_profile", verbose: bool = False):
        """
        Параметры:
            data_dir: папка для токена и профиля браузера (по умолчанию
                      ~/.pycraft/mosru_diary). Держите её вне git!
            browser_path: путь к браузеру (по умолчанию ищется Яндекс/Chrome/Edge)
            cdp_port: порт отладки браузера для обновления токена
            profile_name: имя подпапки профиля браузера внутри data_dir
            verbose: печатать служебные сообщения
        """
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".pycraft" / "mosru_diary"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.auth_file = self.data_dir / "mesh_auth.json"
        self.profile_dir = self.data_dir / profile_name
        self.cdp_port = cdp_port
        self.browser_path = browser_path
        self.verbose = verbose
        self._auth: Optional[dict] = None
        self._ids: Optional[dict] = None
        self._cache: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 🔐 ТОКЕН И ВХОД
    # ------------------------------------------------------------------

    def _log(self, *args) -> None:
        if self.verbose:
            print("[mosru_diary]", *args, file=sys.stderr)

    def _load_auth(self) -> Optional[dict]:
        if self._auth is None:
            try:
                self._auth = json.loads(self.auth_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self._auth = None
        return self._auth

    @staticmethod
    def _jwt_exp(auth: dict) -> float:
        token = auth["headers"]["authorization"].split()[-1]
        payload = token.split(".")[1]
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return float(data["exp"])

    def token_expires_at(self) -> Optional[datetime]:
        """Когда кончится токен (None, если токена ещё нет)."""
        auth = self._load_auth()
        try:
            return datetime.fromtimestamp(self._jwt_exp(auth)) if auth else None
        except Exception:
            return None

    def has_fresh_token(self) -> bool:
        auth = self._load_auth()
        try:
            return bool(auth) and self._jwt_exp(auth) - time.time() > EXPIRY_MARGIN
        except Exception:
            return False

    def _find_browser(self) -> str:
        if self.browser_path and Path(self.browser_path).exists():
            return self.browser_path
        for candidate in BROWSER_CANDIDATES:
            if Path(candidate).exists():
                return candidate
        raise MosRuError("Не найден браузер (Яндекс/Chrome/Edge). Укажите browser_path.")

    def _cdp_alive(self) -> bool:
        try:
            return requests.get(f"http://127.0.0.1:{self.cdp_port}/json/version", timeout=2).ok
        except requests.RequestException:
            return False

    def _start_browser(self, visible: bool) -> bool:
        """Запускает браузер с профилем. True, если запустили мы (а не он уже был)."""
        if self._cdp_alive():
            return False
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        args = [self._find_browser(), f"--remote-debugging-port={self.cdp_port}",
                f"--user-data-dir={self.profile_dir}"]
        if not visible:
            args.append("--start-minimized")
        subprocess.Popen(args)
        for _ in range(40):
            if self._cdp_alive():
                return True
            time.sleep(0.5)
        raise MosRuError("Браузер не открыл порт отладки за 20 секунд.")

    def _capture_auth(self, manual_login: bool = False) -> dict:
        """Открывает страницу заданий и перехватывает заголовки её запроса к API."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise MosRuError("Для обновления токена нужен playwright: pip install playwright") from e

        started = self._start_browser(visible=manual_login)
        caught: dict = {}
        on_login_page = False
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{self.cdp_port}")
            page = browser.contexts[0].new_page()

            def on_request(req):
                parts = urlsplit(req.url)
                if (req.method == "GET" and parts.netloc == "school.mos.ru"
                        and parts.path == "/api/family/web/v1/homeworks"):
                    try:
                        headers = req.all_headers()
                    except Exception:
                        headers = req.headers
                    caught["headers"] = {k: v for k, v in headers.items()
                                         if k.lower() in KEEP_HEADERS}
                    caught["student_id"] = (parse_qs(parts.query).get("student_id") or [""])[0]

            def wait_caught(seconds: float = 15) -> None:
                for _ in range(int(seconds * 2)):
                    if caught:
                        return
                    page.wait_for_timeout(500)

            page.on("request", on_request)
            try:
                page.goto(HOMEWORK_PAGE)
                if manual_login:
                    input("Войдите в МЭШ в открывшемся окне, дождитесь страницы "
                          "домашних заданий и нажмите Enter здесь... ")
                    page.goto(HOMEWORK_PAGE)
                wait_caught()
                if not caught and not manual_login:
                    # Портал вернул на главную с кнопкой «Войти»: куки профиля помнят
                    # аккаунт, достаточно нажать её (пароль не вводится).
                    try:
                        page.get_by_text("Войти", exact=True).first.click(timeout=5000)
                        page.wait_for_url("**/diary/**", timeout=20000)
                    except Exception:
                        pass
                    if "school.mos.ru/diary" in page.url:
                        page.goto(HOMEWORK_PAGE)
                        wait_caught()
                on_login_page = "login" in urlsplit(page.url).netloc or "/login" in page.url
            finally:
                page.close()
                if started:                    # закрываем только то, что открыли сами
                    try:
                        browser.new_browser_cdp_session().send("Browser.close")
                    except Exception:
                        pass
        if not caught or on_login_page:
            raise LoginRequired("Нужен вход в МЭШ: вызовите login() и войдите вручную.")
        caught["saved_at"] = datetime.now().isoformat(timespec="seconds")
        self.auth_file.write_text(json.dumps(caught, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        self._auth, self._ids, self._cache = caught, None, {}
        return caught

    def login(self) -> None:
        """Ручной вход: откроет окно браузера, войдите сами (пароль/SMS/QR), затем Enter."""
        self._capture_auth(manual_login=True)

    def ensure_auth(self) -> dict:
        """Возвращает свежий токен; при необходимости обновляет его через браузер."""
        if not self.has_fresh_token():
            self._log("токен устарел, обновляю через браузер")
            self._capture_auth()
        return self._load_auth()  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # 🌐 НИЗКИЙ УРОВЕНЬ
    # ------------------------------------------------------------------

    def _headers(self) -> dict:
        auth = self.ensure_auth()
        headers = dict(auth["headers"])
        headers["x-mes-role"] = headers.get("profile-type", "student")   # нужен календарю
        return headers

    def _get(self, path: str, params: Optional[dict] = None, *, raw: bool = False) -> Any:
        """GET к API МЭШ. При 401/403 один раз обновляет токен и повторяет."""
        url = path if path.startswith("http") else f"{BASE}{path}"
        for attempt in (1, 2):
            resp = requests.get(url, headers=self._headers(), params=params, timeout=25)
            if resp.status_code in (401, 403) and attempt == 1:
                self._capture_auth()
                continue
            break
        if not resp.ok:
            raise MosRuError(f"{path}: HTTP {resp.status_code}")
        return resp if raw else resp.json()

    @property
    def ids(self) -> dict:
        """Идентификаторы ученика (берутся из /profile по токену, на диск не пишутся)."""
        if self._ids is None:
            self.ensure_auth()
            children = self._get("/api/family/web/v1/profile").get("children") or []
            if not children:
                raise MosRuError("В профиле нет ученика (children пуст).")
            c = children[0]
            self._ids = {
                "student_id": c["id"], "person_id": c["contingent_guid"],
                "school_id": c["school"]["id"], "school_name": c["school"]["name"],
                "class_unit_id": c["class_unit_id"], "class_name": c["class_name"],
                "parallel_curriculum_id": c.get("parallel_curriculum_id"),
                "first_name": c.get("first_name"),
            }
        return self._ids

    def raw(self, path: str, params: Optional[dict] = None) -> Any:
        """Любой GET к API (для разведки новых методов). Пример: raw('/api/family/web/v1/profile')."""
        return self._get(path, params)

    def shape(self, path: str, params: Optional[dict] = None) -> Any:
        """Структура ответа (имена полей и типы) без значений."""
        return _shape(self._get(path, params))

    # ------------------------------------------------------------------
    # 👤 ПРОФИЛЬ И ШКОЛА
    # ------------------------------------------------------------------

    def profile(self) -> dict:
        """Безопасный профиль: имя, класс, школа. Без телефона, почты и СНИЛС."""
        i = self.ids
        return {"first_name": i["first_name"], "class_name": i["class_name"],
                "school_id": i["school_id"], "school_name": i["school_name"],
                "student_id": i["student_id"]}

    def school_info(self) -> dict:
        """Школа: директор, классные руководители, учителя и их предметы."""
        i = self.ids
        return self._get("/api/family/web/v1/school_info", {
            "class_unit_id": i["class_unit_id"], "school_id": i["school_id"],
            "student_id": i["student_id"]})

    def school_events(self, start: DateLike = None, end: DateLike = None) -> List[dict]:
        """События школы (органайзер). По умолчанию весь учебный год."""
        today = date.today()
        y = today.year if today.month >= 9 else today.year - 1
        s = _to_date(start, date(y, 9, 1))
        e = _to_date(end, date(y + 1, 8, 31))
        return self._get("/api/ej/organizer/family/v1/events", {
            "school_id": self.ids["school_id"],
            "begin_date": s.strftime("%d.%m.%Y"), "end_date": e.strftime("%d.%m.%Y")})

    def projects(self) -> List[dict]:
        """Проектная деятельность (задания по проектам)."""
        data = self._get("/api/projects/core/project-tasks", {"personId": self.ids["person_id"]})
        return data.get("content", [])

    def books(self) -> List[dict]:
        """Выданные учебники."""
        return self._get("/api/education_books/v1/issued_materials",
                         {"personId": self.ids["person_id"]}).get("books", [])

    def gamification(self) -> dict:
        """Баланс в геймификации МЭШ (только баланс)."""
        d = self._get("/api/gamification/v1/profiles", {"personId": self.ids["person_id"]})
        return {"balance": d.get("balance")}

    # ------------------------------------------------------------------
    # 📅 КАНИКУЛЫ И УЧЕБНЫЕ ДНИ
    # ------------------------------------------------------------------

    def _academic_year(self) -> dict:
        if "year" not in self._cache:
            years = self._get("/api/ej/core/family/v1/academic_years")
            self._cache["year"] = next((y for y in years if y.get("current_year")), years[-1])
        return self._cache["year"]

    def periods(self) -> List[dict]:
        """Учебные периоды текущего года: четверти и каникулы (is_vacation)."""
        if "periods" not in self._cache:
            data = self._get("/api/ej/core/family/v1/periods_schedules", {
                "academic_year_id": self._academic_year()["id"],
                "student_profile_id": self.ids["student_id"]})
            self._cache["periods"] = [p for s in data for p in s.get("periods", [])]
        return self._cache["periods"]

    def transpositions(self) -> List[dict]:
        """Переносы и праздничные дни производственного календаря."""
        if "transp" not in self._cache:
            cal = self._academic_year()["calendar_id"]
            self._cache["transp"] = self._get(
                f"/api/ej/core/family/v1/calendars/{cal}/calendar_transpositions")
        return self._cache["transp"]

    def school_day_status(self, day: DateLike = None) -> dict:
        """
        Учебный ли день: {'school_day': bool, 'reason': str, 'date': 'ГГГГ-ММ-ДД'},
        на каникулах ещё 'vacation': True. Учитывает каникулы, праздники,
        переносы и выходные.
        """
        d = _to_date(day)
        iso = d.isoformat()
        for p in self.periods():
            if p.get("is_vacation") and p["begin_date"][:10] <= iso <= p["end_date"][:10]:
                return {"school_day": False, "vacation": True,
                        "reason": p.get("name") or "каникулы", "date": iso}
        tr = next((t for t in self.transpositions() if t["date"][:10] == iso), None)
        if tr and tr.get("is_holiday"):
            return {"school_day": False, "reason": tr.get("note") or "праздничный день", "date": iso}
        if tr and tr.get("schedule_for_weekday"):
            return {"school_day": True, "reason": "рабочий день по переносу", "date": iso}
        if d.weekday() >= 5:
            return {"school_day": False, "reason": f"выходной ({DAY_NAMES[d.weekday()]})", "date": iso}
        return {"school_day": True, "reason": "учебный день", "date": iso}

    def is_school_day(self, day: DateLike = None) -> bool:
        return self.school_day_status(day)["school_day"]

    def is_vacation(self, day: DateLike = None) -> bool:
        return bool(self.school_day_status(day).get("vacation"))

    # ------------------------------------------------------------------
    # 📚 ДОМАШНИЕ ЗАДАНИЯ И ВЛОЖЕНИЯ
    # ------------------------------------------------------------------

    def schedule_short(self, dates: List[str]) -> List[dict]:
        """Короткое расписание: по дням список уроков с begin_time/end_time."""
        out: List[dict] = []
        for i in range(0, len(dates), 14):               # по 14 дат за запрос
            data = self._get("/api/family/web/v1/schedule/short", {
                "student_id": self.ids["student_id"], "dates": ",".join(dates[i:i + 14])})
            out += data.get("payload", [])
        return out

    @staticmethod
    def _links(*parts) -> List[str]:
        links: List[str] = []

        def walk(x):
            if isinstance(x, str):
                if x.startswith("http") and x not in links:
                    links.append(x)
            elif isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)

        for p in parts:
            walk(p)
        return links

    def homework(self, start: DateLike = None, end: DateLike = None, *,
                 days: int = 7, back: int = 0, only_undone: bool = False,
                 files: bool = False, files_dir: Union[str, Path, None] = None) -> List[dict]:
        """
        Домашние задания. По умолчанию от сегодня на `days` дней вперёд
        (`back` — начать на столько дней раньше, удобно на каникулах).

        Запись: date, subject, subject_id, lesson_time ('12:10-12:50' или '-'),
        homework (текст), links, materials (названия), is_done, assigned_on,
        files (если files=True: пути скачанных файлов и их текста).
        """
        s = _to_date(start, date.today() - timedelta(days=back))
        e = _to_date(end, date.today() + timedelta(days=days))
        items = self._get("/api/family/web/v1/homeworks", {
            "from": s.isoformat(), "to": e.isoformat(),
            "student_id": self.ids["student_id"]}).get("payload", [])
        times: Dict[Tuple[str, Any], str] = {}
        try:
            for day in self.schedule_short(sorted({it["date"] for it in items})):
                for ls in day.get("lessons", []):
                    times.setdefault((day["date"], ls.get("subject_id")),
                                     f"{ls['begin_time'][:5]}-{ls['end_time'][:5]}")
        except MosRuError as ex:
            self._log("время уроков недоступно:", ex)
        rows = [{
            "date": it["date"], "subject": it["subject_name"],
            "subject_id": it.get("subject_id"),
            "lesson_time": times.get((it["date"], it.get("subject_id")), "-"),
            "homework": " ".join(it["homework"].split()),
            "links": self._links(it.get("attachments"), it.get("materials")),
            "materials": [m.get("title") for m in it.get("materials") or [] if m.get("title")],
            "is_done": it["is_done"], "assigned_on": it.get("date_assigned_on"),
        } for it in items]
        rows.sort(key=lambda r: (r["date"], r["lesson_time"] == "-", r["lesson_time"], r["subject"]))
        if only_undone:
            rows = [r for r in rows if not r["is_done"]]
        if files:
            self.download_files(rows, files_dir)
        return rows

    @staticmethod
    def office_text(path: Path) -> Optional[str]:
        """Текст из .docx/.pptx/.xlsx без сторонних библиотек (старые .doc/.ppt — None)."""
        kinds = {".docx": r"word/document\.xml", ".pptx": r"ppt/slides/slide\d+\.xml",
                 ".xlsx": r"xl/(sharedStrings|worksheets/sheet\d+)\.xml"}
        pattern = kinds.get(path.suffix.lower())
        if not pattern:
            return None
        try:
            with zipfile.ZipFile(path) as z:
                chunks = []
                for n in sorted(n for n in z.namelist() if re.fullmatch(pattern, n)):
                    xml = z.read(n).decode("utf-8", "replace")
                    xml = re.sub(r"</(w:p|a:p|row)>", "\n", xml)
                    xml = re.sub(r"<w:tab/>", "\t", xml)
                    chunks.append(html.unescape(re.sub(r"<[^>]+>", "", xml)))
            return "\n".join(chunks).strip()
        except (zipfile.BadZipFile, KeyError):
            return None

    def download_files(self, rows: List[dict], files_dir: Union[str, Path, None] = None) -> None:
        """
        Скачивает вложения заданий (только с school.mos.ru, до 25 МБ) и для
        .docx/.pptx/.xlsx кладёт рядом <имя>.txt с текстом. В каждую запись
        добавляет files: [{path, text_path, kind, error?}].
        """
        dst_dir = Path(files_dir) if files_dir else self.data_dir / "homework_files"
        dst_dir.mkdir(parents=True, exist_ok=True)
        for row in rows:
            row["files"] = []
            for link in row["links"]:
                parts = urlsplit(link)
                if parts.netloc != "school.mos.ru":
                    continue
                name = re.sub(r'[<>:"/\\|?*]', "_", unquote(parts.path.rsplit("/", 1)[-1]))
                dst = dst_dir / f"{row['date']}_{row['subject'][:30]}_{name}"
                entry = {"path": str(dst), "text_path": None, "kind": dst.suffix.lower()}
                try:
                    if not dst.exists():
                        with requests.get(link, stream=True, timeout=30) as r:
                            r.raise_for_status()
                            if int(r.headers.get("content-length", 0)) > MAX_FILE_BYTES:
                                entry["error"] = "слишком большой файл"
                                row["files"].append(entry)
                                continue
                            dst.write_bytes(r.content)
                    text = self.office_text(dst)
                    if text:
                        txt = dst.with_name(dst.name + ".txt")
                        txt.write_text(text, encoding="utf-8")
                        entry["text_path"] = str(txt)
                except Exception as ex:                      # noqa: BLE001
                    entry["error"] = type(ex).__name__
                row["files"].append(entry)

    # ------------------------------------------------------------------
    # 🕒 РАСПИСАНИЕ
    # ------------------------------------------------------------------

    def schedule(self, start: DateLike = None, end: DateLike = None, *,
                 lessons_only: bool = True) -> List[dict]:
        """
        Расписание с временем, кабинетом и пометками отмены/замены.
        Запись: date, start, end, subject, room, cancelled, replaced,
        hw_total, hw_done, marks, source.
        lessons_only=True оставляет только уроки (source PLAN).
        """
        s = _to_date(start)
        e = _to_date(end, s)
        data = self._get("/api/eventcalendar/v1/api/events", {
            "person_ids": self.ids["person_id"],
            "begin_date": s.isoformat(), "end_date": e.isoformat(),
            "expand": "marks,homework,absence_reason_id,health_status,nonattendance_reason_id",
            "source_types": "PLAN,AE,EC,EVENTS,AFISHA,ORGANIZER,OLYMPIAD,PROF"})
        rows = []
        for ev in data.get("response", []) or []:
            if lessons_only and ev.get("source") != "PLAN":
                continue
            hw = ev.get("homework") or {}
            rows.append({
                "date": ev["start_at"][:10], "start": ev["start_at"][11:16],
                "end": ev["finish_at"][11:16], "subject": ev.get("subject_name"),
                "room": ev.get("room_number") or ev.get("room_name"),
                "cancelled": ev.get("cancelled", False), "replaced": ev.get("replaced", False),
                "hw_total": hw.get("total_count", 0), "hw_done": hw.get("execute_count", 0),
                "marks": ev.get("marks"), "source": ev.get("source"),
            })
        rows.sort(key=lambda r: (r["date"], r["start"]))
        return rows

    # ------------------------------------------------------------------
    # 🎓 ОЦЕНКИ
    # ------------------------------------------------------------------

    def marks(self, start: DateLike = None, end: DateLike = None, *, days: int = 0) -> List[dict]:
        """
        Оценки за период. По умолчанию с 1 сентября текущего учебного года по сегодня.
        Запись: date, subject, value ('5', 'Н', ...), five (число 1–5 или None),
        weight, control_form, comment, is_exam.
        """
        today = date.today()
        y = today.year if today.month >= 9 else today.year - 1
        s = _to_date(start, today - timedelta(days=days) if days else date(y, 9, 1))
        e = _to_date(end, today)
        items = self._get("/api/family/web/v1/marks", {
            "student_id": self.ids["student_id"],
            "from": s.isoformat(), "to": e.isoformat()}).get("payload", [])
        rows = []
        for m in items:
            five = None
            try:
                five = m["values"][0]["grade"]["five"]
            except (KeyError, IndexError, TypeError):
                pass
            rows.append({
                "date": m["date"], "subject": m["subject_name"], "subject_id": m.get("subject_id"),
                "value": m.get("value"), "five": five, "weight": m.get("weight") or 1,
                "control_form": m.get("control_form_name"), "comment": m.get("comment"),
                "is_exam": m.get("is_exam", False),
            })
        rows.sort(key=lambda r: (r["date"], r["subject"]))
        return rows

    def marks_summary(self, start: DateLike = None, end: DateLike = None) -> dict:
        """
        Средний балл и количество оценок.
        Возвращает {'overall': {...}, 'subjects': {предмет: {...}}}, где в каждом:
        count, average (взвешенный, как в МЭШ), average_plain (простой),
        distribution ({'5': n, ...}), last (последние 5 оценок).
        """
        by: Dict[str, List[dict]] = {}
        for m in self.marks(start, end):
            by.setdefault(m["subject"], []).append(m)

        def stat(ms: List[dict]) -> dict:
            nums = [m for m in ms if m["five"] is not None]
            wsum = sum(m["weight"] for m in nums)
            dist: Dict[str, int] = {}
            for m in ms:
                dist[str(m["value"])] = dist.get(str(m["value"]), 0) + 1
            return {
                "count": len(ms),
                "average": round(sum(m["five"] * m["weight"] for m in nums) / wsum, 2) if wsum else None,
                "average_plain": round(sum(m["five"] for m in nums) / len(nums), 2) if nums else None,
                "distribution": dict(sorted(dist.items())),
                "last": [{"date": m["date"], "value": m["value"], "control_form": m["control_form"]}
                         for m in ms[-5:]],
            }

        subjects = {name: stat(ms) for name, ms in sorted(by.items())}
        every = [m for ms in by.values() for m in ms]
        return {"overall": stat(every) if every else {"count": 0, "average": None},
                "subjects": subjects}

    def final_marks(self) -> List[dict]:
        """Итоговые оценки (четверти, год) текущего учебного года."""
        return self._get("/api/family/web/v1/final_marks/v2", {
            "person_id": self.ids["person_id"], "academic_year_id": self._academic_year()["id"],
            "student_id": self.ids["student_id"]}).get("subjects", [])

    def rating(self, day: DateLike = None, history_days: int = 14) -> dict:
        """
        Место в рейтинге класса: place, class_size, average (ваш), class_average,
        trend и history по дням. Данные одноклассников не возвращаются.
        """
        d = _to_date(day)
        me = self.ids["person_id"]
        cls = self._get("/api/ej/rating/v1/rank/class", {"personId": me, "date": d.isoformat()})
        own = next((x for x in cls if x.get("personId") == me), None)
        avgs = [x["rank"]["averageMarkFive"] for x in cls
                if x.get("rank") and x["rank"].get("averageMarkFive")]
        short = self._get("/api/ej/rating/v1/rank/rankShort", {
            "personId": me, "beginDate": (d - timedelta(days=history_days)).isoformat(),
            "endDate": d.isoformat()})
        return {
            "place": own["rank"]["rankPlace"] if own else None,
            "class_size": len(cls),
            "average": own["rank"]["averageMarkFive"] if own else None,
            "class_average": round(sum(avgs) / len(avgs), 2) if avgs else None,
            "trend": own["rank"].get("trend") if own else None,
            "history": [{"date": h["date"][:10], "place": h["rankPlace"]} for h in short],
        }

    # ------------------------------------------------------------------
    # 🏫 ПОСЕЩАЕМОСТЬ, КОНТРОЛЬНЫЕ, ПИТАНИЕ
    # ------------------------------------------------------------------

    def attendance(self, start: DateLike = None, end: DateLike = None, *, days: int = 7) -> dict:
        """Посещаемость: пропуски/опоздания по дням за период (по умолчанию 7 дней назад)."""
        e = _to_date(end)
        s = _to_date(start, e - timedelta(days=days))
        return self._get("/api/family/web/v1/attendance", {
            "student_id": self.ids["student_id"], "from": s.isoformat(), "to": e.isoformat()})

    def visits(self, start: DateLike = None, end: DateLike = None, *, days: int = 7) -> List[dict]:
        """Проходы в школу (турникет): время входа/выхода по дням (запрос не длиннее 7 дней)."""
        e = _to_date(end)
        s = _to_date(start, e - timedelta(days=min(days, 7) - 1))
        return self._get("/api/pass/entrances/v1/visit_durations", {
            "personId": self.ids["person_id"], "from": s.isoformat(),
            "to": e.isoformat()}).get("payload", [])

    def test_works(self, start: DateLike = None, end: DateLike = None) -> List[dict]:
        """Контрольные и проверочные работы (по умолчанию от 1 сентября на 30 дней вперёд)."""
        today = date.today()
        y = today.year if today.month >= 9 else today.year - 1
        s = _to_date(start, date(y, 9, 1))
        e = _to_date(end, today + timedelta(days=30))
        return self._get("/api/ej/plan/family/v1/test_lessons/period", {
            "student_profile_id": self.ids["student_id"], "student_person_id": self.ids["person_id"],
            "from": s.isoformat(), "to": e.isoformat()}).get("items", [])

    def food(self, start: DateLike = None, end: DateLike = None) -> dict:
        """
        Питание (только чтение): баланс карты, дневной лимит, дни питания и заказы.
        Суммы портал отдаёт в копейках: balance_rub и day_limit_rub уже в рублях.
        Меню блюд в API дневника отдельным запросом не найдено: оно появляется
        только в предзаказе, а оформлять заказ модуль не умеет и не будет.
        """
        pid = json.dumps({"personId": self.ids["person_id"]}, separators=(",", ":"))
        bal = self._get("/api/food/meals/v3/clients/balance",
                        {"clientIds": json.dumps([{"personId": self.ids["person_id"]}], separators=(",", ":"))})
        state = self._get("/api/food/meals/v3/clients/allowed-food-state", {"clientId": pid})
        s = _to_date(start)
        e = _to_date(end, s)
        orders = self._get("/api/food/meals/v3/orders", {
            "clientId": pid, "from": s.isoformat(), "to": e.isoformat(), "limit": 50})
        b = bal[0] if bal else {}
        limit = (b.get("expenseConstraints") or {}).get("expenseDayLimit")
        return {
            "balance_rub": round(b["balance"] / 100, 2) if b.get("balance") is not None else None,
            "day_limit_rub": round(limit / 100, 2) if limit is not None else None,
            "feeding_week": state.get("feedingWeek"),
            "discounted_meals": state.get("discountedMeals"),
            "orders": orders.get("orders", []),
        }

    # ------------------------------------------------------------------
    # 📦 ВСЁ СРАЗУ
    # ------------------------------------------------------------------

    def snapshot(self, days: int = 7, back: int = 3, files: bool = False,
                 files_dir: Union[str, Path, None] = None) -> dict:
        """
        Снимок для ежедневной сводки: статус дня, домашка, расписание на сегодня и
        завтра, средний балл, рейтинг, оценки за неделю, посещаемость, питание.
        Отдельные блоки при ошибке заменяются на {'error': ...}, остальное не страдает.
        """
        def safe(fn):
            try:
                return fn()
            except Exception as ex:                          # noqa: BLE001
                return {"error": f"{type(ex).__name__}: {ex}"}

        today = date.today()
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "profile": safe(self.profile),
            "today": safe(self.school_day_status),
            "homework": safe(lambda: self.homework(days=days, back=back, files=files,
                                                   files_dir=files_dir)),
            "schedule_today": safe(lambda: self.schedule(today)),
            "schedule_tomorrow": safe(lambda: self.schedule(today + timedelta(days=1))),
            "marks_summary": safe(self.marks_summary),
            "marks_last_week": safe(lambda: self.marks(days=7)),
            "rating": safe(self.rating),
            "attendance_week": safe(self.attendance),
            "food": safe(self.food),
        }


# ======================================================================
# 🖥️ КОНСОЛЬ
# ======================================================================

def _print_homework(rows: List[dict]) -> None:
    if not rows:
        print("Заданий за выбранный период нет.")
        return
    cur = None
    for r in rows:
        if r["date"] != cur:
            cur = r["date"]
            print(f"\n=== {cur} ({DAY_NAMES[date.fromisoformat(cur).weekday()]}) ===")
        print(f"{'[x]' if r['is_done'] else '[ ]'} {r['subject']}  (урок {r['lesson_time']})")
        print(textwrap.fill(r["homework"] or "(без текста)", width=100,
                            initial_indent="    ", subsequent_indent="    "))
        for link in r["links"]:
            print(f"    ссылка: {link}")


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="mosru-diary", description="Дневник МЭШ (только чтение)")
    ap.add_argument("--data-dir", help="папка токена и профиля браузера (по умолчанию ~/.pycraft/mosru_diary)")
    ap.add_argument("--json", action="store_true", help="вывод в JSON")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("homework", help="домашние задания")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--back", type=int, default=0)
    p.add_argument("--undone", action="store_true", help="только невыполненные")
    p.add_argument("--files", action="store_true", help="скачать вложения и вытащить текст")
    p.add_argument("--save", help="сохранить результат в JSON-файл")
    p = sub.add_parser("schedule", help="расписание на день")
    p.add_argument("--date", help="ГГГГ-ММ-ДД (по умолчанию сегодня)")
    p.add_argument("--all", action="store_true", help="не только уроки, но и все события")
    p = sub.add_parser("marks", help="оценки и средний балл")
    p.add_argument("--days", type=int, default=0, help="за последние N дней (по умолчанию с 1 сентября)")
    sub.add_parser("final-marks", help="итоговые оценки")
    sub.add_parser("rating", help="место в рейтинге класса")
    sub.add_parser("attendance", help="посещаемость за неделю")
    sub.add_parser("food", help="питание: баланс, лимит, заказы")
    sub.add_parser("tests", help="контрольные и проверочные")
    sub.add_parser("school", help="школа, учителя")
    sub.add_parser("events", help="события школы")
    p = sub.add_parser("school-day", help="учебный ли день (код возврата 0 = да, 10 = нет)")
    p.add_argument("--date")
    p = sub.add_parser("snapshot", help="всё сразу для ежедневной сводки")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--back", type=int, default=3)
    p.add_argument("--files", action="store_true")
    p.add_argument("--save", help="сохранить результат в JSON-файл")
    sub.add_parser("login", help="войти вручную и обновить токен")
    sub.add_parser("status", help="состояние токена")
    args = ap.parse_args(argv)

    d = MosRuDiary(data_dir=args.data_dir, verbose=args.verbose)

    def out(obj: Any) -> None:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))

    try:
        if args.cmd == "login":
            d.login()
            print("Вход сохранён, токен обновлён.")
        elif args.cmd == "status":
            exp = d.token_expires_at()
            print("токена нет" if not exp else f"токен до {exp:%Y-%m-%d %H:%M} "
                  f"({'свежий' if d.has_fresh_token() else 'нужно обновить'})")
        elif args.cmd == "school-day":
            st = d.school_day_status(args.date)
            print(f"{st['date']}: {'учебный день' if st['school_day'] else 'не учебный'} ({st['reason']})")
            return 0 if st["school_day"] else 10
        elif args.cmd == "homework":
            rows = d.homework(days=args.days, back=args.back, only_undone=args.undone, files=args.files)
            if args.save:
                Path(args.save).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            out(rows) if args.json else _print_homework(rows)
        elif args.cmd == "schedule":
            rows = d.schedule(args.date, lessons_only=not args.all)
            if args.json:
                out(rows)
            else:
                for r in rows:
                    flag = " (отмена)" if r["cancelled"] else " (замена)" if r["replaced"] else ""
                    print(f"{r['start']}-{r['end']}  {r['subject']}  каб. {r['room']}{flag}")
                if not rows:
                    print("Уроков нет.")
        elif args.cmd == "marks":
            s = d.marks_summary(start=date.today() - timedelta(days=args.days) if args.days else None)
            if args.json:
                out(s)
            else:
                o = s["overall"]
                print(f"Всего оценок: {o['count']}, средний балл: {o['average']} (простой {o.get('average_plain')})")
                for name, st in s["subjects"].items():
                    print(f"  {name:<34} {st['count']:>3} шт.  ср. {st['average']}  {st['distribution']}")
        elif args.cmd == "snapshot":
            snap = d.snapshot(days=args.days, back=args.back, files=args.files)
            if args.save:
                Path(args.save).write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
            out(snap)
        else:
            fn = {"final-marks": d.final_marks, "rating": d.rating, "attendance": d.attendance,
                  "food": d.food, "tests": d.test_works, "school": d.school_info,
                  "events": d.school_events}[args.cmd]
            out(fn())
    except LoginRequired as ex:
        print(f"{ex}  Команда: mosru-diary login", file=sys.stderr)
        return 2
    except MosRuError as ex:
        print(f"Ошибка: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
