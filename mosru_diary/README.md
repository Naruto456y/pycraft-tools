# 📘 mosru_diary — дневник МЭШ (PyCraft Tools)

Читает электронный дневник МЭШ (school.mos.ru) **без открытия браузера**: домашка с вложениями, расписание со временем уроков, оценки и средний балл, рейтинг класса, посещаемость, каникулы и учебные дни, питание, контрольные. Всё в одном файле `mosru_diary.py`, как и `help_manager`.

> ⚠️ Модуль **только читает**. Он ничего не отмечает, не отправляет, не заказывает. Логин, пароль и SMS не вводятся и не хранятся: первый вход вы делаете сами.

## 🚀 Установка

```bash
pip install pycraft-tools[mosru_diary]   # модуль + requests и playwright (для обновления токена)
```

## ⚙️ Как это работает

1. Данные берутся обычными GET-запросами. Нужен токен (JWT на **24 часа**), он лежит в `<data_dir>/mesh_auth.json`.
2. Токен кончился: на несколько секунд поднимается ваш браузер (Яндекс/Chrome/Edge) с сохранённым профилем, портал выдаёт новый токен, кнопка «Войти» нажимается сама (по куки).
3. Вход в профиле протух: `LoginRequired`, и вы один раз делаете `login()` вручную.

Идентификаторы ученика берутся из `/profile` по токену и на диск не пишутся.

## 💻 Python

```python
from mosru_diary import MosRuDiary

d = MosRuDiary(data_dir=r"C:\Users\Me\.session")

d.school_day_status()                 # {'school_day': False, 'vacation': True, 'reason': 'каникулы 1', ...}
d.homework(days=7, only_undone=True, files=True)   # домашка + скачанные вложения и текст из .docx/.pptx
d.schedule("2026-10-23")              # время, кабинет, замены и отмены
d.marks_summary()                     # средний балл и количество оценок по каждому предмету
d.rating()                            # место в классе, динамика
d.food()                              # баланс карты, лимит, заказы (только чтение)
d.snapshot()                          # всё сразу для ежедневной сводки
```

| Метод | Что отдаёт |
|---|---|
| `school_day_status(day)` / `is_school_day` / `is_vacation` | учебный ли день: каникулы, праздники, переносы, выходные |
| `homework(start, end, days, back, only_undone, files)` | задания, время урока, ссылки, вложения |
| `schedule(start, end, lessons_only)` | уроки с `start`/`end`, кабинетом, `cancelled`/`replaced` |
| `marks(start, end)` / `marks_summary()` | оценки; средний балл (взвешенный и простой), количество, распределение |
| `final_marks()` | итоговые оценки |
| `rating()` | место в классе, средний балл класса, история места |
| `attendance()` / `visits()` | посещаемость и проходы в школу |
| `test_works()` | контрольные и проверочные |
| `food()` | баланс, лимит, дни питания, заказы |
| `school_info()` / `school_events()` | школа, учителя, события |
| `projects()` / `books()` / `gamification()` | проекты, учебники, баланс геймификации |
| `profile()` | безопасный профиль (без телефона, почты и СНИЛС) |
| `raw(path, params)` / `shape(path)` | любой GET к API и структура ответа (для новых методов) |

## 🖥️ Консоль

```bash
python mosru_diary.py --data-dir .session homework --days 7 --files
python mosru_diary.py --data-dir .session school-day    # код возврата 0 = учебный день, 10 = нет
python mosru_diary.py --data-dir .session marks
python mosru_diary.py --data-dir .session menu --date 2026-11-05   # меню столовой
python mosru_diary.py --data-dir .session snapshot --save snapshot.json
python mosru_diary.py --data-dir .session login          # ручной вход
```

После `pip install` команда называется `mosru-diary`.

## 🍽️ Про меню столовой

В API дневника есть баланс, лимит, дни питания и заказы. **Меню блюд отдельным запросом не найдено**: оно появляется только при предзаказе, а оформлять заказ модуль не умеет и не будет.

## 🔒 Безопасность

- Токен и профиль браузера лежат только в `data_dir`. Никогда не коммитьте эту папку (она в `.gitignore`).
- Не присылайте `mesh_auth.json` никому и никуда.
- Скачиваются только вложения с `school.mos.ru` (до 25 МБ).

## ⚠️ Ограничения

- Это неофициальный клиент: портал может изменить API.
- Старые форматы `.ppt` и `.doc` не разбираются (файл скачивается, текста не будет).
- Срок жизни входа в профиле браузера (кука `login.mos.ru`) заранее неизвестен.
