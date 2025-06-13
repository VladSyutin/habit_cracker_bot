from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_keyboard, get_habits_keyboard, get_period_keyboard
from database.models import db
from utils.helpers import format_date, get_date_range, calculate_streak
from bot.handlers.habits import HabitStates

router = Router()


@router.message(F.text == "📊 Статистика")
async def show_statistics_menu(message: Message, state: FSMContext):
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


@router.message(HabitStates.waiting_for_period_selection)
async def show_statistics(message: Message, state: FSMContext):
    """Показ статистики за выбранный период"""
    if message.text == "🔙 Вернуться в главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_keyboard())
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


@router.callback_query(F.data.startswith("stats_"))
async def show_stats_period(callback: CallbackQuery):
    """Выбор периода для статистики"""
    if "_" not in callback.data:
        return
        
    parts = callback.data.split("_")
    if len(parts) != 2:
        return
        
    action, value = parts
    
    if action == "stats":
        # Показываем выбор периода
        habit_id = int(value)
        await callback.message.edit_text(
            "📅 Выберите период:",
            reply_markup=get_period_keyboard()
        )
        # Сохраняем ID привычки в callback_data следующей клавиатуры
        for row in get_period_keyboard().inline_keyboard:
            for button in row:
                button.callback_data = f"{button.callback_data}_{habit_id}"
    else:
        # Показываем статистику за период
        period = value
        habit_id = int(parts[2])
        
        start_date, end_date = get_date_range(period)
        completions = await db.get_completions(habit_id, start_date, end_date)
        
        # Подсчитываем статистику
        total_days = len(completions)
        streak = calculate_streak(completions)
        
        # Формируем текст статистики
        stats_text = (
            f"📊 Статистика за {period}:\n\n"
            f"✅ Всего выполнено: {total_days} раз\n"
            f"🔥 Текущая серия: {streak} дней\n"
            f"📅 Период: {format_date(start_date)} - {format_date(end_date)}"
        )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=None
        ) 