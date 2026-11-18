"""Happ VPN: статус, трафик подписок и переключение стран в клиенте Happ на Windows."""
from .happ_vpn import Happ, HappError, HappSubscription, main

__all__ = ["Happ", "HappError", "HappSubscription", "main"]
