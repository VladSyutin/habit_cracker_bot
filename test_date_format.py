#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pytz

def format_date(date_value):
    """Форматирует дату из различных форматов в '28 июня в 17:55' с учетом часового пояса"""
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
        
        # Конвертируем UTC время в московское время
        # Предполагаем, что время в базе данных сохранено в UTC
        utc_tz = pytz.UTC
        moscow_tz = pytz.timezone('Europe/Moscow')
        
        # Если datetime не имеет информации о часовом поясе, считаем его UTC
        if dt.tzinfo is None:
            dt = utc_tz.localize(dt)
        
        # Конвертируем в московское время
        moscow_dt = dt.astimezone(moscow_tz)
        
        # Словарь для названий месяцев
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        
        # Форматируем дату
        day = moscow_dt.day
        month = months[moscow_dt.month]
        
        # Если время есть, добавляем его
        if moscow_dt.hour != 0 or moscow_dt.minute != 0:
            hour = moscow_dt.hour
            minute = moscow_dt.minute
            return f"{day} {month} в {hour:02d}:{minute:02d}"
        else:
            # Если времени нет, показываем только дату
            return f"{day} {month}"
            
    except (ValueError, TypeError, AttributeError) as e:
        # Если не удалось распарсить дату, возвращаем исходную строку
        print(f"Ошибка при форматировании даты {date_value}: {e}")
        return str(date_value)

# Тестируем функцию
if __name__ == "__main__":
    test_cases = [
        "2025-06-28 17:55:32",  # Строка с полной датой
        "2025-06-28",           # Строка только с датой
        datetime(2025, 6, 28, 17, 55, 32),  # Объект datetime с временем
        datetime(2025, 6, 28),              # Объект datetime без времени
        datetime(2025, 1, 15, 9, 30, 0),    # Другой объект datetime
        None,                   # Пустое значение
        "",                     # Пустая строка
        "invalid_date",         # Некорректная дата
    ]
    
    print("Тестирование функции format_date с объектами datetime:")
    print("=" * 65)
    
    for test_date in test_cases:
        result = format_date(test_date)
        print(f"Вход: {test_date} (тип: {type(test_date)})")
        print(f"Выход: {result}")
        print("-" * 50) 