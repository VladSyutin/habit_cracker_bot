from pydantic_settings import BaseSettings
from pydantic import SecretStr, HttpUrl
from typing import Optional


class Settings(BaseSettings):
    # Основные настройки бота
    BOT_TOKEN: SecretStr
    ENVIRONMENT: str = "development"
    
    # Настройки веб-сервера и вебхука
    WEBHOOK_HOST: Optional[HttpUrl] = None
    WEBHOOK_PATH: str = "/webhook"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # База данных
    DATABASE_PATH: str = "data/habits.db"
    
    @property
    def webhook_url(self) -> Optional[str]:
        """Полный URL для вебхука"""
        if self.WEBHOOK_HOST:
            return f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"
        return None
    
    @property
    def is_production(self) -> bool:
        """Проверка продакшн-режима"""
        return self.ENVIRONMENT.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем глобальный экземпляр настроек
settings = Settings() 