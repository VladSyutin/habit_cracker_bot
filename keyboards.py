from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Главная клавиатура с основными функциями"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать привычку")],
            [KeyboardButton(text="Удалить привычку")],
            [KeyboardButton(text="Выполнить привычку")],
            [KeyboardButton(text="Статистика")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_confirm_keyboard():
    """Клавиатура для подтверждения"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_confirm_inline_keyboard():
    """Инлайн клавиатура для подтверждения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="Нет", callback_data="confirm_no")
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ])
    return keyboard

def get_habits_keyboard(habits):
    """Инлайн клавиатура со списком привычек"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for habit in habits:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{habit['name']}",
                callback_data=f"habit_{habit['id']}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ])
    
    return keyboard

def get_delete_habits_keyboard(habits):
    """Инлайн клавиатура со списком привычек для удаления"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for habit in habits:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{habit['name']}",
                callback_data=f"delete_habit_{habit['id']}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ])
    
    return keyboard

def get_delete_habits_reply_keyboard(habits):
    """Обычная клавиатура со списком привычек для удаления"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Добавляем кнопки для каждой привычки
    for habit in habits:
        keyboard.keyboard.append([KeyboardButton(text=habit['name'].replace("'", "").replace('"', ""))])
    
    # Добавляем кнопку отмены
    keyboard.keyboard.append([KeyboardButton(text="Отмена")])
    
    return keyboard

def get_complete_habits_reply_keyboard(habits):
    """Обычная клавиатура со списком привычек для выполнения"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Добавляем кнопки для каждой привычки
    for habit in habits:
        keyboard.keyboard.append([KeyboardButton(text=habit['name'].replace("'", "").replace('"', ""))])
    
    # Добавляем кнопку отмены
    keyboard.keyboard.append([KeyboardButton(text="Отмена")])
    
    return keyboard

def get_stats_habits_reply_keyboard(habits):
    """Обычная клавиатура со списком привычек для просмотра статистики"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Добавляем кнопки для каждой привычки
    for habit in habits:
        keyboard.keyboard.append([KeyboardButton(text=habit['name'].replace("'", "").replace('"', ""))])
    
    # Добавляем кнопку отмены
    keyboard.keyboard.append([KeyboardButton(text="Отмена")])
    
    return keyboard 