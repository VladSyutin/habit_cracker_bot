from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
import logging
from datetime import datetime

from states import CreateHabitStates, DeleteHabitStates, CompleteHabitStates, StatsHabitStates
from keyboards import get_main_keyboard, get_cancel_keyboard, get_confirm_keyboard, get_habits_keyboard, get_delete_habits_keyboard, get_confirm_inline_keyboard, get_delete_habits_reply_keyboard, get_complete_habits_reply_keyboard, get_stats_habits_reply_keyboard
from database import Database

router = Router()
db = Database()
logger = logging.getLogger(__name__)

def format_date(date_value):
    """Форматирует дату из различных форматов в '28 июня в 17:55'"""
    if not date_value:
        return "Не выполнялась"
    
    try:
        # Если это уже объект datetime
        if isinstance(date_value, datetime):
            dt = date_value
        else:
            # Пробуем разные форматы дат для строк
            date_formats = [
                '%Y-%m-%d %H:%M:%S',  # 2025-06-28 17:55:32
                '%Y-%m-%d',           # 2025-06-28
                '%Y-%m-%d %H:%M',     # 2025-06-28 17:55
                '%d.%m.%Y %H:%M:%S',  # 28.06.2025 17:55:32
                '%d.%m.%Y %H:%M',     # 28.06.2025 17:55
                '%d.%m.%Y',           # 28.06.2025
            ]
            
            dt = None
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(str(date_value), fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                # Если не удалось распарсить, возвращаем исходную строку
                return str(date_value)
        
        # Словарь для названий месяцев
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        
        # Форматируем дату
        day = dt.day
        month = months[dt.month]
        
        # Если время есть, добавляем его
        if dt.hour != 0 or dt.minute != 0:
            hour = dt.hour
            minute = dt.minute
            return f"{day} {month} в {hour:02d}:{minute:02d}"
        else:
            # Если времени нет, показываем только дату
            return f"{day} {month}"
            
    except (ValueError, TypeError, AttributeError):
        # Если не удалось распарсить дату, возвращаем исходную строку
        return str(date_value)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для трекинга привычек.\n\n"
        "Я помогу тебе:\n"
        "• Создавать новые привычки\n"
        "• Отслеживать их выполнение\n"
        "• Просматривать статистику\n"
        "• Удалять ненужные привычки\n\n"
        "Выбери действие в меню ниже:",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Справка по использованию бота:\n\n"
        "Создать привычку - создание новой привычки\n"
        "Удалить привычку - удаление существующей привычки\n"
        "Выполнить привычку - отметка о выполнении привычки\n"
        "Статистика - просмотр статистики по привычкам\n\n"
        "Для отмены любого действия используй кнопку Отмена",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "Создать привычку")
async def create_habit_start(message: Message, state: FSMContext):
    """Начало процесса создания привычки"""
    logger.info("Начало создания привычки")
    await state.set_state(CreateHabitStates.waiting_for_name)
    logger.info(f"Состояние установлено: {CreateHabitStates.waiting_for_name.state}")
    await message.answer(
        "Введите название новой привычки:\n\n"
        "Например: Читать 30 минут в день, Делать зарядку, Пить воду",
        reply_markup=get_cancel_keyboard()
    )

