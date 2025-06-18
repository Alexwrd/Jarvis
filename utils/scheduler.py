from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def send_reminder(chat_id: int):
    await bot.send_message(chat_id, "⏰ Напоминание: занятие через 1 час!")

scheduler = AsyncIOScheduler()