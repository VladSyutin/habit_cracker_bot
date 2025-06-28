from aiogram.fsm.state import State, StatesGroup

class CreateHabitStates(StatesGroup):
    """Состояния для создания привычки"""
    waiting_for_name = State()  # Ожидание ввода названия привычки
    waiting_for_confirmation = State()  # Ожидание подтверждения создания

class DeleteHabitStates(StatesGroup):
    """Состояния для удаления привычки"""
    waiting_for_habit_selection = State()  # Ожидание выбора привычки для удаления
    waiting_for_confirmation = State()  # Ожидание подтверждения удаления
    waiting_for_habit_choice = State()  # Ожидание выбора привычки через обычные кнопки

class CompleteHabitStates(StatesGroup):
    """Состояния для выполнения привычки"""
    waiting_for_habit_choice = State()  # Ожидание выбора привычки для выполнения
    waiting_for_count = State()  # Ожидание ввода количества выполнений
    waiting_for_confirmation = State()  # Ожидание подтверждения выполнения

class StatsHabitStates(StatesGroup):
    """Состояния для просмотра статистики привычек"""
    waiting_for_habit_choice = State()  # Ожидание выбора привычки для просмотра статистики 