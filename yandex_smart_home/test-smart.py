from dotenv import load_dotenv
from yandex_smart_home import SmartHome, SmartHomeError

load_dotenv()
home = SmartHome()

# Список устройств
for dev in home.devices:
    print(f"{dev.name:15} | вкл={dev.is_on} | яркость={dev.brightness} | темп={dev.temperature}")

# Проверки возможностей
print(home.device("Саске").turn_off())    
time  # True
print(home.device("Саске").turn_on())       # True