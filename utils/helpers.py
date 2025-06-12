from datetime import datetime, timedelta
from typing import List, Tuple
from loguru import logger


def setup_logging() -> None:
    """Настройка логирования"""
    logger.add(
        "logs/bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        encoding="utf-8"
    )


def format_date(date: datetime) -> str:
    """Форматирование даты для вывода"""
    return date.strftime("%d.%m.%Y")


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """Получение диапазона дат для статистики"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == "day":
        return today, today + timedelta(days=1)
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=7)
    elif period == "month":
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)
        return start, end
    elif period == "year":
        start = today.replace(month=1, day=1)
        end = today.replace(year=today.year + 1, month=1, day=1)
        return start, end
    else:
        raise ValueError(f"Неизвестный период: {period}")


def calculate_streak(dates: List[datetime]) -> int:
    """Подсчет текущей серии выполнений привычки"""
    if not dates:
        return 0
        
    dates = sorted(dates, reverse=True)
    today = datetime.now().date()
    streak = 0
    last_date = None
    
    for date in dates:
        date = date.date()
        if last_date is None:
            if (today - date).days <= 1:
                streak = 1
                last_date = date
            else:
                break
        elif (last_date - date).days == 1:
            streak += 1
            last_date = date
        else:
            break
            
    return streak 