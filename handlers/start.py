from config import ADMIN_ID
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold
from aiogram import Router
from database.queries import get_user_by_username

router = Router()

# Основное меню
def student_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Домашка"), KeyboardButton(text="📘 Теория")],
        ],
        resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Добавить ученика"),
                KeyboardButton(text="📤 Дать домашнее задание")
            ],
            [
                KeyboardButton(text="📚 Домашка"),
                KeyboardButton(text="📘 Теория")
            ],
            [
                KeyboardButton(text="📋 Список учеников"),  # новая кнопка
                KeyboardButton(text="❌ Удалить ученика")   # новая кнопка
            ]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    username = message.from_user.username
    if not username:
        await message.answer("❗ У вас не установлен username в Telegram. Установите его в настройках и попробуйте снова.")
        return

    username = f"@{username}"
    user = get_user_by_username(username)

    if not user:
        await message.answer("❗ Вас нет в базе. Обратитесь к преподавателю.")
        return

    tg_name = message.from_user.full_name

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            f"👋 Привет, {tg_name}! Ты вошёл как администратор.",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            f"👋 Привет, {tg_name}!",
            reply_markup=student_menu()
        )