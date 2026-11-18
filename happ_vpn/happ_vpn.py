"""
🛡️ ================================================================
   Happ VPN — управление VPN-клиентом Happ на Windows из Python
   ================================================================

   📦 Что умеет модуль:
      ✅ Статус: запущен ли Happ, подключён ли VPN, работает ли TUN
      ✅ Текущий сервер (страна) и реальный IP / страна выхода
      ✅ Остаток трафика и дата окончания каждой подписки
         (заголовок Subscription-Userinfo)
      ✅ Подключить / отключить / переключить VPN (deeplink happ://)
      ✅ Запоминать серверы и переключаться между странами (switch / next)
      ✅ Бэкап настроек Happ из реестра перед любым изменением
      ✅ Консольная команда: happ-vpn status | info | switch Швеция | next

   🔌 Как работает:
      Happ — это GUI (Qt) + служба HappService. Под капотом ядро xray
      (локальный прокси 127.0.0.1:10808 socks / 10809 http) и sing-box,
      который поднимает TUN-адаптер happ-tun. API у ядра нет, поэтому:
        - статус читается из процессов и реестра HKCU\\Software\\Happ
        - подписки — из лога Happ (ссылки наружу НЕ выводятся)
        - сервер переключается через реестр + перезапуск Happ
      🧪 switch() экспериментальный: перед ним сервер нужно «выучить» —
      один раз выбрать его в Happ и вызвать remember().

   🔑 Токены не нужны: всё берётся из установленного Happ.
      Модуль работает только на Windows, зависимостей нет (stdlib).

   🚀 Быстрый старт:

      from happ_vpn import Happ

      happ = Happ()

      # 📊 Что сейчас: сервер, IP, страна выхода
      print(happ.status())

      # 📥 Сколько трафика и до какого числа подписки
      for sub in happ.subscriptions():
          print(sub.title, sub.info())

      # 🧠 Запомнить текущий сервер (сделать для каждой страны один раз)
      happ.remember()

      # 🔄 Переключиться на Швецию / на следующую страну
      happ.switch("Швеция")
      happ.next()
"""

import os
import re
import sys
import json
import time
import base64
import argparse
import datetime
import subprocess
import urllib.error
import urllib.request

try:
    import winreg
except ImportError:  # 🐧 не Windows — модуль импортируется, но Happ() скажет, что не так
    winreg = None


class HappError(Exception):
    """🚫 Ошибка при работе с Happ.

    Возникает, когда:
      - модуль запущен не на Windows или Happ не установлен
      - сервер с таким именем ещё не выучен (нужно remember())
      - подписка не ответила (сеть, 502, протухла)
      - Happ не удалось закрыть или запустить

    Пример перехвата:

        from happ_vpn import Happ, HappError

        try:
            Happ().switch("Япония")
        except HappError as e:
            print(f"Не вышло: {e}")
            # Выведет: "🔍 Сервер 'Япония' не выучен. Выбери его в Happ и вызови happ.remember() ..."
    """
    pass


class HappSubscription:
    """📋 Подписка Happ (ссылка от VPN-провайдера).

    Не создаётся вручную — получается через happ.subscriptions().
    Сама ссылка хранится только в памяти и в repr/str не попадает.

    Свойства:
      - id     — номер подписки в Happ (как в логе и в реестре)
      - title  — имя провайдера ("Nova VPN"), если известно
      - host   — домен сервера подписок (без пути и ключа)

    Методы:
      - info() — трафик и срок: upload, download, total, expire, days_left
    """

    def __init__(self, sub_id, url, title, happ):
        """🔧 Внутренний конструктор. Не вызывай напрямую — используй happ.subscriptions()"""
        self.id = sub_id
        self._url = url        # 🔒 секрет: наружу не отдаём
        self.title = title or ""
        self._happ = happ
        self.host = re.sub(r"^https?://([^/]+).*$", r"\1", url)

    def __repr__(self):
        return f"<HappSubscription {self.title or self.id} @ {self.host}>"

    # ================================================================
    #  ТРАФИК И СРОК
    # ================================================================

    def info(self):
        """📥 Трафик и срок подписки из заголовка Subscription-Userinfo.

        Делает один GET-запрос к ссылке подписки (как кнопка «Обновить» в Happ).
        Серверы из ответа не используются, только заголовки.

        Returns:
            dict: {
              "title": "Nova VPN",
              "upload_gb": 0.0, "download_gb": 490.2,
              "total_gb": 0.0,          # 0 = безлимит
              "left_gb": None,          # None = безлимит
              "expire": datetime.date | None,
              "days_left": 46 | None,
            }

        Пример:
            sub = happ.subscriptions()[0]
            print(sub.info()["days_left"], "дней осталось")

        Raises HappError, если подписка не ответила или нет заголовка.
        """
        headers = self._happ._fetch_headers(self._url)
        raw = headers.get("subscription-userinfo", "")
        if not raw:
            raise HappError(f"📭 Подписка {self!r} не прислала Subscription-Userinfo — провайдер не отдаёт трафик и срок")

        vals = {}
        for part in raw.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    vals[k.strip().lower()] = int(float(v.strip() or 0))
                except ValueError:
                    pass

        gb = lambda b: round(b / 2 ** 30, 2)
        up, down, total = vals.get("upload", 0), vals.get("download", 0), vals.get("total", 0)
        expire = None
        if vals.get("expire"):
            expire = datetime.date.fromtimestamp(vals["expire"])

        title = headers.get("profile-title", "") or self.title
        if title.startswith("base64:"):
            try:
                title = base64.b64decode(title[7:]).decode("utf-8", "replace")
            except ValueError:
                pass
        if title:
            self.title = title

        return {
            "title": self.title,
            "upload_gb": gb(up),
            "download_gb": gb(down),
            "total_gb": gb(total),
            "left_gb": gb(total - up - down) if total else None,
            "expire": expire,
            "days_left": (expire - datetime.date.today()).days if expire else None,
        }


