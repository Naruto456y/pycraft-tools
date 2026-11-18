# 🛠️ pycraft-tools — «швейцарский нож» для Python

Один пакет, в котором лежат **девять модулей**: главный `help_manager` (голос, музыка, автоматизация, база данных, экран, файлы, консоль) и восемь специальных: нейросети, распознавание речи, Яндекс.Музыка, умный дом Яндекса, Алиса (ТВ и колонки), робот Makerzoid, дневник МЭШ и VPN-клиент Happ.

```bash
pip install pycraft-tools
```

## 📑 Содержание

1. [Установка и extras](#-установка-и-extras)
2. [Быстрый старт](#-быстрый-старт)
3. [help_manager: главный модуль](#-help_manager-главный-модуль)
4. [ai_modules: нейросети](#-ai_modules-нейросети)
5. [voice_recognition: распознавание речи](#-voice_recognition-распознавание-речи)
6. [yandex_music_tools: лайки Яндекс.Музыки](#-yandex_music_tools-лайки-яндексмузыки)
7. [yandex_smart_home: умный дом](#-yandex_smart_home-умный-дом)
8. [makerzoid_robot: робот по Bluetooth](#-makerzoid_robot-робот-по-bluetooth)
9. [mosru_diary: дневник МЭШ](#-mosru_diary-дневник-мэш)
10. [happ_vpn: VPN-клиент Happ](#️-happ_vpn-vpn-клиент-happ)
11. [Секреты и безопасность](#-секреты-и-безопасность)

---

## 📦 Установка и extras

Код всех модулей приходит в одном пакете. Зависимости отдельных модулей ставятся по имени модуля в квадратных скобках:

```bash
pip install pycraft-tools[makerzoid_robot]     # bleak, python-dotenv
pip install pycraft-tools[voice_recognition]   # pyaudio, vosk, tqdm, onnx-asr
pip install pycraft-tools[mosru_diary]         # requests, playwright
pip install pycraft-tools[yandex_smart_home]   # python-dotenv, flask
pip install pycraft-tools[yandex_music_tools]  # yandex-music
pip install pycraft-tools[ai_modules]          # requests
pip install pycraft-tools[all]                 # зависимости всех модулей сразу
```

Несколько сразу: `pip install pycraft-tools[makerzoid_robot,mosru_diary]`.

| Модуль | Для чего | Extra |
|---|---|---|
| `help_manager` | главный модуль: Manager, Voice, Music, Auto, Face, BazaDB, Console и другие | не нужен |
| `ai_modules` | GigaChat (Сбер): чат, картинки, файлы | `[ai_modules]` |
| `voice_recognition` | распознавание речи: Google, Vosk, GigaAM | `[voice_recognition]` |
| `yandex_music_tools` | скачать «Мне нравится» из Яндекс.Музыки | `[yandex_music_tools]` |
| `yandex_smart_home` | лампы, группы, сценарии Умного дома Яндекса | `[yandex_smart_home]` |
| `yandex_alice` | Яндекс ТВ и колонки с Алисой по Wi-Fi: голос, приложения, плеер, громкость | `[yandex_alice]` |
| `makerzoid_robot` | робот Makerzoid по Bluetooth LE | `[makerzoid_robot]` |
| `mosru_diary` | домашка, оценки, расписание из МЭШ | `[mosru_diary]` |
| `happ_vpn` | VPN-клиент Happ (Windows): статус, страна выхода, трафик и срок подписок, смена страны | не нужен |

> ℹ️ Если для модуля не хватает зависимости, импорт подскажет, какой extra поставить.

---

## 🚀 Быстрый старт

```python
from help_manager import Manager, Music, Auto, Console, BazaDB, Face

Manager.say("Привет, мир!")                      # озвучка
print(Manager.get_weather("Москва"))             # погода
Console.success("Операция выполнена!")           # цветной вывод
Auto.screenshot("screen.png")                    # скриншот

db = BazaDB("test.db")
db.create_table("users", ["name", "age"])
db.insert("users", {"name": "Юсуф", "age": "12"})
print(db.get_all("users"))
```

---

## 🧰 help_manager: главный модуль

Всё в одном файле, все классы можно импортировать так: `from help_manager import *`.

```python
from help_manager import *
```

### 🌐 Manager: голос, погода, файлы, время, интернет

Набор статических методов «на каждый день».

```python
Manager.say("Привет!", "ru")                       # озвучка через Google TTS
text = Manager.listen_text(5)                      # слушает микрофон 5 секунд, возвращает текст
Manager.play_music("sound.mp3")                    # проиграть файл

Manager.get_weather("Москва")                      # погода (OpenWeatherMap)
Manager.get_weather("Москва", api_key="ВАШ_КЛЮЧ")  # со своим ключом
Manager.get_text_with_url("https://example.com", "title")   # текст со страницы по CSS-классу

Manager.now("%H:%M")                               # текущее время по формату
Manager.today()                                    # сегодняшняя дата
Manager.is_connected()                             # есть ли интернет
Manager.download_file("https://site/file.zip", "file.zip")

Manager.save_json("data.json", {"a": 1})           # JSON-файлы
data = Manager.load_json("data.json")
Manager.load_env(".env")                           # переменные из .env

Manager.search_and_open_youtube("Imagine Dragons", 1)   # найти и открыть видео
Manager.wait(3, "Подождите")                       # пауза с сообщением
Manager.beep(1000, 300)                            # звуковой сигнал
```

### 🎙️ Voice: все движки речи в одном классе

Озвучка (`gtts`, `silero`, `edge`, `pyttsx3`) и распознавание (`google`, `vosk`, `gigaam`, `whisper`). Движки ставятся только по необходимости, нужное покажет `Voice.check()`.

```python
Voice.check()                                       # что установлено, чего не хватает
Voice.say("Привет, я Кеша!")                        # gTTS по умолчанию
Voice.say("Привет!", engine="silero", voice="aidar", pitch_shift=-2)   # офлайн-нейроголос
Voice.say("В файл", engine="edge", save_path="hello.mp3", play=False)

Voice.use(tts="silero", stt="vosk")                 # выбрать движки по умолчанию
text = Voice.listen(seconds=5)                      # распознавание выбранным движком
text = Voice.listen("vosk", grammar=["включи свет", "выключи свет"])   # только команды
Voice.transcribe_file("record.wav", engine="whisper")                  # речь из файла
```

У любой озвучки есть `speed` (темп), `pitch_shift` (тембр в полутонах) и `gain` (громкость). Для темпа и тембра нужен `ffmpeg`; для записи и воспроизведения `numpy`, `soundfile`, `sounddevice`.

### 🎵 Music: плеер Яндекс.Музыки на VLC

Нужны токен Яндекс.Музыки и установленный VLC. Токен можно передать в конструктор или задать переменной `YANDEX_MUSIC_TOKEN`.

```python
player = Music(token="y0_...")
player.play("Imagine Dragons")        # найти и включить трек
player.pause(); player.next(); player.prev()
player.volume(60); player.volume_up(); player.volume_down()

player.add_to_queue("Miyagi - Captain")   # очередь
player.show_queue(); player.clear_queue()

player.play_my_wave(limit=15)         # случайные из избранного
player.play_favorites(limit=20)
player.mood("happy", limit=10)        # музыка под настроение
player.download_favorites("C:/MyMusic")   # скачать всё избранное
print(player.get_current_track())
```

### 🖱️ Auto: мышь, клавиатура, скриншоты, уведомления

```python
Auto.click(500, 300)                  # клик
Auto.double_click(500, 300)
Auto.move(100, 100, duration=0.5)
Auto.drag(100, 100, 400, 400)         # перетащить
Auto.scroll(-300)                     # прокрутка

Auto.write("Привет!", delay=0.05)     # печатает текст
Auto.press("enter")                   # нажать клавишу
Auto.screenshot("screen.png")         # скриншот
Auto.notify("Готово", "Задача завершена")   # уведомление Windows
```

### 🖥️ ScreenReader: что на экране

```python
pos = ScreenReader.find_image("button.png", confidence=0.8)     # поиск картинки
ScreenReader.wait_for_image("ok.png", timeout=10)               # дождаться появления
ScreenReader.find_color((255, 0, 0), tolerance=10)              # пиксель по цвету
ScreenReader.find_text_coordinates("Отправить")                 # текст на экране (EasyOCR)
ScreenReader.highlight_image("button.png", duration=2)          # обвести рамкой
```

### 🧠 Face: эмоции и улыбка с камеры

```python
emotion = Face.detect_emotion()       # 'happy', 'sad', 'angry'...
if Face.detect_smile():
    print("Улыбка!")
Face.music_by_mood(player)            # включить музыку под настроение (player = Music)
```

### 🗄️ BazaDB: SQLite без SQL

```python
db = BazaDB("school.db")
db.create_table("students", ["name", "grade"])
db.insert("students", {"name": "Юсуф", "grade": "8"})
db.get_all("students")
db.find("students", "name", "Юсуф")       # точное совпадение
db.search("students", "name", "Юс")       # поиск по части (LIKE)
db.update("students", 1, {"grade": "9"})
db.delete("students", 1)
db.stats("students"); db.show_tables(); db.close()
```

### 🖥️ Console: красивый вывод

```python
Console.success("Готово!"); Console.error("Ошибка"); Console.warning("Внимание"); Console.info("Инфо")
Console.header("Заголовок")
print(Console.color("Красный текст", "red"))
Console.progress_bar(100, "Загрузка")
w, h = Console.size()
Console.hide()                            # скрыть окно консоли (Windows)
```

### 🔧 Остальные классы

| Класс | Что делает | Пример |
|---|---|---|
| `Web` | открыть сайт, поиск, YouTube | `Web.search("погода")` |
| `System` | выключение, перезагрузка, сон, блокировка | `System.lock()` |
| `Info` | батарея, CPU, RAM, ОС | `Info.battery()` |
| `FolderUtils` | папки и файлы: создать, копировать, найти, размер | `FolderUtils.find_files("C:/docs", ".pdf")` |
| `FileUtils` | чтение, запись, подсчёт строк | `FileUtils.read_text("a.txt")` |
| `ImageUtils` | ресайз, обрезка, поворот | `ImageUtils.resize("a.jpg", "b.jpg", 800, 600)` |
| `PDFUtils` | текст из PDF | `PDFUtils.extract_text("book.pdf")` |
| `Clipboard` | буфер обмена | `Clipboard.copy("текст")` |
| `MathHelper` | факториал, среднее, медиана, школьное округление | `MathHelper.school_round(2.5)` |
| `PasswordGen` | генератор паролей | `PasswordGen.generate(16)` |
| `UnitConverter` | температура, расстояния, вес | `UnitConverter.km_to_miles(10)` |
| `ThreadManager` | фоновые потоки | `ThreadManager().start(func)` |
| `ImportManager` | импорт модулей по пути | `ImportManager.import_module("path/to/file.py")` |
| `GigaChat` | клиент GigaChat (тот же, что в `ai_modules`) | см. ниже |

---

## 🤖 ai_modules: нейросети

Клиенты ИИ-сервисов. Сейчас есть `GigaChat` (Сбер), другие провайдеры добавляются отдельными файлами. Нужны ключи из кабинета разработчика Сбера (`GIGACHAT_CLIENT_ID` и `GIGACHAT_CLIENT_SECRET` в окружении или `.env`).

```python
from ai_modules import GigaChat

ai = GigaChat(remember=True, system_prompt="Отвечай коротко")

print(ai.chat("Как дела?"))                       # ответ с памятью диалога
for part in ai.chat_stream("Расскажи анекдот"):   # ответ по кусочкам
    print(part, end="")

print(ai.describe_image("photo.jpg", style="brief"))           # описание картинки
print(ai.ask_image("Сколько людей на фото?", "photo.jpg"))     # вопрос по картинке
ai.generate_image("рыжий кот в скафандре", save_path="cat.jpg")

print(ai.clean_speech("я э-э-э хочу пиццу"))      # очистка распознанной речи
print(ai.count_tokens("Привет, мир"), ai.get_balance())
```

Методы: `chat`, `chat_stream`, `reset_history`, `ask_image`, `describe_image`, `generate_image`, `upload_file`, `list_files`, `get_file_info`, `download_file`, `delete_file`, `count_tokens`, `get_balance`, `list_models`, `embeddings`, `clean_speech`. Ошибки API: `GigaChatError` с полями `status_code` и `body`.

> ⚠️ `verify_ssl=False` по умолчанию. Для боевого кода передайте `ca_bundle="сертификат_Минцифры.pem"`.

---

## 🎙️ voice_recognition: распознавание речи

Один интерфейс для трёх движков, выбор строкой.

| Движок | Где | Особенности |
|---|---|---|
| `google` | онлайн | проще всего, нужен интернет и микрофон |
| `vosk` | офлайн | модель скачивается сама (small ~80 МБ), wake-word, потоковое распознавание |
| `gigaam` | офлайн | GigaAM v3 (ONNX, INT8), принимает аудио (файл или PCM) |

```bash
pip install pycraft-tools[voice_recognition]
```

```python
from voice_recognition import create_recognizer

# 1. Google: слушает микрофон
rec = create_recognizer("google", language="ru-RU")
print(rec.listen(timeout=5, phrase_limit=5))     # текст в нижнем регистре или ""

# 2. Vosk: офлайн
rec = create_recognizer("vosk", model_name="small")   # "large" ~2 ГБ
print(rec.listen())

# 3. GigaAM: распознать файл или сырой звук
rec = create_recognizer("gigaam")
print(rec.recognize_file("speech.wav"))
print(rec.recognize(pcm_bytes))                  # PCM int16, mono, 16 кГц
```

`VoskRecognizer` умеет больше: `recognize_from_file`, `recognize_stream` с колбэками, `set_wake_words`, `stop_listening`. `GigaAMEngine.listen()` не реализован: записывайте звук сами и передавайте в `recognize()`. Модель GigaAM скачивается с HuggingFace при первом запуске (~225 МБ).

---

## 🎵 yandex_music_tools: лайки Яндекс.Музыки

Скачивает весь раздел «Мне нравится» в папку. Токен в аргументе или в переменной `YANDEX_MUSIC_TOKEN`.

```python
from yandex_music_tools import YandexMusic

ym = YandexMusic()                        # токен из YANDEX_MUSIC_TOKEN
print(len(ym.likes()), "треков в лайках")

downloaded, failed = ym.download_likes(output_dir="./YandexMusic", delay=1.0, retries=3)
print(f"Скачано: {downloaded}, ошибок: {failed}")
```

Файлы называются `Артисты - Название.mp3`, уже скачанные пропускаются, пауза `delay` защищает от лимитов Яндекса.

---

## 🏠 yandex_smart_home: умный дом

Лампы, группы и сценарии Яндекса. Перед командой модуль проверяет, что устройство её умеет. Токен лежит в `.env`:

```
SMART_HOME_TOKEN=y0_...
```

```python
from dotenv import load_dotenv
from yandex_smart_home import SmartHome, SmartHomeError

load_dotenv()
home = SmartHome()

for dev in home.devices:
    print(dev.name, dev.is_on, dev.brightness, dev.temperature)

home.device("Саске").turn_on()
home.device("Саске").set_brightness(50)          # 1-100 %
home.device("Саске").set_temperature(4000)       # 2700-6500 K
home.group("Верхний свет").turn_off()            # группа
home.scenario("Я дома").run()                    # сценарий
home.turn_off_all_lights()                       # весь свет

try:
    home.device("Яндекс ТВ").turn_on()
except SmartHomeError as e:
    print("Не вышло:", e)
```

Веб-панель: `python -m yandex_smart_home.smart_home_web` (нужен extra `[yandex_smart_home]`). Панель без пароля, держите её только в домашней сети.

---

## 🗣️ yandex_alice: Яндекс ТВ и колонки

Команды идут напрямую в устройство по локальному протоколу Glagol (`wss://IP:1961`), ноутбук и устройство должны быть в одной Wi-Fi сети. Нужен токен **Яндекс Музыки** (токен умного дома не подходит), получить: [oauth.yandex.ru](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d).

```
GLAGOL_TOKEN=y0_...
```

```python
from dotenv import load_dotenv
from yandex_alice import Alice, AliceError

load_dotenv()
alice = Alice()

print(alice.devices)                      # ТВ и колонки в сети
alice.tv.open_app("YouTube")              # приложение на ТВ
alice.speaker.say("Ужин готов!")          # произнести фразу
alice.tv.command("включи канал Пятница")  # любая команда Алисе
alice.tv.set_volume(30)                   # 0-100 %
alice.tv.pause(); alice.tv.play()         # плеер: pause/play/next/prev/rewind
print(alice.speaker.get_state())          # громкость, играет ли, название трека
alice.say_everywhere("Всем привет!")      # на всех устройствах

try:
    alice.device("Кухня").say("Привет")
except AliceError as e:
    print("Не вышло:", e)
```

---

## 🤖 makerzoid_robot: робот по Bluetooth

Два мотора и две лампы по Bluetooth LE. Методы обычные, без `await`. MAC и UUID берутся из `.env` (`ROBOT_MAC`, `ROBOT_UUID`) или из аргументов конструктора.

```python
import time
from dotenv import load_dotenv
from makerzoid_robot import Robot, RobotError

load_dotenv()
bot = Robot()
bot.connect()                  # только подключается, ничего не выключает

bot.light1(3)                  # свет 1, цвет 1-7
bot.light2(5)                  # свет 2, свет 1 не гаснет
bot.forward(5)                 # скорость 0-10
time.sleep(2)
bot.turn_left(4); time.sleep(1)
bot.stop()

bot.send(m1=7, m2=7, l1=2, l2=6)    # моторы и свет одной командой
bot.disconnect(restore=True)        # всё выключить и отключиться
```

Остальное: `backward`, `turn_right`, `motor1`, `motor2`, `light_off`, `restore`, `init` (если робот не отвечает), `send_raw`. В коде остался MAC моего робота «по умолчанию»: укажите свой.

---

## 📘 mosru_diary: дневник МЭШ

Читает электронный дневник school.mos.ru **без открытия браузера**: домашка с вложениями, расписание, оценки и средний балл, рейтинг, посещаемость, каникулы, питание.

> ⚠️ Только чтение: ничего не отмечается, не отправляется и не заказывается. Логин, пароль и SMS не вводятся и не хранятся: первый вход вы делаете сами в окне браузера.

```bash
pip install pycraft-tools[mosru_diary]
```

```python
from mosru_diary import MosRuDiary

d = MosRuDiary(data_dir=r"C:\Users\Me\.session")   # тут хранится токен (не коммитьте папку!)
d.login()                                          # один раз: вход вручную в окне браузера

d.school_day_status()                              # {'school_day': True, 'vacation': False, ...}
d.homework(days=7, only_undone=True, files=True)   # невыполненная домашка + вложения
d.schedule("2026-10-23")                           # уроки: время, кабинет, замены
d.marks_summary()                                  # средний балл по предметам
d.rating()                                         # место в классе
d.attendance(); d.food()                           # посещаемость; баланс питания
d.menu("2026-11-05")                               # меню столовой: комплексы, цены, блюда
d.snapshot()                                       # всё сразу, удобно для ежедневной сводки
```

Консоль:

```bash
mosru-diary --data-dir .session homework --days 7 --files
mosru-diary --data-dir .session school-day      # код возврата 0 = учебный день, 10 = нет
mosru-diary --data-dir .session snapshot --save snapshot.json
```

Токен (JWT) живёт 24 часа и обновляется сам: на несколько секунд поднимается ваш браузер с сохранённым профилем. Неофициальный клиент: портал может изменить API. Подробный список методов смотрите в `mosru_diary/README.md` в репозитории.

---

## 🛡️ happ_vpn: VPN-клиент Happ

Управляет установленным [Happ](https://www.happ.su/main/ru) на Windows: показывает, подключён ли VPN и TUN, через какую страну вы выходите, сколько трафика и дней осталось у каждой подписки, умеет включать и выключать VPN и переключать страны. Зависимостей нет, хватает стандартной библиотеки.

> 🔒 Ссылки подписок модуль берёт из лога Happ и держит только в памяти: в выводе показывается лишь домен.

```python
from happ_vpn import Happ

happ = Happ()
happ.status()            # {'connected': True, 'tun': True, 'server': 'Швеция', 'ip': '...', 'country': 'Sweden', ...}
for sub in happ.subscriptions():
    print(sub.info())    # {'title': 'Nova VPN', 'download_gb': 490.2, 'left_gb': None, 'days_left': 47, ...}

happ.connect(); happ.disconnect(); happ.toggle()   # через ссылки happ://

# 🔄 Смена страны: сначала один раз выбрать каждую страну в окне Happ и запомнить
happ.remember()          # запомнил текущий сервер
happ.switch("Швеция")    # бэкап реестра → перезапуск Happ с нужным сервером
happ.next()              # следующая запомненная страна (удобно при лимитах по IP)
```

Консоль:

```bash
happ-vpn status          # VPN, TUN, сервер, IP и страна выхода
happ-vpn info            # трафик и срок подписок
happ-vpn remember        # запомнить текущий сервер
happ-vpn switch Швеция   # переключиться
happ-vpn next            # следующая страна
happ-vpn on | off        # подключить / отключить
```

> ⚠️ У Happ нет API для выбора сервера: `switch()` пишет сервер в реестр и перезапускает Happ, VPN пропадает примерно на 18 секунд. Перед этим делается бэкап в `%LOCALAPPDATA%\pycraft_happ\backups`. Если Happ не взял сервер из реестра, будет понятная ошибка.

---

## 🔒 Секреты и безопасность

- Токены и ключи держите в переменных окружения или в `.env`, а `.env` добавьте в `.gitignore`. Никогда не вставляйте их в код.
- `mosru_diary` хранит токен только локально в `data_dir`. Не отправляйте файл `mesh_auth.json` никому.
- Если ключ или токен когда-то попал в код, чат или публичный репозиторий, выпустите новый.

## 📄 Лицензия
MIT © 2026 Yusuf Guseinov

## 🌐 Ссылки
[PyPI](https://pypi.org/project/pycraft-tools/)

[GitHub](https://github.com/Naruto456y/pycraft-tools)
