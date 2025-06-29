#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

def test_timezone_fix():
    """Простой тест исправления часового пояса для сервера"""
    
    print("=" * 50)
    print("ТЕСТ ИСПРАВЛЕНИЯ ЧАСОВОГО ПОЯСА")
    print("=" * 50)
    
    try:
        # Проверяем импорт pytz
        import pytz
        print("✅ pytz импортирован успешно")
        
        # Проверяем импорт handlers
        from handlers import format_date
        print("✅ format_date импортирована успешно")
        
        # Тестируем конкретный случай
        test_time = "2025-06-29 09:25:00"
        expected_result = "29 июня в 12:25"
        
        result = format_date(test_time)
        print(f"Тест: {test_time} -> {result}")
        print(f"Ожидалось: {expected_result}")
        
        if result == expected_result:
            print("✅ ИСПРАВЛЕНИЕ РАБОТАЕТ КОРРЕКТНО!")
        else:
            print("❌ ПРОБЛЕМА: результат не совпадает с ожидаемым")
            print(f"Получено: {result}")
            print(f"Ожидалось: {expected_result}")
        
        # Дополнительные тесты
        print("\nДополнительные тесты:")
        test_cases = [
            ("2025-06-29 09:15:00", "29 июня в 12:15"),
            ("2025-06-29 12:00:00", "29 июня в 15:00"),
            ("2025-06-29 00:00:00", "29 июня в 03:00"),
        ]
        
        for test_input, expected in test_cases:
            result = format_date(test_input)
            status = "✅" if result == expected else "❌"
            print(f"{status} {test_input} -> {result} (ожидалось: {expected})")
        
    except ImportError as e:
        print(f"❌ ОШИБКА ИМПОРТА: {e}")
        print("Возможно, библиотека pytz не установлена на сервере")
        print("Установите: pip install pytz")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        print("Полный traceback:")
        traceback.print_exc()
    
    print("=" * 50)

if __name__ == "__main__":
    test_timezone_fix() 