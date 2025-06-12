from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import get_main_keyboard, get_habits_keyboard
from database.models import db
from utils.helpers import format_date, get_date_range, calculate_streak

router = Router()


class HabitStates(StatesGroup):
    """Состояния для создания привычки"""
    waiting_for_name = State()


@router.message(F.text == "🆕 Создать привычку")
async def create_habit_start(message: Message, state: FSMContext):
    """Начало создания привычки"""
    await state.set_state(HabitStates.waiting_for_name)
    await message.answer(
        "📝 Введите название новой привычки:",
        reply_markup=None
    )


@router.message(HabitStates.waiting_for_name)
async def create_habit_name(message: Message, state: FSMContext):
    """Создание привычки с указанным именем"""
    habit_name = message.text.strip()
    
    if len(habit_name) > 100:
        await message.answer(
            "❌ Слишком длинное название. Попробуйте короче (до 100 символов)."
        )
        return
        
    await db.add_habit(message.from_user.id, habit_name)
    await state.clear()
    
    await message.answer(
        f"✅ Привычка «{habit_name}» создана!",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "✅ Отметить выполнение")
async def mark_habit_start(message: Message):
    """Выбор привычки для отметки выполнения"""
    habits = await db.get_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "❌ У вас пока нет привычек. Создайте новую!",
            reply_markup=get_main_keyboard()
        )
        return
        
    await message.answer(
        "📝 Выберите привычку:",
        reply_markup=get_habits_keyboard(habits, prefix="complete")
    )


@router.callback_query(F.data.startswith("complete_"))
async def mark_habit_complete(callback: CallbackQuery):
    """Отметка выполнения привычки"""
    habit_id = int(callback.data.split("_")[1])
    await db.add_completion(habit_id)
    
    # Получаем текущую серию
    completions = await db.get_completions(habit_id)
    streak = calculate_streak(completions)
    
    await callback.message.edit_text(
        f"✅ Отлично! Привычка отмечена как выполненная.\n"
        f"🔥 Текущая серия: {streak} дней"
    )


@router.message(F.text == "❌ Удалить привычку")
async def delete_habit_start(message: Message):
    """Выбор привычки для удаления"""
    habits = await db.get_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "❌ У вас пока нет привычек. Создайте новую!",
            reply_markup=get_main_keyboard()
        )
        return
        
    await message.answer(
        "⚠️ Выберите привычку для удаления:",
        reply_markup=get_habits_keyboard(habits, prefix="delete")
    )


@router.callback_query(F.data.startswith("delete_"))
async def delete_habit_confirm(callback: CallbackQuery):
    """Удаление привычки"""
    habit_id = int(callback.data.split("_")[1])
    await db.delete_habit(habit_id)
    
    await callback.message.edit_text(
        "✅ Привычка удалена!"
    ) 