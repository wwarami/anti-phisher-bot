import os
import asyncio
from dotenv import load_dotenv
import logging
import sys
from aiogram import Dispatcher
from src.bot import tele_bot


async def start_bot():
    DATABASE_URL = os.getenv('DATABASE_URL')
    dp = Dispatcher()
    bot = tele_bot

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
    asyncio.run(main)
