from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import (
    get_main_keyboard,
    get_habits_keyboard,
    get_period_keyboard,
    get_confirm_keyboard
)
from database.models import db
from utils.helpers import format_date, get_date_range, calculate_streak

router = Router()


class HabitStates(StatesGroup):
    """Состояния для создания привычки"""
    waiting_for_name = State()
    waiting_for_habit_selection = State()
    waiting_for_period_selection = State()
    waiting_for_confirmation = State()


@router.message(F.text == "🆕 Создать привычку")
async def create_habit_start(message: Message, state: FSMContext):
    """Начало создания привычки"""
    await state.set_state(HabitStates.waiting_for_name)
    await message.answer(
        "📝 Введите название новой привычки:",
        reply_markup=get_main_keyboard()
    )


@router.message(HabitStates.waiting_for_name)
async def create_habit_name(message: Message, state: FSMContext):
    """Создание привычки с указанным именем"""
    if message.text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())
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


@router.message(HabitStates.waiting_for_confirmation)
async def process_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения действий"""
    if message.text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())
        return

    data = await state.get_data()
    action = data.get("action")
    
    if action == "delete":
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


@router.message(F.text == "✅ Отметить выполнение")
async def mark_habit_start(message: Message, state: FSMContext):
    """Выбор привычки для отметки выполнения"""
    habits = await db.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "❌ У вас пока нет привычек. Создайте новую!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(HabitStates.waiting_for_habit_selection)
    await state.update_data(action="complete", habits=habits)
    await message.answer(
        "Выберите привычку:",
        reply_markup=get_habits_keyboard(habits)
    )


@router.message(HabitStates.waiting_for_habit_selection)
async def process_habit_selection(message: Message, state: FSMContext):
    """Обработка выбора привычки"""
    if message.text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())
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

    if action == "complete":
        await db.mark_habit_completion(habit["id"])
        await message.answer(
            f"✅ Привычка «{habit_name}» отмечена как выполненная!",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
    elif action == "stats":
        await state.update_data(habit_id=habit["id"], habit_name=habit["name"])
        await message.answer(
            "Выберите период:",
            reply_markup=get_period_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_period_selection)
    elif action == "delete":
        await state.update_data(habit_id=habit["id"], habit_name=habit["name"])
        await message.answer(
            f"Вы уверены, что хотите удалить привычку «{habit_name}»?",
            reply_markup=get_confirm_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_confirmation)


@router.message(F.text == "❌ Удалить привычку")
async def delete_habit_start(message: Message, state: FSMContext):
    """Выбор привычки для удаления"""
    habits = await db.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "❌ У вас пока нет привычек. Создайте новую!",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(HabitStates.waiting_for_habit_selection)
    await state.update_data(action="delete", habits=habits)
    await message.answer(
        "Выберите привычку для удаления:",
        reply_markup=get_habits_keyboard(habits)
    ) 