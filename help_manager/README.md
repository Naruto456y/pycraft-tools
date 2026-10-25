# 🛠️ pycraft-tools — универсальный модуль-помощник на Python

Модуль, который объединяет десятки функций и классов для работы с голосом, музыкой, автоматизацией, базами данных и искусственным интеллектом. Всё в одном файле — просто подключи и используй.

---

## 🚀 Возможности

### 🎙️ Голос и звук (Manager)
- Распознавание речи (speech-to-text)
- Озвучка текста (TTS) через Google
- Воспроизведение MP3/WAV/OGG
- Кроссплатформенные звуковые сигналы

### 🎵 Музыкальный плеер (Music)
- Поиск и воспроизведение треков из Яндекс.Музыки
- Управление очередью (добавление, переключение, очистка)
- Пауза, регулировка громкости, перемотка
- Запуск «Моей волны» (случайные треки из избранного)
- Скачивание всех треков из избранного в папку
- Кэширование ссылок и избранного (2 часа)

### 🌐 Парсинг и погода (Manager)
- Извлечение текста с веб-страниц по CSS-классу
- Получение текущей погоды для любого города (OpenWeatherMap)

### 🖥️ Консоль (Console)
- Цветной вывод (16 цветов + стили)
- Управление курсором, прогресс-бары
- Скрытие/показ окна консоли (Windows)
- Быстрые сообщения (success, error, warning, info)

### 🗄️ База данных SQLite (BazaDB)
- Создание таблиц, вставка, поиск (точный и LIKE), обновление, удаление
- Статистика и список таблиц

### 🧠 Распознавание лиц и эмоций (Face)
- Определение эмоции через веб-камеру (DeepFace)
- Обнаружение улыбки
- Автоматический запуск музыки под настроение

### 🖱️ Автоматизация (Auto)
- Клики, двойные клики, перетаскивание, скроллинг
- Нажатие и удержание клавиш
- Эмуляция печати текста
- Скриншоты и системные уведомления

### 💻 Системные команды (System)
- Выключение, перезагрузка, сон, блокировка экрана (Windows)

### ℹ️ Информация о системе (Info)
- Уровень заряда батареи, загрузка CPU, использование RAM, тип ОС

### 🖥️ Распознавание экрана (ScreenReader)
- Поиск изображения на экране (OpenCV)
- Поиск пикселя по цвету
- Чтение текста с экрана (EasyOCR)
- Выделение найденных объектов рамкой
- Ожидание появления изображения

### 🤖 Искусственный интеллект (GigaChat)
- Подключение к GigaChat Сбера
- Очистка распознанной речи от слов-паразитов и шума

### 🔧 Дополнительные утилиты
- **Буфер обмена** (Clipboard) — копирование/вставка
- **Математика** (MathHelper) — факториал, среднее, медиана, перевод систем, школьное округление
- **Файлы** (FileUtils) — чтение, запись, подсчёт строк
- **Изображения** (ImageUtils) — ресайз, кроп, поворот
- **PDF** (PDFUtils) — извлечение текста
- **Генератор паролей** (PasswordGen)
- **Конвертер единиц** (UnitConverter) — температура, расстояние, вес
- **Фоновые потоки** (ThreadManager)

---

## 📦 Установка

```bash
pip install pycraft-tools
```

Код всех модулей PyCraft приходит в одном пакете. Если для модуля нужны свои зависимости, поставьте их через extras (см. ниже), иначе импорт подскажет, чего не хватает:

```python
import help_manager
import ai_modules            # GigaChat и другие нейросети
import voice_recognition     # Google, Vosk, GigaAM
import yandex_music_tools    # скачивание лайков Яндекс.Музыки
import yandex_smart_home     # Умный дом Яндекса
import makerzoid_robot       # робот Makerzoid по Bluetooth
import mosru_diary           # дневник МЭШ
```

Зависимости отдельных модулей ставятся по имени модуля в квадратных скобках:

```bash
pip install pycraft-tools[makerzoid_robot]     # bleak, python-dotenv
pip install pycraft-tools[voice_recognition]   # pyaudio, vosk, tqdm, onnx-asr
pip install pycraft-tools[mosru_diary]         # requests, playwright
pip install pycraft-tools[yandex_smart_home]   # python-dotenv, flask
pip install pycraft-tools[yandex_music_tools]  # yandex-music
pip install pycraft-tools[ai_modules]          # requests
pip install pycraft-tools[all]                 # зависимости всех модулей сразу
```

Можно несколько сразу: `pip install pycraft-tools[makerzoid_robot,mosru_diary]`.

| Модуль | Что внутри |
|---|---|
| `help_manager` | главный модуль: Manager, Music, Auto, Face, BazaDB и другие |
| `ai_modules` | GigaChat и другие нейросети |
| `voice_recognition` | распознавание речи: Google, Vosk, GigaAM |
| `yandex_music_tools` | скачивание лайков Яндекс.Музыки |
| `yandex_smart_home` | Умный дом Яндекса |
| `makerzoid_robot` | робот Makerzoid по Bluetooth |
| `mosru_diary` | дневник МЭШ (есть консольная команда `mosru-diary`) |

## 🚀 Быстрый старт

```python
from help_manager import Manager, Music, Auto, Console, BazaDB, Face

# Голос
Manager.say("Привет, мир!")

# Погода
weather = Manager.get_weather("Москва")
print(weather["Температура"])

# Музыка (требуется токен Яндекс.Музыки)
player = Music(token="y0_...")
player.play("Imagine Dragons")
player.download_favorites("C:/MyMusic")  # скачать всё избранное

# Автоматизация
Auto.click(500, 300)
Auto.screenshot("screen.png")

# Консоль
Console.success("Операция выполнена!")
Console.progress_bar(100, "Загрузка")

# База данных
db = BazaDB("test.db")
db.create_table("users", ["name", "age"])
db.insert("users", {"name": "Юсуф", "age": "12"})

# Распознавание лиц
emotion = Face.detect_emotion()
print(f"Эмоция: {emotion}")
```

## 📄 Лицензия
MIT © 2026 Yusuf Guseinov

## 🌐 Ссылки
[PyPI](https://pypi.org/project/pycraft-tools/)

[GitHub](https://github.com/Naruto456y/pycraft-tools)