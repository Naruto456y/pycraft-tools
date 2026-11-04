# 🤖 makerzoid_robot — робот Makerzoid (PyCraft Tools)

Управление роботом Makerzoid по Bluetooth Low Energy: два мотора и две лампы. Внутри работает фоновый поток, поэтому все методы обычные, **без `await`**, как блоки в Scratch.

## 🚀 Установка

```bash
pip install pycraft-tools[makerzoid_robot]   # модуль + bleak и python-dotenv
```

## 🔑 Настройка

MAC-адрес и UUID характеристики берутся из `.env` (или передаются в конструктор):

```
ROBOT_MAC=AA:BB:CC:DD:EE:FF
ROBOT_UUID=6e400002-b5a3-f393-e0a9-e50e24dcca9e
```

> ⚠️ В коде остались адрес и UUID моего робота «по умолчанию». У вас будет свой MAC, укажите его в `.env`.

## 💻 Пример

```python
import time
from dotenv import load_dotenv
from makerzoid_robot import Robot, RobotError

load_dotenv()
bot = Robot()
bot.connect()              # только подключается, ничего не выключает

bot.light1(3)              # свет 1, цвет 3
bot.light2(5)              # свет 2, свет 1 не гаснет
bot.forward(5)             # скорость 0-10
time.sleep(2)
bot.stop()

bot.send(m1=7, m2=7, l1=2, l2=6)   # моторы и свет одной командой
bot.disconnect(restore=True)       # всё выключить и отключиться
```

| Метод | Что делает |
|---|---|
| `connect()` / `disconnect(restore=False)` | подключение и отключение |
| `motor1(v)` / `motor2(v)` | мотор: 0 стоп, 1..10 вперёд, -1..-10 назад |
| `forward` / `backward` / `turn_left` / `turn_right` / `stop` | движение |
| `light1(цвет)` / `light2(цвет)` / `light_off()` | свет: 0 выкл, 1..7 цвета |
| `send(m1, m2, l1, l2)` / `send_raw(data)` | своя команда или сырой пакет |
| `restore()` / `all_off()` | сбросить всё в ноль |
| `init()` | init-пакет, если робот не отвечает на команды |
| `is_connected` / `state` | текущее состояние |

## 📡 Протокол

Команда — 14 байт: `FF FE 09 01 02 [M1] [M2] 00 [L1] [L2] 00 00 FD FC`. Состояние запоминается, поэтому `light1` не гасит `light2`.

## ⚠️ Ограничения

- Проверено только на одном роботе. Нужен Bluetooth-адаптер с поддержкой BLE.
- Ошибки соединения поднимают `RobotError`.
