import os
import logging
import os
from aiogram import types, Router, F
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from config import ADMIN_ID
from database.queries import add_user, get_user_by_username
from database.queries import get_users_by_group, delete_user_by_username
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

class UploadStates(StatesGroup):
    choosing_type = State()
    choosing_group = State()
    choosing_number = State()
    waiting_for_file = State()

class AddUserStates(StatesGroup):
    waiting_for_user_data = State()

class HomeworkStates(StatesGroup):
    choosing_group = State()
    entering_text = State()
    waiting_for_file_optional = State()


def admin_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Домашка"), KeyboardButton(text="📘 Теория")],
            [KeyboardButton(text="📤 Дать домашнее задание"), KeyboardButton(text="➕ Добавить ученика"), KeyboardButton(text="📋 Список учеников")]
        ],
        resize_keyboard=True
    )

def group_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ege_1"), KeyboardButton(text="ege_2"), KeyboardButton(text="ege_3")],
            [KeyboardButton(text="oge_1"), KeyboardButton(text="oge_2"), KeyboardButton(text="oge_3")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

@router.message(lambda m: m.text == "📤 Дать домашнее задание")
async def start_homework_upload(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа.")
        return

    await message.answer("Выбери группу для ДЗ:", reply_markup=group_keyboard())
    await state.set_state(HomeworkStates.choosing_group)


# Новый обработчик для выдачи домашки ученику
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
    text_path = f"files/homework/{group}/latest.txt"
    pdf_path = f"files/homework/{group}/attached.pdf"

    if not os.path.exists(text_path):
        await message.answer("⚠️ Домашка для вашей группы пока не загружена.")
        return

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    await message.answer(f"📚 Домашка для группы {group.upper()}:\n\n{text}")

    if os.path.exists(pdf_path):
        file = FSInputFile(pdf_path)
        await message.answer_document(file, caption="📎 Прикреплённый файл к домашке")

@router.message(HomeworkStates.choosing_group)
async def choose_group(message: types.Message, state: FSMContext):
    group = message.text.strip().lower()
    if group not in ["ege_1", "ege_2", "ege_3", "oge_1", "oge_2", "oge_3"]:
        await message.answer("Пожалуйста, выбери группу из предложенных кнопок.")
        return
    await state.update_data(group=group)
    await message.answer(f"✍️ Напиши текст домашнего задания для группы {group.upper()}:")
    await state.set_state(HomeworkStates.entering_text)

@router.message(HomeworkStates.entering_text)
async def receive_homework_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    text = message.text.strip()

    os.makedirs(f"files/homework/{group}", exist_ok=True)
    with open(f"files/homework/{group}/latest.txt", "w", encoding="utf-8") as f:
        f.write(text)

    await message.answer(
        "📎 Если хочешь прикрепить PDF-файл с заданием — отправь его сейчас.\n"
        "Если не нужно — напиши <b>пропустить</b>.",
        parse_mode="HTML"
    )
    await state.set_state(HomeworkStates.waiting_for_file_optional)
@router.message(HomeworkStates.waiting_for_file_optional)
async def receive_optional_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    file_path = f"files/homework/{group}/attached.pdf"

    if message.document:
        if not message.document.file_name.endswith(".pdf"):
            await message.answer("⚠️ Принимаются только PDF-файлы.")
            return

        file = await message.bot.get_file(message.document.file_id)
        os.makedirs(f"files/homework/{group}", exist_ok=True)
        await message.bot.download_file(file.file_path, destination=file_path)
        await message.answer("✅ Файл прикреплён.")
    elif message.text.strip().lower() == "пропустить":
        await message.answer("⏭️ Прикрепление файла пропущено.")
    else:
        await message.answer("⚠️ Отправь PDF или напиши 'пропустить'.")
        return

    await message.answer(f"✅ Домашка для группы {group.upper()} обновлена!", reply_markup=admin_menu_keyboard())
    await state.clear()


@router.message(Command("upload"))
async def start_upload(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📚 Домашка"), types.KeyboardButton(text="📘 Теория")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Что вы хотите загрузить?", reply_markup=keyboard)
    await state.set_state(UploadStates.choosing_type)

@router.message(UploadStates.choosing_type)
async def choose_group(message: types.Message, state: FSMContext):
    if message.text not in ["📚 Домашка", "📘 Теория"]:
        await message.answer("Пожалуйста, выберите из кнопок.")
        return

    await state.update_data(file_type=message.text)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="ege_1")],
            [types.KeyboardButton(text="ege_2")],
            [types.KeyboardButton(text="ege_3")],
            [types.KeyboardButton(text="oge_1")],
            [types.KeyboardButton(text="oge_2")],
            [types.KeyboardButton(text="oge_3")],

        ],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("Выберите группу:", reply_markup=keyboard)
    await state.set_state(UploadStates.choosing_group)

