from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.keyboards import get_main_keyboard, get_habits_keyboard, get_period_keyboard
from database.models import db
from utils.helpers import format_date, get_date_range, calculate_streak

router = Router()


@router.message(F.text == "📊 Статистика")
async def stats_start(message: Message):
    """Выбор привычки для просмотра статистики"""
    habits = await db.get_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "❌ У вас пока нет привычек. Создайте новую!",
            reply_markup=get_main_keyboard()
        )
        return
        
    await message.answer(
        "📊 Выберите привычку для просмотра статистики:",
        reply_markup=get_habits_keyboard(habits, prefix="stats")
    )


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