import os
from aiogram import types
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from aiogram.filters import Command
from database.queries import get_user_by_username

router = Router()

@router.message(Command("домашка"))
@router.message(lambda msg: msg.text == "📚 Домашка")
async def send_homework(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer("❗ У вас не установлен username.")
        return

    username = f"@{username}"
    user = get_user_by_username(username)

    if not user:
        await message.answer("❗ Вас нет в базе. Обратитесь к преподавателю.")
        return

    group = user[3]
    file_path = f"files/homework/{group}/latest.txt"

    if not os.path.exists(file_path):
        await message.answer("⚠️ Домашка для вашей группы пока не загружена.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        hw_text = f.read()

    await message.answer(f"📚 Домашнее задание: \n\n{hw_text}")