class Happ:
    """🛡️ Главный класс: управление установленным Happ.

    Параметры:
      - http_proxy — локальный http-прокси xray (по умолчанию 127.0.0.1:10809),
                     через него идут запросы, если напрямую сеть недоступна

    Методы:
      - status()            — сводка: процессы, TUN, сервер, IP и страна выхода
      - current_server()    — имя текущего сервера из настроек Happ
      - exit_ip()           — реальный IP и страна выхода
      - subscriptions()     — список подписок (HappSubscription)
      - connect() / disconnect() / toggle() — VPN через deeplink
      - open() / close()    — показать окно / закрыть Happ
      - remember()          — запомнить текущий сервер для switch()
      - servers()           — список выученных серверов
      - switch(name)        — переключиться на сервер (🧪 через реестр + перезапуск)
      - next()              — следующий выученный сервер
      - backup()            — бэкап настроек Happ в .reg
    """

    REG_PATH = r"Software\Happ\OrganizationDefaults\Preferences"
    REG_ROOT = r"HKCU\Software\Happ"
    # 🧠 Поля реестра, которые описывают выбранный сервер
    SERVER_FIELDS = ("lastSubscription", "lastServer", "lastServerName",
                     "lastServerGuid", "lastServerHost", "lastServerPort")
    DEFAULT_EXE = r"C:\Program Files\FlyFrogLLC\Happ\Happ.exe"

    def __init__(self, http_proxy="http://127.0.0.1:10809"):
        """🔌 Находит Happ на компьютере.

        Args:
            http_proxy: адрес локального http-прокси Happ (xray)

        Пример:
            happ = Happ()

        Raises HappError, если не Windows или Happ не установлен.
        """
        if winreg is None or sys.platform != "win32":
            raise HappError("🪟 Модуль happ_vpn работает только на Windows")
        self.http_proxy = http_proxy
        self.exe = self._find_exe()
        self.data_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Happ")
        if not os.path.isfile(self.exe):
            raise HappError("📦 Happ не найден. Установи его: https://www.happ.su/main/ru")
        # 💾 свои файлы (выученные серверы, бэкапы) — отдельно от Happ
        self.own_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "pycraft_happ")
        self.servers_file = os.path.join(self.own_dir, "servers.json")

    # ================================================================
    #  СТАТУС
    # ================================================================

    def status(self, check_ip=True):
        """📊 Полная сводка о VPN.

        Args:
            check_ip: True — ещё и узнать IP/страну выхода (1 сетевой запрос)

        Returns:
            dict: {"happ_running", "connected", "tun", "server", "ip", "country", "city"}

        Пример:
            s = happ.status()
            print(s["server"], s["country"], "TUN" if s["tun"] else "прокси")
        """
        procs = self._processes()
        result = {
            "happ_running": "happ.exe" in procs,
            "connected": "xray.exe" in procs,     # 🔌 ядро живо = VPN подключён
            "tun": "sing-box.exe" in procs,       # 🕳️ sing-box поднимает TUN
            "server": self.current_server(),
            "ip": None, "country": None, "city": None,
        }
        if check_ip:
            try:
                result.update(self.exit_ip())
            except HappError:
                pass
        return result

    def current_server(self):
        """📍 Имя текущего сервера из настроек Happ (например "Казахстан").

        Returns:
            str или None, если сервер ещё не выбирался.

        Пример:
            print(happ.current_server())
        """
        return self._read_server().get("lastServerName", (None,))[0]

    def exit_ip(self):
        """🌍 Реальный IP и страна, под которыми тебя видят сайты.

        Returns:
            dict: {"ip": "1.2.3.4", "country": "Sweden", "city": "Stockholm"}

        Пример:
            print(happ.exit_ip()["country"])

        Raises HappError, если сеть недоступна.
        """
        data = json.loads(self._get("http://ip-api.com/json/?fields=query,country,city").decode("utf-8"))
        return {"ip": data.get("query"), "country": data.get("country"), "city": data.get("city")}

    # ================================================================
    #  ПОДПИСКИ
    # ================================================================

    def subscriptions(self):
        """📋 Подписки, которые Happ обновлял (из его лога).

        Returns:
            list[HappSubscription]

        Пример:
            for sub in happ.subscriptions():
                print(sub.title, sub.info()["days_left"])

        Raises HappError, если лог подписок не найден.
        """
        log = os.path.join(self.data_dir, "logs", "subscription_log.txt")
        if not os.path.isfile(log):
            raise HappError("📭 Лог подписок Happ не найден — обнови подписку в Happ хотя бы раз")
        with open(log, encoding="utf-8", errors="replace") as f:
            text = f.read()

        urls, titles = {}, {}
        for sub_id, url in re.findall(r"#(-?\d+) starting update from: (\S+)", text):
            urls[sub_id] = url  # 🔄 берём самую свежую ссылку
        # 🏷️ имя провайдера стоит в строке после "starting update"
        for sub_id, title in re.findall(r"#(-?\d+) starting update from: \S+\s*\n[^\n]*\[INFO\] (.+?) fetching", text):
            titles[sub_id] = title.strip()
        return [HappSubscription(int(i), u, titles.get(i), self) for i, u in urls.items()]

    # ================================================================
    #  УПРАВЛЕНИЕ (deeplink happ://)
    # ================================================================

    def connect(self):
        """✅ Подключить VPN (как кнопка в Happ).

        Пример:
            happ.connect()
        """
        self._deeplink("connect")

    def disconnect(self):
        """❌ Отключить VPN. Интернет пойдёт напрямую.

        Пример:
            happ.disconnect()
        """
        self._deeplink("disconnect")

    def toggle(self):
        """🔄 Переключить VPN: включён → выключить, выключен → включить.

        Пример:
            happ.toggle()
        """
        self._deeplink("toggle")

    def open(self):
        """🪟 Показать окно Happ.

        Пример:
            happ.open()
        """
        self._deeplink("open")

    def close(self, timeout=10):
        """🚪 Закрыть Happ (VPN при этом отключается).

        Args:
            timeout: сколько секунд ждать закрытия

        Пример:
            happ.close()

        Raises HappError, если Happ не закрылся.
        """
        if "happ.exe" not in self._processes():
            return
        self._deeplink("close")
        if self._wait(lambda: "happ.exe" not in self._processes(), timeout):
            return
        # 🔨 вежливо не вышло — просим Windows закрыть окно
        subprocess.run(["taskkill", "/IM", "Happ.exe"], capture_output=True)
        if not self._wait(lambda: "happ.exe" not in self._processes(), timeout):
            raise HappError("⏳ Happ не закрылся. Закрой его вручную из трея")

    def start(self, timeout=15):
        """🚀 Запустить Happ, если он не запущен.

        Args:
            timeout: сколько секунд ждать запуска

        Пример:
            happ.start()
        """
        if "happ.exe" in self._processes():
            return
        subprocess.Popen([self.exe], close_fds=True, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
        if not self._wait(lambda: "happ.exe" in self._processes(), timeout):
            raise HappError("⏳ Happ не запустился за отведённое время")

    # ================================================================
    #  СЕРВЕРЫ: ЗАПОМНИТЬ И ПЕРЕКЛЮЧИТЬ
    # ================================================================

    def remember(self):
        """🧠 Запомнить текущий сервер, чтобы потом на него переключаться.

        Happ хранит серверы в зашифрованной базе, поэтому каждую страну
        нужно один раз выбрать в Happ вручную и вызвать remember().

        Returns:
            str: имя запомненного сервера

        Пример:
            # выбрал «Швеция» в Happ →
            happ.remember()

        Raises HappError, если в Happ ещё не выбран сервер.
        """
        data = self._read_server()
        name = data.get("lastServerName", (None,))[0]
        if not name or "lastServerGuid" not in data:
            raise HappError("🤷 В Happ не выбран сервер — выбери страну в окне Happ")
        servers = self._load_servers()
        servers[name] = {k: list(v) for k, v in data.items()}
        self._save_servers(servers)
        return name

    def servers(self):
        """📋 Выученные серверы (имена) в порядке добавления.

        Пример:
            print(happ.servers())   # ['Казахстан', 'Швеция ⭐', ...]
        """
        return list(self._load_servers())

    def switch(self, name, connect=True):
        """🔄 Переключиться на сервер по имени (🧪 экспериментально).

        Что происходит: бэкап реестра → Happ закрывается → в реестр
        пишется выбранный сервер → Happ запускается → connect().
        VPN пропадает на несколько секунд.

        Args:
            name: часть имени сервера без учёта регистра ("швец", "США")
            connect: True — сразу подключить VPN

        Returns:
            str: полное имя сервера, на который переключились

        Пример:
            happ.switch("Швеция")

        Raises HappError, если сервер не выучен или Happ не перезапустился.
        """
        if not name or not name.strip():
            raise HappError("✏️ Укажи страну, например happ.switch('Швеция')")
        full = self._match(name)
        self._apply(full, connect)
        return full

    def next(self, connect=True):
        """⏭️ Переключиться на следующий выученный сервер по кругу.

        Удобно, когда на текущей стране упёрся в лимит сервиса.

        Returns:
            str: имя нового сервера

        Пример:
            happ.next()

        Raises HappError, если выучено меньше двух серверов.
        """
        names = self.servers()
        if len(names) < 2:
            raise HappError("📚 Для next() нужно хотя бы 2 выученных сервера — см. happ.remember()")
        cur = self.current_server()
        idx = names.index(cur) if cur in names else -1
        full = names[(idx + 1) % len(names)]
        self._apply(full, connect)
        return full

    def backup(self):
        """💾 Сохранить все настройки Happ из реестра в .reg-файл.

        Returns:
            str: путь к файлу бэкапа (восстановить — двойной клик по нему)

        Пример:
            print(happ.backup())
        """
        folder = os.path.join(self.own_dir, "backups")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, datetime.datetime.now().strftime("happ_%Y%m%d_%H%M%S.reg"))
        r = subprocess.run(["reg", "export", self.REG_ROOT, path, "/y"], capture_output=True)
        if r.returncode != 0:
            raise HappError("💾 Не удалось сделать бэкап реестра Happ — переключение отменено")
        return path

    # ================================================================
    #  ВНУТРЕННЕЕ
    # ================================================================

    def _find_exe(self):
        """🔧 Внутренний метод — путь к Happ.exe из обработчика ссылок happ://"""
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"happ\shell\open\command") as k:
                cmd = winreg.QueryValueEx(k, "")[0]
            m = re.match(r'"([^"]+)"', cmd)
            if m:
                return m.group(1)
        except OSError:
            pass
        return self.DEFAULT_EXE

    def _deeplink(self, action):
        """🔧 Внутренний метод — отправить команду happ://<action>"""
        try:
            os.startfile(f"happ://{action}")
        except OSError as e:
            raise HappError(f"🔗 Happ не принял команду happ://{action}: {e}") from e

    def _processes(self):
        """🔧 Внутренний метод — имена запущенных процессов (в нижнем регистре)"""
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                             text=True, encoding="cp866", errors="replace").stdout
        return {line.split('","')[0].strip('"').lower() for line in out.splitlines() if line}

    def _wait(self, check, timeout):
        """🔧 Внутренний метод — ждать, пока check() не станет True"""
        end = time.time() + timeout
        while time.time() < end:
            if check():
                return True
            time.sleep(0.5)
        return False

    def _read_server(self):
        """🔧 Внутренний метод — поля текущего сервера из реестра: {имя: (значение, тип)}"""
        data = {}
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH) as k:
                for field in self.SERVER_FIELDS:
                    try:
                        data[field] = winreg.QueryValueEx(k, field)
                    except OSError:
                        pass
        except OSError:
            pass
        return data

    def _load_servers(self):
        """🔧 Внутренний метод — прочитать servers.json"""
        try:
            with open(self.servers_file, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def _save_servers(self, servers):
        """🔧 Внутренний метод — записать servers.json"""
        os.makedirs(self.own_dir, exist_ok=True)
        with open(self.servers_file, "w", encoding="utf-8") as f:
            json.dump(servers, f, ensure_ascii=False, indent=2)

    def _match(self, name):
        """🔧 Внутренний метод — найти выученный сервер по части имени"""
        clean = lambda s: re.sub(r"[^\w#]+", " ", s.lower()).strip()
        want = clean(name)
        hits = [n for n in self.servers() if want in clean(n)]
        if not hits:
            raise HappError(f"🔍 Сервер '{name}' не выучен. Выбери его в Happ и вызови happ.remember(). "
                            f"Выучены: {', '.join(self.servers()) or 'пока ничего'}")
        exact = [n for n in hits if clean(n) == want]
        return (exact or hits)[0]

    def _apply(self, full_name, connect):
        """🔧 Внутренний метод — бэкап, закрыть Happ, записать сервер, запустить"""
        fields = self._load_servers()[full_name]
        self.backup()
        self.close()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
            for field, (value, kind) in fields.items():
                winreg.SetValueEx(k, field, 0, kind, value)
        self.start()
        if connect:
            time.sleep(3)  # ⏳ даём окну подняться, иначе deeplink запустит второй экземпляр
            self.connect()
            self._wait(lambda: "xray.exe" in self._processes(), 15)
        now = self.current_server()
        if now != full_name:
            raise HappError(f"🧪 Happ стартовал с сервером '{now}', а не '{full_name}'. "
                            f"Значит, он не берёт сервер из реестра — переключай в окне Happ")

    def _get(self, url, headers=None, want_headers=False, timeout=15):
        """🔧 Внутренний метод — GET напрямую, при сбое через локальный прокси Happ"""
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Happ/3.3.6/Windows"})
        last = None
        for proxy in ({}, {"http": self.http_proxy, "https": self.http_proxy}):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy))
            try:
                with opener.open(req, timeout=timeout) as r:
                    if want_headers:
                        return {k.lower(): v for k, v in r.headers.items()}
                    return r.read()
            except urllib.error.HTTPError as e:
                raise HappError(f"🌐 Сервер ответил {e.code} — подписка мёртвая или ссылка устарела") from e
            except (urllib.error.URLError, OSError) as e:
                last = e
        raise HappError(f"🌐 Ошибка сети: {last}") from last

    def _fetch_headers(self, url):
        """🔧 Внутренний метод — заголовки ответа подписки"""
        return self._get(url, want_headers=True)


