# core/onlyfans_client.py
from __future__ import annotations
from typing import List, Dict, Any
import pandas as pd

from core.utils import get_settings


class OnlyFansClient:
    """
    Абстракция клиента OnlyFans/API-провайдера.
    Сейчас работает на заглушках, позже сюда подставим реальные запросы.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.onlyfans_api_key
        self.base_url = base_url or settings.onlyfans_api_url
        # сюда позже добавим httpx.Client / requests.Session, прокси и т.д.

    # ====== Фаны ======

    def fetch_fans(self, account: str) -> pd.DataFrame:
        """
        Вернуть DataFrame с фанами для аккаунта.
        Колонки:
        - id, name, segment, revenue, has_new
        """
        # TODO: заменить на реальный запрос к API/БД
        return pd.DataFrame([
            {"id": 1, "name": "Mike 🔥", "segment": "VIP", "revenue": 250, "has_new": True},
            {"id": 2, "name": "Alex 💎", "segment": "Buyer", "revenue": 100, "has_new": False},
            {"id": 3, "name": "John", "segment": "Free", "revenue": 0, "has_new": True},
            {"id": 4, "name": "Sarah", "segment": "Buyer", "revenue": 75, "has_new": False},
            {"id": 5, "name": "Dave", "segment": "VIP", "revenue": 300, "has_new": False},
        ])

    # ====== Чаты ======

    def fetch_chat_history(self, fan_id: int) -> List[Dict[str, Any]]:
        """
        История чата: список словарей с полями role, text, time.
        """
        # TODO: заменить на SELECT из БД или вызов API
        return [
            {"role": "user", "text": "Привет, как ты?", "time": "10:01"},
            {"role": "assistant", "text": "Хей, милашка 😘 Только проснулась, думаю о тебе.", "time": "10:02"},
            {"role": "user", "text": "Хочу кастом видео 😈", "time": "10:05"},
        ]

    # ====== Аналитика ======

    def fetch_analytics(self, account: str) -> pd.DataFrame:
        """
        Данные для графиков: day, revenue, subs, avg_watch.
        """
        # TODO: заменить на реальные метрики из БД/BI
        return pd.DataFrame({
            "day": pd.date_range("2026-01-20", periods=7),
            "revenue": [1200, 1800, 950, 2200, 1500, 1900, 2300],
            "subs": [45, 52, 48, 60, 55, 62, 70],
            "avg_watch": [18, 21, 16, 24, 20, 23, 25],
        })
