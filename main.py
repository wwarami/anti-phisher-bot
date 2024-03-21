import os
import asyncio
from dotenv import load_dotenv
import logging
import sys
from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.bot import tele_bot
from src.database import init_db, AsyncDatabaseManager
from src.check_url_bot import main_router


async def start_bot():
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(f'Database url', DATABASE_URL)
    DB_ENGINE = await init_db(database_url=DATABASE_URL)
    async_session = async_sessionmaker(DB_ENGINE, expire_on_commit=False)
    database_manager_instance = AsyncDatabaseManager(async_session=async_session)

    dp = Dispatcher()
    bot = tele_bot

    dp.include_router(main_router)
    await dp.start_polling(bot)


async def start_cli():
    raise NotImplementedError()


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    command = sys.argv[1].strip().lower() if len(sys.argv) > 1 else None
    if command == 'bot':
        await start_bot()
    elif command == 'cli':
        await start_cli()
    else:
        print('Enter a valid command ["bot", "cli"].')


if __name__ == "__main__":
    asyncio.run(main())