# ================================================================
#  КОНСОЛЬНАЯ КОМАНДА happ-vpn
# ================================================================

def main(argv=None):
    """💻 Консольная команда: happ-vpn status | info | servers | remember | switch <страна> | next | on | off"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # 🇷🇺 эмодзи и флаги в консоли Windows
    p = argparse.ArgumentParser(prog="happ-vpn", description="Управление VPN-клиентом Happ")
    p.add_argument("command", choices=["status", "info", "servers", "remember", "switch", "next", "on", "off", "backup"])
    p.add_argument("name", nargs="?", help="страна для switch")
    a = p.parse_args(argv)

    try:
        happ = Happ()
        if a.command == "status":
            s = happ.status()
            print(f"🛡️ VPN: {'подключён' if s['connected'] else 'выключен'} | TUN: {'да' if s['tun'] else 'нет'}")
            print(f"📍 Сервер в Happ: {s['server']}")
            print(f"🌍 Выход: {s['ip']} — {s['country']}, {s['city']}")
        elif a.command == "info":
            for sub in happ.subscriptions():
                try:
                    i = sub.info()
                    left = "безлимит" if i["left_gb"] is None else f"осталось {i['left_gb']} ГБ"
                    exp = f"до {i['expire']:%d.%m.%Y} ({i['days_left']} дн.)" if i["expire"] else "бессрочно"
                    print(f"📋 {i['title'] or sub.host}: скачано {i['download_gb']} ГБ, {left}, {exp}")
                except HappError as e:
                    print(f"⚠️ {sub.title or sub.host}: {e}")
        elif a.command == "servers":
            names = happ.servers()
            print("📋 Выучено: " + (", ".join(names) if names else "пока ничего — happ-vpn remember"))
        elif a.command == "remember":
            print(f"🧠 Запомнил: {happ.remember()}")
        elif a.command == "switch":
            if not a.name:
                p.error("укажи страну: happ-vpn switch Швеция")
            print(f"🔄 Переключено на: {happ.switch(a.name)}")
        elif a.command == "next":
            print(f"⏭️ Переключено на: {happ.next()}")
        elif a.command == "on":
            happ.connect(); print("✅ Команда подключения отправлена")
        elif a.command == "off":
            happ.disconnect(); print("❌ Команда отключения отправлена")
        elif a.command == "backup":
            print(f"💾 Бэкап: {happ.backup()}")
    except HappError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
