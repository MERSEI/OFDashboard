# core/utils.py
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv  # добавь python-dotenv в requirements.txt


# Загружаем .env один раз при импорте
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)


@dataclass
class Settings:
    onlyfans_api_key: str | None
    onlyfans_api_url: str | None
    db_url: str | None


_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Централизованные настройки проекта.
    Читаем переменные окружения и кешируем.
    """
    global _settings
    if _settings is None:
        _settings = Settings(
            onlyfans_api_key=os.getenv("ONLYFANS_API_KEY"),
            onlyfans_api_url=os.getenv("ONLYFANS_API_URL"),
            db_url=os.getenv("DB_URL"),
        )
    return _settings
