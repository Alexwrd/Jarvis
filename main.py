# main.py
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, admin, homework, theory, reminders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(homework.router)
    dp.include_router(theory.router)

    logging.info("✅ Бот запускается...")
    reminders.setup_scheduler(bot)  # <- теперь в теле main

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("❌ Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())