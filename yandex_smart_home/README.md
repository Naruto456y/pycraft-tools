# 🏠 yandex_smart_home — Яндекс Умный Дом (PyCraft Tools)

Управление устройствами умного дома Яндекса из Python: включение и выключение ламп, яркость, цветовая температура, группы, сценарии и «выключить весь свет». Перед командой модуль проверяет, что устройство это умеет. Ещё есть небольшая веб-панель на Flask.

## 🚀 Установка

```bash
pip install pycraft-tools[yandex_smart_home]   # модуль + python-dotenv и flask для веб-панели
```

## 🔑 Токен

Нужен OAuth-токен для API умного дома (`api.iot.yandex.net`), он начинается с `y0_`. Положите его в `.env` рядом со скриптом:

```
SMART_HOME_TOKEN=y0_...
```

> 🔒 Файл `.env` в `.gitignore`. Никому не отправляйте токен и не вставляйте его в код. Если токен когда-то лежал в коде или попал в чат, выпустите новый.

## 💻 Примеры

```python
from dotenv import load_dotenv
from yandex_smart_home import SmartHome, SmartHomeError

load_dotenv()
home = SmartHome()                         # токен из SMART_HOME_TOKEN

for dev in home.devices:
    print(dev.name, dev.is_on, dev.brightness, dev.temperature)

home.device("Саске").turn_on()
home.device("Саске").set_brightness(50)    # 1-100 %
home.device("Саске").set_temperature(4000) # 2700-6500 K
home.group("Верхний свет").turn_off()
home.scenario("Я дома").run()
home.turn_off_all_lights()

try:
    home.device("Яндекс ТВ").turn_on()
except SmartHomeError as e:
    print(f"Не вышло: {e}")
```

| Класс | Что умеет |
|---|---|
| `SmartHome` | `devices`, `groups`, `scenarios`, `device(имя)`, `group(имя)`, `scenario(имя)`, `turn_off_all_lights()`, `custom_action()`, `refresh()` |
| `Device` | `turn_on/off/toggle`, `set_brightness`, `set_temperature`, `is_on`, `brightness`, `temperature` |
| `Group` | `turn_on/off`, `set_brightness`, `is_on`, `brightness` |
| `Scenario` | `run()` |
| `SmartHomeError` | нет устройства, не поддерживается функция, значение вне диапазона, ошибка сети |

## 🌐 Веб-панель

```bash
python smart_home_web.py
```

Токен читается из `.env`. Панель без авторизации, поэтому не открывайте её в интернет: только домашняя сеть.

## ⚠️ Ограничения

- Данные кэшируются: если что-то изменилось вне скрипта, вызовите `home.refresh()`.
- Это неофициальная обёртка над API Яндекса.