@router.message(CreateHabitStates.waiting_for_name)
async def process_habit_name(message: Message, state: FSMContext):
    """Обработка введенного названия привычки"""
    logger.info(f"Обработка названия привычки: {message.text}")
    
    # Проверяем, не является ли сообщение кнопкой "Отмена"
    if message.text == "Отмена":
        logger.info("Нажата кнопка отмены в состоянии ввода названия привычки")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Сохраняем название привычки в состоянии
    await state.update_data(habit_name=message.text)
    await state.set_state(CreateHabitStates.waiting_for_confirmation)
    logger.info(f"Состояние изменено на waiting_for_confirmation, название: {message.text}")
    
    clean_name = message.text.replace("'", "").replace('"', "")
    await message.answer(
        f"Подтвердите создание привычки:\n\n"
        f"Название: <b>{clean_name}</b>\n\n"
        f"Создать эту привычку?",
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.message(CreateHabitStates.waiting_for_confirmation)
async def process_habit_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения создания привычки"""
    logger.info(f"Обработка подтверждения: {message.text}")
    
    # Более гибкая проверка подтверждения
    if message.text in ["Да", "Да", "да", "ДА", "yes", "Yes", "YES", "1", "true"]:
        # Получаем данные из состояния
        data = await state.get_data()
        habit_name = data.get('habit_name')
        logger.info(f"Подтверждение создания привычки: {habit_name}")
        
        if not habit_name:
            await message.answer(
                "Ошибка: название привычки не найдено. Попробуйте создать привычку заново.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Создаем привычку в базе данных
        success = await db.create_habit(message.from_user.id, habit_name)
        
        if success:
            clean_name = habit_name.replace("'", "").replace('"', "")
            await message.answer(
                f"Привычка <b>{clean_name}</b> успешно создана!\n\n"
                f"Теперь вы можете отмечать её выполнение в меню Выполнить привычку",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "Произошла ошибка при создании привычки. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
        
        await state.clear()
    
    elif message.text in ["Нет", "Нет", "нет", "НЕТ", "no", "No", "NO", "0", "false"]:
        await state.clear()
        await message.answer(
            "Создание привычки отменено.",
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Если введен непонятный текст, просим повторить
        await message.answer(
            "Пожалуйста, выберите Да для создания привычки или Нет для отмены.",
            reply_markup=get_confirm_keyboard()
        )

@router.message(F.text == "Удалить привычку")
async def delete_habit_start(message: Message, state: FSMContext):
    """Начало процесса удаления привычки"""
    logger.info("Начало удаления привычки")
    habits = await db.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "У вас пока нет созданных привычек.\n"
            "Создайте первую привычку, нажав Создать привычку",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(DeleteHabitStates.waiting_for_habit_choice)
    logger.info(f"Состояние установлено: {DeleteHabitStates.waiting_for_habit_choice.state}")
    await message.answer(
        "Выберите привычку для удаления:",
        reply_markup=get_delete_habits_reply_keyboard(habits)
    )

@router.message(DeleteHabitStates.waiting_for_habit_choice)
async def process_delete_habit_choice(message: Message, state: FSMContext):
    """Обработка выбора привычки для удаления через обычные кнопки"""
    logger.info(f"Обработка выбора привычки для удаления: {message.text}")
    
    # Проверяем, не является ли сообщение кнопкой "Отмена"
    if message.text == "Отмена":
        logger.info("Нажата кнопка отмены в состоянии выбора привычки для удаления")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Получаем название привычки напрямую
    habit_name = message.text
    logger.info(f"Название привычки: {habit_name}")
    
    # Получаем все привычки пользователя
    habits = await db.get_user_habits(message.from_user.id)
    
    # Ищем привычку по названию
    selected_habit = None
    for habit in habits:
        if habit['name'] == habit_name:
            selected_habit = habit
            break
    
    if not selected_habit:
        logger.info("Привычка не найдена")
        await message.answer(
            "Привычка не найдена. Попробуйте выбрать из списка.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    logger.info(f"Привычка найдена: {selected_habit['name']} (ID: {selected_habit['id']})")
    
    # Получаем статистику привычки
    habit_stats = await db.get_habit_stats(selected_habit['id'], message.from_user.id)
    
    # Сохраняем ID привычки в состоянии
    await state.update_data(habit_id=selected_habit['id'], habit_name=selected_habit['name'])
    await state.set_state(DeleteHabitStates.waiting_for_confirmation)
    logger.info(f"Состояние изменено на waiting_for_confirmation")
    
    clean_name = selected_habit['name'].replace("'", "").replace('"', "")
    await message.answer(
        f"Подтвердите удаление привычки:\n\n"
        f"Название: <b>{clean_name}</b>\n"
        f"Выполнено раз: {habit_stats['completed_count']}\n"
        f"Создана: {format_date(habit_stats['created_at'])}\n\n"
        f"<b>ВНИМАНИЕ!</b> Это действие нельзя отменить!\n"
        f"Удалить эту привычку?",
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.message(DeleteHabitStates.waiting_for_confirmation)
async def process_delete_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения удаления привычки"""
    # Более гибкая проверка подтверждения
    if message.text in ["Да", "Да", "да", "ДА", "yes", "Yes", "YES", "1", "true"]:
        # Получаем данные из состояния
        data = await state.get_data()
        habit_id = data.get('habit_id')
        habit_name = data.get('habit_name')
        
        if not habit_id or not habit_name:
            await message.answer(
                "Ошибка: данные о привычке не найдены. Попробуйте удалить привычку заново.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Удаляем привычку из базы данных
        success = await db.delete_habit(habit_id, message.from_user.id)
        
        if success:
            clean_name = habit_name.replace("'", "").replace('"', "")
            await message.answer(
                f"Привычка <b>{clean_name}</b> успешно удалена!",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "Произошла ошибка при удалении привычки. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
        
        await state.clear()
    
    elif message.text in ["Нет", "Нет", "нет", "НЕТ", "no", "No", "NO", "0", "false"]:
        await state.clear()
        await message.answer(
            "Удаление привычки отменено.",
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Если введен непонятный текст, просим повторить
        await message.answer(
            "Пожалуйста, выберите Да для удаления привычки или Нет для отмены.",
            reply_markup=get_confirm_keyboard()
        )

@router.message(F.text == "Выполнить привычку")
async def complete_habit_start(message: Message, state: FSMContext):
    """Начало процесса выполнения привычки"""
    logger.info("Начало выполнения привычки")
    habits = await db.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "У вас пока нет созданных привычек.\n"
            "Создайте первую привычку, нажав Создать привычку",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(CompleteHabitStates.waiting_for_habit_choice)
    logger.info(f"Состояние установлено: {CompleteHabitStates.waiting_for_habit_choice.state}")
    await message.answer(
        "Выберите привычку для отметки выполнения:",
        reply_markup=get_complete_habits_reply_keyboard(habits)
    )

@router.message(F.text == "Статистика")
async def show_stats_start(message: Message, state: FSMContext):
    """Начало просмотра статистики"""
    logger.info("Начало просмотра статистики")
    habits = await db.get_user_habits(message.from_user.id)
    
    if not habits:
        await message.answer(
            "У вас пока нет созданных привычек.\n"
            "Создайте первую привычку, нажав Создать привычку",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.set_state(StatsHabitStates.waiting_for_habit_choice)
    logger.info(f"Состояние установлено: {StatsHabitStates.waiting_for_habit_choice.state}")
    await message.answer(
        "Выберите привычку для просмотра статистики:",
        reply_markup=get_stats_habits_reply_keyboard(habits)
    )

@router.callback_query(F.data.startswith("habit_"))
async def process_habit_selection(callback: CallbackQuery):
    """Обработка выбора привычки в инлайн клавиатуре"""
    habit_id = int(callback.data.split("_")[1])
    habit = await db.get_habit_stats(habit_id, callback.from_user.id)
    
    if not habit:
        await callback.answer("Привычка не найдена")
        await callback.message.delete()
        return
    
    # Здесь можно добавить логику для разных действий
    # Пока просто показываем информацию о привычке
    await callback.message.answer(
        f"Статистика привычки <b>{habit['name']}</b>:\n\n"
        f"Выполнено раз: {habit['completed_count']}\n"
        f"Создана: {format_date(habit['created_at'])}\n"
        f"Последнее выполнение: {format_date(habit['last_completed'])}",
        parse_mode="HTML"
    )
    
    await callback.answer()

@router.message(StatsHabitStates.waiting_for_habit_choice)
async def process_stats_habit_choice(message: Message, state: FSMContext):
    """Обработка выбора привычки для просмотра статистики"""
    logger.info(f"Обработка выбора привычки для статистики: {message.text}")
    
    # Проверяем, не является ли сообщение кнопкой "Отмена"
    if message.text == "Отмена":
        logger.info("Нажата кнопка отмены в состоянии выбора привычки для статистики")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Получаем название привычки напрямую
    habit_name = message.text
    logger.info(f"Название привычки: {habit_name}")
    
    # Получаем все привычки пользователя
    habits = await db.get_user_habits(message.from_user.id)
    
    # Ищем привычку по названию
    selected_habit = None
    for habit in habits:
        if habit['name'] == habit_name:
            selected_habit = habit
            break
    
    if not selected_habit:
        logger.info("Привычка не найдена")
        await message.answer(
            "Привычка не найдена. Попробуйте выбрать из списка.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    logger.info(f"Привычка найдена: {selected_habit['name']} (ID: {selected_habit['id']})")
    
    # Получаем статистику привычки
    habit_stats = await db.get_habit_stats(selected_habit['id'], message.from_user.id)
    
    # Очищаем состояние
    await state.clear()
    
    clean_name = selected_habit['name'].replace("'", "").replace('"', "")
    await message.answer(
        f"Статистика привычки <b>{clean_name}</b>:\n\n"
        f"Выполнено раз: <b>{habit_stats['completed_count']}</b>\n"
        f"Создана: {format_date(habit_stats['created_at'])}\n"
        f"Последнее выполнение: {format_date(habit_stats['last_completed'])}\n\n"
        f"Продолжайте в том же духе!",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "Отмена")
async def handle_cancel_button(message: Message, state: FSMContext):
    """Обработка кнопки отмены"""
    current_state = await state.get_state()
    logger.info(f"Нажата кнопка отмены, состояние: {current_state}")
    
    # Очищаем состояние
    await state.clear()
    
    # Отправляем сообщение об отмене
    await message.answer(
        "Действие отменено.",
        reply_markup=get_main_keyboard()
    )

@router.message(CompleteHabitStates.waiting_for_confirmation)
async def process_complete_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения выполнения привычки"""
    logger.info(f"Обработка подтверждения выполнения: {message.text}")
    logger.info(f"Текущее состояние: {await state.get_state()}")
    
    # Более гибкая проверка подтверждения
    if message.text in ["Да", "Да", "да", "ДА", "yes", "Yes", "YES", "1", "true"]:
        logger.info("Подтверждение получено, обрабатываем выполнение привычки")
        
        # Получаем данные из состояния
        data = await state.get_data()
        habit_id = data.get('habit_id')
        habit_name = data.get('habit_name')
        count = data.get('count')
        
        logger.info(f"Данные из состояния: habit_id={habit_id}, habit_name={habit_name}, count={count}")
        
        if not habit_id or not habit_name or count is None:
            logger.error("Недостаточно данных в состоянии")
            await message.answer(
                "Ошибка: данные о привычке не найдены. Попробуйте выполнить привычку заново.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Выполняем привычку в базе данных
        logger.info(f"Выполняем привычку в БД: habit_id={habit_id}, user_id={message.from_user.id}, count={count}")
        success = await db.complete_habit_multiple(habit_id, message.from_user.id, count)
        
        if success:
            logger.info("Привычка успешно выполнена в БД")
            # Получаем обновленную статистику
            updated_stats = await db.get_habit_stats(habit_id, message.from_user.id)
            logger.info(f"Обновленная статистика: {updated_stats}")
            
            clean_name = habit_name.replace("'", "").replace('"', "")
            await message.answer(
                f"Привычка <b>{clean_name}</b> отмечена как выполненная {count} раз!\n\n"
                f"Общая статистика:\n"
                f"Всего выполнено: {updated_stats['completed_count']} раз\n"
                f"Последнее выполнение: {format_date(updated_stats['last_completed'])}",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
            logger.info("Сообщение об успешном выполнении отправлено")
        else:
            logger.error("Ошибка при выполнении привычки в БД")
            await message.answer(
                "Произошла ошибка при выполнении привычки. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
        
        await state.clear()
        logger.info("Состояние очищено")
    
    elif message.text in ["Нет", "Нет", "нет", "НЕТ", "no", "No", "NO", "0", "false"]:
        logger.info("Выполнение привычки отменено пользователем")
        await state.clear()
        await message.answer(
            "Выполнение привычки отменено.",
            reply_markup=get_main_keyboard()
        )
    
    else:
        logger.info(f"Неизвестный ответ: {message.text}")
        # Если введен непонятный текст, просим повторить
        await message.answer(
            "Пожалуйста, выберите Да для подтверждения выполнения или Нет для отмены.",
            reply_markup=get_confirm_keyboard()
        )

@router.message(CompleteHabitStates.waiting_for_habit_choice)
async def process_complete_habit_choice(message: Message, state: FSMContext):
    """Обработка выбора привычки для выполнения"""
    current_state = await state.get_state()
    logger.info(f"Обработка выбора привычки для выполнения: {message.text}, текущее состояние: {current_state}")
    
    # Проверяем, не является ли сообщение кнопкой "Отмена"
    if message.text == "Отмена":
        logger.info("Нажата кнопка отмены в состоянии выбора привычки для выполнения")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Получаем название привычки напрямую
    habit_name = message.text
    logger.info(f"Название привычки: {habit_name}")
    
    # Получаем все привычки пользователя
    habits = await db.get_user_habits(message.from_user.id)
    
    # Ищем привычку по названию
    selected_habit = None
    for habit in habits:
        if habit['name'] == habit_name:
            selected_habit = habit
            break
    
    if not selected_habit:
        logger.info("Привычка не найдена")
        await message.answer(
            "Привычка не найдена. Попробуйте выбрать из списка.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    logger.info(f"Привычка найдена: {selected_habit['name']} (ID: {selected_habit['id']})")
    
    # Сохраняем данные о привычке в состоянии
    await state.update_data(habit_id=selected_habit['id'], habit_name=selected_habit['name'])
    await state.set_state(CompleteHabitStates.waiting_for_count)
    logger.info(f"Состояние изменено на waiting_for_count")
    
    await message.answer(
        f"Выбрана привычка: <b>{selected_habit['name']}</b>\n\n"
        f"Сколько раз вы выполнили эту привычку?\n"
        f"Введите число (например: 1, 2, 5):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(CompleteHabitStates.waiting_for_count)
async def process_complete_count(message: Message, state: FSMContext):
    """Обработка ввода количества выполнений"""
    logger.info(f"Обработка количества выполнений: {message.text}")
    logger.info(f"Текущее состояние: {await state.get_state()}")
    
    # Проверяем, не является ли сообщение кнопкой "Отмена"
    if message.text == "Отмена":
        logger.info("Нажата кнопка отмены в состоянии ввода количества выполнений")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_keyboard()
        )
        return
    
    try:
        count = int(message.text)
        if count <= 0:
            await message.answer(
                "Количество выполнений должно быть положительным числом.\n"
                "Попробуйте еще раз:",
                reply_markup=get_cancel_keyboard()
            )
            return
        if count > 100:
            await message.answer(
                "Количество выполнений не может быть больше 100.\n"
                "Попробуйте еще раз:",
                reply_markup=get_cancel_keyboard()
            )
            return
    except ValueError:
        await message.answer(
            "Пожалуйста, введите целое число (например: 1, 2, 5).\n"
            "Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Получаем данные о привычке из состояния
    data = await state.get_data()
    habit_name = data.get('habit_name')
    habit_id = data.get('habit_id')
    
    logger.info(f"Данные из состояния: habit_id={habit_id}, habit_name={habit_name}")
    
    # Сохраняем количество в состоянии
    await state.update_data(count=count)
    await state.set_state(CompleteHabitStates.waiting_for_confirmation)
    logger.info(f"Состояние изменено на waiting_for_confirmation, количество: {count}")
    
    # Проверяем, что данные сохранились
    updated_data = await state.get_data()
    logger.info(f"Обновленные данные в состоянии: {updated_data}")
    
    clean_name = habit_name.replace("'", "").replace('"', "")
    await message.answer(
        f"Подтвердите выполнение привычки:\n\n"
        f"Привычка: <b>{clean_name}</b>\n"
        f"Количество выполнений: <b>{count}</b>\n\n"
        f"Подтвердить выполнение?",
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )
    logger.info("Сообщение с подтверждением отправлено")

@router.message(any_state)
async def handle_unknown_message(message: Message, state: FSMContext):
    """Обработка неизвестных сообщений"""
    current_state = await state.get_state()
    logger.info(f"Неизвестное сообщение: {message.text}, состояние: {current_state}")
    
    # Проверяем, есть ли другие обработчики, которые должны обработать это сообщение
    logger.info(f"Проверяем состояния: CreateHabitStates.waiting_for_name.state = {CreateHabitStates.waiting_for_name.state}")
    logger.info(f"Проверяем состояния: CreateHabitStates.waiting_for_confirmation.state = {CreateHabitStates.waiting_for_confirmation.state}")
    logger.info(f"Проверяем состояния: DeleteHabitStates.waiting_for_habit_choice.state = {DeleteHabitStates.waiting_for_habit_choice.state}")
    logger.info(f"Проверяем состояния: DeleteHabitStates.waiting_for_confirmation.state = {DeleteHabitStates.waiting_for_confirmation.state}")
    logger.info(f"Проверяем состояния: CompleteHabitStates.waiting_for_habit_choice.state = {CompleteHabitStates.waiting_for_habit_choice.state}")
    logger.info(f"Проверяем состояния: CompleteHabitStates.waiting_for_count.state = {CompleteHabitStates.waiting_for_count.state}")
    logger.info(f"Проверяем состояния: CompleteHabitStates.waiting_for_confirmation.state = {CompleteHabitStates.waiting_for_confirmation.state}")
    
    # Если мы находимся в состоянии создания привычки, не показываем это сообщение
    if current_state in [CreateHabitStates.waiting_for_name.state, CreateHabitStates.waiting_for_confirmation.state]:
        logger.info("Сообщение в состоянии создания привычки - игнорируем")
        return
    
    # Если мы находимся в состоянии удаления привычки, не показываем это сообщение
    if current_state in [DeleteHabitStates.waiting_for_habit_choice.state, DeleteHabitStates.waiting_for_confirmation.state]:
        logger.info("Сообщение в состоянии удаления привычки - игнорируем")
        return
    
    # Если мы находимся в состоянии выполнения привычки, не показываем это сообщение
    if current_state in [CompleteHabitStates.waiting_for_habit_choice.state, CompleteHabitStates.waiting_for_count.state, CompleteHabitStates.waiting_for_confirmation.state]:
        logger.info("Сообщение в состоянии выполнения привычки - игнорируем")
        return
    
    # Если состояние None, значит пользователь не в процессе создания/удаления/выполнения
    if current_state is None:
        await message.answer(
            "Пожалуйста, используйте кнопки меню для выбора действия.",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Пожалуйста, используйте кнопки меню или нажмите Отмена для отмены текущего действия.",
            reply_markup=get_main_keyboard()
        ) 