import os
from aiogram import types
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from database.queries import get_user_by_username

router = Router()

class TheoryStates(StatesGroup):
    waiting_for_number = State()

def numbers_keyboard():
    buttons = []
    row = []
    for i in range(1, 28):
        row.append(KeyboardButton(text=str(i)))
        if len(row) == 6:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(text="🔙 Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

def after_file_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Ещё теория")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )
@router.message(Command("теория"))
@router.message(lambda msg: msg.text == "📘 Теория")
async def start_theory(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if not username:
        await message.answer("❗ У вас не установлен username.")
        return

    username = f"@{username}"
    user = get_user_by_username(username)

    if not user:
        await message.answer("❗ Вас нет в базе. Обратитесь к преподавателю.")
        return

    await state.update_data(group=user[3])
    await message.answer("Выбери номер теоретического задания:", reply_markup=numbers_keyboard())
    await state.set_state(TheoryStates.waiting_for_number)

@router.message(TheoryStates.waiting_for_number)
async def send_theory_file(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📚 Домашка"), KeyboardButton(text="📘 Теория")]
            ],
            resize_keyboard=True
        )
        await message.answer("🔙 Возвращаюсь в главное меню.", reply_markup=keyboard)
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, нажми на номер задания.")
        return

    data = await state.get_data()
    group = data.get("group")
    number = message.text
    file_path = f"files/theory/{group}/{number}.pdf"

    if not os.path.exists(file_path):
        await message.answer("Файл не найден. Возможно, он ещё не загружен.", reply_markup=ReplyKeyboardRemove())
    else:
        file = FSInputFile(file_path)
        await message.answer_document(file, caption=f"📘 Теория задания №{number}", reply_markup=ReplyKeyboardRemove())
        await message.answer("Что дальше?", reply_markup=after_file_keyboard())

    await state.clear()

@router.message(lambda m: m.text == "📘 Ещё теория")
async def more_theory(message: types.Message, state: FSMContext):
    username = f"@{message.from_user.username}"
    user = get_user_by_username(username)

    if not user:
        await message.answer("❗ Вас нет в базе.")
        return

    await state.update_data(group=user[3])
    await message.answer("Выбери номер задания:", reply_markup=numbers_keyboard())
    await state.set_state(TheoryStates.waiting_for_number)


@router.message(lambda m: m.text == "🔙 Главное меню")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Домашка"), KeyboardButton(text="📘 Теория")]
        ],
        resize_keyboard=True
    )
    await message.answer("🔙 Главное меню", reply_markup=keyboard)