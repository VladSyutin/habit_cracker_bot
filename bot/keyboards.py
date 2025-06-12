from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню"""
    kb = [
        [KeyboardButton(text="🆕 Создать привычку")],
        [KeyboardButton(text="✅ Отметить выполнение")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="❌ Удалить привычку")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_habits_keyboard(habits: list) -> ReplyKeyboardMarkup:
    """Клавиатура со списком привычек"""
    kb = []
    for habit in habits:
        kb.append([KeyboardButton(text=f"📝 {habit['name']}")])
    kb.append([KeyboardButton(text="🔙 Вернуться в главное меню")])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_period_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с выбором периода для статистики"""
    kb = [
        [KeyboardButton(text="📊 Сегодня"), KeyboardButton(text="📊 Неделя")],
        [KeyboardButton(text="📊 Месяц"), KeyboardButton(text="📊 Год")],
        [KeyboardButton(text="🔙 Вернуться в главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    kb = [
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
        [KeyboardButton(text="🔙 Вернуться в главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True) 