from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_keyboard
from database.models import db

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для отслеживания привычек.\n\n"
        "С моей помощью ты можешь:\n"
        "• Создавать новые привычки\n"
        "• Отмечать их выполнение\n"
        "• Смотреть статистику\n"
        "• Удалять ненужные привычки\n\n"
        "Используй кнопки меню для управления 👇",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 Справка по командам:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/cancel - Отменить текущее действие\n\n"
        "Также вы можете использовать кнопки меню для всех действий.",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "🤔 Нечего отменять",
            reply_markup=get_main_keyboard()
        )
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено",
        reply_markup=get_main_keyboard()
    ) 