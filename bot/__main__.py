import psycopg2
import asyncio
import logging

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config import parse_settings
from bot.handlers import get_routers
from bot import bot, settings
from bot.middlewares import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)

async def main():

    # Создание асинхронного "движка" с указанием URL подключения
    engine = create_async_engine(url=str(settings.db_url), echo=True)
    # Создание пула сессий
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # Создание диспетчера aiogram
    dp = Dispatcher()
    # На тип Update (родительский тип всех видов апдейтов)
    # навешивается мидлварь, из которой будут пробрасываться сессии в хэндлеры
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    # Подключение цепочки роутеров к диспетчеру
    dp.include_routers(*get_routers())

    # Создание объекта бота с токеном, полученным из настроек
    
    print("Starting polling...")

    # Запуск поллинга
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())