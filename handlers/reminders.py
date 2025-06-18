import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from pytz import timezone
from config import GROUP_CHAT_IDS

scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))


# Чаты
GROUP_CHAT_ID_EGE = GROUP_CHAT_IDS["ege"]  # ЕГЭ-группа
#GROUP_CHAT_ID_OGE = -1000000000000  # ← заменить на ID группы ОГЭ

# Напоминалка
async def send_reminder(bot: Bot, chat_id: int, text: str):
    try:
        now = datetime.now(timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"📤 [{chat_id}] Напоминание отправляется в {now}")
        await bot.send_message(chat_id, text)
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке в чат {chat_id}: {e}")

def setup_scheduler(bot: Bot):
    loop = asyncio.get_event_loop()

    # ЕГЭ группы
    def ege_group_1():
        asyncio.run_coroutine_threadsafe(
            send_reminder(bot, GROUP_CHAT_ID_EGE, "Сегодня в 16:30 занятие! Не забудьте\n@rinxxvv\n@Pdurove_s"),
            loop
        )
    def ege_group_1_over():
        asyncio.run_coroutine_threadsafe(
            send_reminder(bot, GROUP_CHAT_ID_EGE, "🧠 : Занятие уже подошло к концу(((\n домашку подгрузил в бота, до встречи, друзья)"),
            loop
        )

    #def ege_group_2():

    #  asyncio.run_coroutine_threadsafe(
            #   send_reminder(bot, GROUP_CHAT_ID_EGE, "🧠 ЕГЭ-2: Завтра в 15:00 занятие по информатике! Не забудь 📘"),
            #  loop
        #)

    #def ege_group_3():
        # asyncio.run_coroutine_threadsafe(
        #     send_reminder(bot, GROUP_CHAT_ID_EGE, "🧠 ЕГЭ-3: В пятницу в 17:30 занятие. Подготовь ноутбук! 💼"),
        #     loop
    # )

    # ОГЭ группы (расписание пока не определено)
    #def oge_group_1():
        # asyncio.run_coroutine_threadsafe(
        #    send_reminder(bot, GROUP_CHAT_ID_OGE, "🧮 ОГЭ-1: (расписание пока не задано)"),
        #    loop
    # )

        # def oge_group_2():
        #asyncio.run_coroutine_threadsafe(
        #    send_reminder(bot, GROUP_CHAT_ID_OGE, "🧮 ОГЭ-2: (расписание пока не задано)"),
        #    loop
        # )

    #def oge_group_3():
        #asyncio.run_coroutine_threadsafe(
        # send_reminder(bot, GROUP_CHAT_ID_OGE, "🧮 ОГЭ-3: (расписание пока не задано)"),
        #    loop
    # )

    # Егэшка 1гр
    scheduler.add_job(ege_group_1, "cron", day_of_week="tue, thu", hour=15, minute=30)
    scheduler.add_job(ege_group_1_over, "cron", day_of_week="tue, thu", hour=17, minute=50)


    #scheduler.add_job(ege_group_2, "cron", day_of_week="wed", hour=15, minute=0)
    #scheduler.add_job(ege_group_3, "cron", day_of_week="fri", hour=17, minute=30)

    #scheduler.add_job(oge_group_1, "cron", day_of_week="mon", hour=10, minute=0)
    #scheduler.add_job(oge_group_2, "cron", day_of_week="wed", hour=11, minute=0)
    #scheduler.add_job(oge_group_3, "cron", day_of_week="fri", hour=12, minute=0)

    scheduler.start()
    logging.info("✅ Планировщик запущен")