# core/data.py
from __future__ import annotations
import pandas as pd
from core.onlyfans_client import OnlyFansClient


_client: OnlyFansClient | None = None


def get_client() -> OnlyFansClient:
    """
    Ленивая инициализация клиента.
    Потом сюда можно передать api_key, настройки прокси и т.п.
    """
    global _client
    if _client is None:
        _client = OnlyFansClient(api_key=None)
    return _client


def get_fans_df(account: str) -> pd.DataFrame:
    """
    Публичный интерфейс для UI. Сейчас тянет данные из OnlyFansClient,
    позже внутри него будут реальные запросы к API/БД.
    """
    client = get_client()
    return client.fetch_fans(account)


def get_chat_history(fan_id: int):
    """
    История чата для UI.
    """
    client = get_client()
    return client.fetch_chat_history(fan_id)


def get_analytics_data(account: str):
    """
    Данные аналитики для UI.
    """
    client = get_client()
    return client.fetch_analytics(account)
