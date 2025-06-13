import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonDefault

from database.models import db
from bot.keyboards import (
    get_main_keyboard,
    get_habits_keyboard,
    get_period_keyboard,
    get_confirm_keyboard
)

# Замените на свой токен от @BotFather
BOT_TOKEN = "8131632477:AAGg76we2apCbPj880yZ73Bcwr3yPZXmVU0"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для FSM (машины состояний)
class HabitStates(StatesGroup):
    waiting_for_habit_name = State()
    waiting_for_completion_count = State()
    waiting_for_habit_selection = State()
    waiting_for_period_selection = State()
    waiting_for_confirmation = State()

async def remove_bot_commands():
    """Удаление всех команд бота и кнопки меню"""
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
    await bot.set_chat_menu_button(menu_button=None)

@dp.message(F.text.lower() == "/start")
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await remove_bot_commands()  # Удаляем меню при каждом старте
    await message.answer(
        "👋 Привет! Я бот для отслеживания привычек.\n"
        "Используйте кнопки меню для управления привычками:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "🔙 Вернуться в главное меню")
async def return_to_main_menu(message: types.Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())

@dp.message(F.text == "🆕 Создать привычку")
async def create_habit(message: types.Message, state: FSMContext):
    """Обработчик создания новой привычки"""
    await message.answer(
        "Введите название новой привычки:",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(HabitStates.waiting_for_habit_name)
    await state.update_data(action="create")

@dp.message(HabitStates.waiting_for_habit_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    """Обработка введенного названия привычки"""
    if message.text == "🔙 Вернуться в главное меню":
        await return_to_main_menu(message, state)
        return

    habit_name = message.text.strip()
    if len(habit_name) < 1 or len(habit_name) > 50:
        await message.answer(
            "❌ Название должно быть от 1 до 50 символов. Попробуйте еще раз:"
        )
        return

    await state.update_data(habit_name=habit_name)
    await message.answer(
        f"Создать привычку «{habit_name}»?",
        reply_markup=get_confirm_keyboard()
    )
    await state.set_state(HabitStates.waiting_for_confirmation)

@dp.message(HabitStates.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    """Обработка подтверждения действий"""
    if message.text == "🔙 Вернуться в главное меню":
        await return_to_main_menu(message, state)
        return

    data = await state.get_data()
    action = data.get("action")
    
    if action == "delete":
        # Обработка подтверждения удаления
        habit_id = data.get("habit_id")
        habit_name = data.get("habit_name")
        
        if message.text == "✅ Да":
            await db.delete_habit(habit_id)
            await message.answer(
                f"✅ Привычка «{habit_name}» успешно удалена!",
                reply_markup=get_main_keyboard()
            )
        elif message.text == "❌ Нет":
            await message.answer(
                "❌ Удаление отменено",
                reply_markup=get_main_keyboard()
            )
    else:
        # Обработка подтверждения создания привычки
        habit_name = data.get("habit_name")
        
        if message.text == "✅ Да":
            habit_id = await db.add_habit(message.from_user.id, habit_name)
            await message.answer(
                f"✅ Привычка «{habit_name}» успешно создана!",
                reply_markup=get_main_keyboard()
            )
        elif message.text == "❌ Нет":
            await message.answer(
                "❌ Создание привычки отменено",
                reply_markup=get_main_keyboard()
            )
    
    await state.clear()

@dp.message(F.text == "✅ Отметить выполнение")
async def mark_completion(message: types.Message, state: FSMContext):
    """Обработчик отметки выполнения привычки"""
    habits = await db.get_user_habits(message.from_user.id)
    if not habits:
        await message.answer(
            "У вас пока нет привычек. Создайте новую привычку!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(HabitStates.waiting_for_habit_selection)
    await state.update_data(action="complete", habits=habits)
    await message.answer(
        "Выберите привычку:",
        reply_markup=get_habits_keyboard(habits)
    )

@dp.message(F.text == "📊 Статистика")
async def show_statistics_menu(message: types.Message, state: FSMContext):
    """Показ меню статистики"""
    habits = await db.get_user_habits(message.from_user.id)
    if not habits:
        await message.answer(
            "У вас пока нет привычек. Создайте новую привычку!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(HabitStates.waiting_for_habit_selection)
    await state.update_data(action="stats", habits=habits)
    await message.answer(
        "Выберите привычку для просмотра статистики:",
        reply_markup=get_habits_keyboard(habits)
    )

@dp.message(HabitStates.waiting_for_habit_selection)
async def process_habit_selection(message: types.Message, state: FSMContext):
    """Обработка выбора привычки"""
    if message.text == "🔙 Вернуться в главное меню":
        await return_to_main_menu(message, state)
        return

    data = await state.get_data()
    habits = data.get("habits", [])
    action = data.get("action")
    
    habit_name = message.text[2:].strip()  # Убираем эмодзи
    habit = next((h for h in habits if h["name"] == habit_name), None)
    
    if not habit:
        await message.answer(
            "❌ Привычка не найдена",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    if action == "stats":
        await state.update_data(habit_id=habit["id"], habit_name=habit["name"])
        await message.answer(
            "Выберите период:",
            reply_markup=get_period_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_period_selection)

@dp.message(HabitStates.waiting_for_period_selection)
async def show_statistics(message: types.Message, state: FSMContext):
    """Показ статистики за выбранный период"""
    if message.text == "🔙 Вернуться в главное меню":
        await return_to_main_menu(message, state)
        return

    data = await state.get_data()
    habit_id = data.get("habit_id")
    habit_name = data.get("habit_name")

    period_map = {
        "📊 Сегодня": "today",
        "📊 Неделя": "week",
        "📊 Месяц": "month",
        "📊 Год": "year"
    }
    
    period = period_map.get(message.text)
    if not period:
        await message.answer(
            "❌ Неверный период",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return
    
    count = await db.get_statistics(habit_id, period)
    period_names = {
        "today": "сегодня",
        "week": "за неделю",
        "month": "за месяц",
        "year": "за год"
    }
    
    await message.answer(
        f"📊 Статистика по привычке «{habit_name}»\n"
        f"Количество выполнений {period_names[period]}: {count}",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@dp.message(F.text == "❌ Удалить привычку")
async def delete_habit_menu(message: types.Message, state: FSMContext):
    """Показ меню удаления привычки"""
    habits = await db.get_user_habits(message.from_user.id)
    if not habits:
        await message.answer(
            "У вас пока нет привычек. Создайте новую привычку!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(HabitStates.waiting_for_habit_selection)
    await state.update_data(action="delete", habits=habits)
    await message.answer(
        "Выберите привычку для удаления:",
        reply_markup=get_habits_keyboard(habits)
    )

async def main():
    """Запуск бота"""
    await db.init_db()
    await remove_bot_commands()  # Удаляем все команды бота и кнопку меню
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 