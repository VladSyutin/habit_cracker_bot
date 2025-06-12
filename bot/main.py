import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from loguru import logger

from config.settings import settings
from database.models import db
from utils.helpers import setup_logging
from bot.handlers import base, habits, stats


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    # Инициализация базы данных
    await db.init()
    
    # Создаем директорию для базы данных
    Path("data").mkdir(exist_ok=True)
    
    # Создаем директорию для логов
    Path("logs").mkdir(exist_ok=True)
    
    # Настройка вебхука в продакшн режиме
    if settings.is_production and settings.webhook_url:
        await bot.set_webhook(
            url=settings.webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to {settings.webhook_url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted, using polling")


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота"""
    logger.info("Shutting down...")
    
    if settings.is_production:
        await bot.delete_webhook()
    
    await bot.session.close()
    logger.info("Bye!")


def main():
    """Основная функция запуска бота"""
    # Настройка логирования
    setup_logging()
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting bot...")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(base.router)
    dp.include_router(habits.router)
    dp.include_router(stats.router)
    
    # Регистрация хэндлеров запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск бота
    if settings.is_production and settings.webhook_url:
        # Запуск через вебхук
        app = web.Application()
        
        # Создаем хэндлер для вебхука
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        
        # Настраиваем пути
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        
        # Настраиваем веб-приложение
        setup_application(app, dp, bot=bot)
        
        # Запускаем веб-сервер
        web.run_app(
            app,
            host=settings.HOST,
            port=settings.PORT
        )
    else:
        # Запуск через polling
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main() 