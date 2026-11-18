"""🧪 Безопасная проверка happ_vpn на живом Happ: только чтение, VPN не трогает."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happ_vpn import Happ, HappError  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

happ = Happ()
print("📊", happ.status())
for sub in happ.subscriptions():
    try:
        print("📋", sub, sub.info())
    except HappError as e:
        print("⚠️", sub, e)
print("🧠 Выучено:", happ.servers())