@router.message(UploadStates.choosing_group)
async def maybe_choose_number(message: types.Message, state: FSMContext):
    group = message.text
    await state.update_data(group=group)
    data = await state.get_data()

    if data["file_type"] == "📘 Теория":
        numbers = [[types.KeyboardButton(text=str(i)) for i in range(j, j+6)] for j in range(1, 28, 6)]
        await message.answer("Выберите номер задания:", reply_markup=types.ReplyKeyboardMarkup(keyboard=numbers, resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(UploadStates.choosing_number)
    else:
        await message.answer("Отправьте PDF-файл с домашкой:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(UploadStates.waiting_for_file)

@router.message(UploadStates.choosing_number)
async def choose_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Номер должен быть числом.")
        return
    await state.update_data(number=message.text)
    await message.answer("Отправьте PDF-файл с теорией:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(UploadStates.waiting_for_file)

@router.message(UploadStates.waiting_for_file, F.document)
async def handle_upload(message: types.Message, state: FSMContext):
    document = message.document
    if not document.file_name.endswith(".pdf"):
        await message.answer("Пожалуйста, отправьте PDF-файл.")
        return

    data = await state.get_data()
    file_type = data["file_type"]
    group = data["group"]

    if file_type == "📚 Домашка":
        os.makedirs("files/homework", exist_ok=True)
        save_path = f"files/homework/{group}.pdf"
    else:
        number = data["number"]
        os.makedirs(f"files/theory/{group}", exist_ok=True)
        save_path = f"files/theory/{group}/{number}.pdf"

    file = await message.bot.get_file(document.file_id)
    await message.bot.download_file(file.file_path, destination=save_path)

    await message.answer(f"✅ Файл успешно сохранён: `{save_path}`", parse_mode="Markdown")
    await state.clear()

@router.message(Command("add_user"))
async def add_user_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    args = message.text.split(maxsplit=4)
    if len(args) < 4:
        await message.answer("⚠️ Используйте формат:\n<code>/add_user @username Имя Фамилия группа</code>", parse_mode="HTML")
        return

    _, username, *name_parts, group = args
    full_name = " ".join(name_parts)

    if not username.startswith("@"):
        await message.answer("⚠️ Username должен начинаться с @")
        return

    add_user(username, full_name, group)
    await message.answer(f"✅ Пользователь {full_name} ({username}) добавлен в группу {group.upper()}")

@router.message(lambda message: message.text == "➕ Добавить ученика")
async def start_add_user(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    await message.answer(
        "Введите данные ученика в формате:\n"
        "/add_user @username Имя Фамилия группа\n\n"
        "Пример:\n/add_user @ivanov Иван Иванов ege_1"
    )
    await state.set_state(AddUserStates.waiting_for_user_data)

@router.message(AddUserStates.waiting_for_user_data)
async def process_add_user(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        await state.clear()
        return

    text = message.text
    if not text.startswith("/add_user "):
        await message.answer("Ошибка! Пожалуйста, используйте команду в формате:\n/add_user @username Имя Фамилия группа")
        await state.clear()
        return

    args = text.split(maxsplit=4)
    if len(args) < 4:
        await message.answer("Недостаточно данных. Используйте формат:\n/add_user @username Имя Фамилия группа")
        await state.clear()
        return

    _, username, *name_parts, group = args
    full_name = " ".join(name_parts)

    if not username.startswith("@"):
        await message.answer("Username должен начинаться с @")
        await state.clear()
        return

    try:
        add_user(username, full_name, group)
        await message.answer(f"✅ Пользователь {full_name} ({username}) добавлен в группу {group.upper()}")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении: {e}")
    finally:
        await state.clear()


@router.message(lambda m: m.text == "📋 Список учеников")
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа.")
        return

    groups = ["ege_1", "ege_2", "ege_3", "oge_1", "oge_2", "oge_3"]
    result = ""
    for group in groups:
        users = get_users_by_group(group)
        result += f"<b>{group.upper()}</b> ({len(users)} учеников):\n"
        for u in users:
            result += f" - {u[2]} ({u[1]})\n"
        result += "\n"

    await message.answer(result, parse_mode="HTML")

# Новый хендлер для удаления ученика (по кнопке)
@router.message(lambda m: m.text == "❌ Удалить ученика")
async def prompt_delete_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа.")
        return

    await message.answer(
        "ℹ️ Чтобы удалить ученика, отправьте команду:\n<code>/delete_user @username</code>",
        parse_mode="HTML"
    )

@router.message(Command("delete_user"))
async def delete_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа.")
        return

    await message.answer("ℹ️ Чтобы удалить ученика, используйте команду:\n<code>/delete_user @username</code>", parse_mode="HTML")
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].startswith("@"):
        await message.answer("⚠️ Используйте формат:\n/delete_user @username")
        return

    username = args[1]
    user = get_user_by_username(username)
    if not user:
        await message.answer(f"⚠️ Пользователь {username} не найден в базе.")
        return

    try:
        delete_user_by_username(username)
        await message.answer(f"✅ Пользователь {username} удалён из базы.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении: {e}")