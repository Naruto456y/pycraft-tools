"""
🧪 ТЕСТЕР mosru_diary: проверяет все методы на живых данных (нужен вход в МЭШ).

Запуск:
    set MOSRU_DATA_DIR=C:\\Users\\Yusuf\\Programming\\Python\\.session
    python test_mosru_diary.py
"""

import os
import sys
from datetime import date, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")      # эмодзи в консоли cp1251

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mosru_diary import MosRuDiary, LoginRequired  # noqa: E402

passed = failed = 0


def test(name, func):
    global passed, failed
    try:
        result = func()
        print(f"  ✅ {name}: {str(result)[:90]}")
        passed += 1
        return result
    except LoginRequired:
        print("  ⛔ нужен вход: mosru_diary.py login")
        sys.exit(2)
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ {name}: {type(e).__name__}: {e}")
        failed += 1


d = MosRuDiary(data_dir=os.environ.get("MOSRU_DATA_DIR"))
today = date.today()

print("🔐 Токен")
test("токен свежий", lambda: d.has_fresh_token() or d.ensure_auth() and True)
test("профиль без личных данных", lambda: (lambda p: p if "phone" not in p and "snils" not in p else 1 / 0)(d.profile()))

print("📅 Дни")
test("статус сегодня", d.school_day_status)
test("выходной (суббота)", lambda: d.school_day_status(today + timedelta((5 - today.weekday()) % 7 or 7)))
test("праздник 4 ноября", lambda: d.school_day_status(f"{today.year}-11-04"))
test("периоды", lambda: len(d.periods()))

print("📚 Домашка")
hw = test("homework за 14 дней", lambda: len(d.homework(back=14, days=0)))
test("только невыполненные", lambda: len(d.homework(back=14, days=0, only_undone=True)))
test("с файлами", lambda: sum(len(r["files"]) for r in d.homework(back=14, days=0, files=True)))

print("🕒 Расписание")
test("расписание на пятницу", lambda: len(d.schedule(today - timedelta((today.weekday() - 4) % 7 or 7))))

print("🎓 Оценки")
test("оценки", lambda: len(d.marks()))
test("средний балл", lambda: d.marks_summary()["overall"]["average"])
test("итоговые", lambda: len(d.final_marks()))
test("рейтинг", lambda: d.rating()["place"])

print("🏫 Школа")
test("посещаемость", lambda: d.attendance()["days_count"])
test("проходы", lambda: len(d.visits()))
test("контрольные", lambda: len(d.test_works()))
test("питание", lambda: d.food()["balance_rub"])
test("школа", lambda: d.school_info()["name"])
test("события", lambda: len(d.school_events()))
test("проекты", lambda: len(d.projects()))
test("учебники", lambda: len(d.books()))
test("геймификация", d.gamification)

print("📦 Всё сразу")
snap = test("snapshot", lambda: [k for k, v in d.snapshot().items() if isinstance(v, dict) and "error" in v] or "без ошибок")

print(f"\nИтог: ✅ {passed}  ❌ {failed}")
sys.exit(1 if failed else 0)
