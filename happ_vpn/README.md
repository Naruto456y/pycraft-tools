# 🛡️ happ_vpn — VPN-клиент Happ из Python (PyCraft Tools)

Управляет установленным [Happ](https://www.happ.su/main/ru) на Windows: показывает, подключён ли VPN и TUN, через какую страну вы выходите, сколько трафика и дней осталось у каждой подписки, включает и выключает VPN, переключает страны. Всё в одном файле `happ_vpn.py`, зависимостей нет: хватает стандартной библиотеки Python.

> 🔒 Ссылки подписок модуль берёт из лога Happ и держит только в памяти. В выводе и в `repr` показывается лишь домен провайдера.

## 🚀 Установка

```bash
pip install pycraft-tools            # extra не нужен
pip install pycraft-tools[happ_vpn]  # то же самое, для единообразия
```

Нужны Windows и установленный Happ.

## ⚙️ Как это работает

Happ состоит из окна (Qt), службы `HappService` и двух ядер:

```
Happ.exe → HappService → sing-box (TUN happ-tun) → xray (127.0.0.1:10808 socks / 10809 http) → сервер
```

API у ядер нет, поэтому модуль работает так:

| Что | Откуда |
|---|---|
| VPN включён, TUN работает | процессы `xray.exe` и `sing-box.exe` |
| Текущий сервер | реестр `HKCU\Software\Happ\OrganizationDefaults\Preferences` |
| IP и страна выхода | ip-api.com |
| Трафик и срок подписки | заголовок `Subscription-Userinfo` по ссылке подписки |
| Вкл / выкл VPN | ссылки `happ://connect`, `happ://disconnect`, `happ://toggle` |
| Смена страны | реестр + перезапуск Happ (🧪 экспериментально) |

## 💻 Python

```python
from happ_vpn import Happ, HappError

happ = Happ()

happ.status()
# {'happ_running': True, 'connected': True, 'tun': True,
#  'server': 'Казахстан', 'ip': '...', 'country': 'Kazakhstan', 'city': 'Almaty'}

for sub in happ.subscriptions():
    print(sub.info())
# {'title': 'Nova VPN', 'upload_gb': 0.0, 'download_gb': 490.21, 'total_gb': 0.0,
#  'left_gb': None, 'expire': datetime.date(2027, 1, 4), 'days_left': 47}
# total_gb = 0 и left_gb = None значат безлимит

happ.connect(); happ.disconnect(); happ.toggle()
happ.open(); happ.close(); happ.start()
```

### 🔄 Смена страны

Happ хранит серверы в зашифрованной базе, поэтому каждую страну нужно один раз «выучить»: выбрать её в окне Happ и вызвать `remember()`.

```python
happ.remember()          # выбрал «Швеция» в Happ → запомнил
happ.servers()           # ['Казахстан', '🇸🇪 Швеция ⭐', ...]

happ.switch("швец")      # по части имени, без учёта регистра и флагов
happ.next()              # следующая выученная страна по кругу
happ.backup()            # бэкап настроек Happ в .reg
```

`switch()` и `next()` делают так:

1. 💾 бэкап `HKCU\Software\Happ` в `%LOCALAPPDATA%\pycraft_happ\backups`;
2. 🚪 закрывают Happ (VPN пропадает на несколько секунд);
3. ✏️ записывают выбранный сервер в реестр;
4. 🚀 запускают Happ и отправляют `happ://connect`.

Если Happ стартовал не с тем сервером, будет `HappError` с объяснением. Восстановить настройки: двойной клик по `.reg` из папки бэкапов.

## ⌨️ Консоль

```bash
happ-vpn status          # VPN, TUN, сервер, IP и страна выхода
happ-vpn info            # трафик и срок всех подписок
happ-vpn remember        # запомнить текущий сервер
happ-vpn servers         # выученные серверы
happ-vpn switch Швеция   # переключиться
happ-vpn next            # следующая страна
happ-vpn on | off        # подключить / отключить
happ-vpn backup          # бэкап настроек Happ
```

Без установки пакета: `python happ_vpn.py status` из этой папки.

## 📁 Файлы модуля

| Файл | Что внутри |
|---|---|
| `%LOCALAPPDATA%\pycraft_happ\servers.json` | выученные серверы (GUID, имя, хост из реестра) |
| `%LOCALAPPDATA%\pycraft_happ\backups\*.reg` | бэкапы реестра перед каждым переключением |

## ⚠️ Ограничения

- Неофициальный способ: новая версия Happ может поменять реестр или лог.
- Отдельно включать и выключать TUN нельзя: в настройках Happ нет такого флага, только `happ://toggle` для всего VPN.
- Некоторые провайдеры (с проверкой HWID) без заголовков Happ отдают заглушку вместо серверов. На `info()` это не влияет: трафик и срок приходят в заголовке.
- Если напрямую сеть недоступна, запросы идут через локальный прокси Happ `127.0.0.1:10809` (меняется параметром `Happ(http_proxy=...)`).

## 📄 Лицензия

MIT, см. [LICENSE](LICENSE).
