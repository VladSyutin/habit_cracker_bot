# Исправление проблемы с отображением времени

## Проблема
Бот неправильно отображал время выполнения привычек. Например, показывал "Последнее выполнение: 29 июня в 09:15", хотя фактически было "29 июня в 12:12".

## Причина
SQLite сохраняет время в UTC, но функция `format_date` не учитывала часовой пояс и отображала время как есть, без конвертации в московское время (UTC+3).

## Решение
1. Добавлен импорт библиотеки `pytz` для работы с часовыми поясами
2. Обновлена функция `format_date` в `handlers.py`:
   - Добавлена конвертация UTC времени в московское время
   - Время из базы данных (UTC) теперь корректно отображается в московском часовом поясе

## Изменения в файлах
- `handlers.py`: обновлена функция `format_date` с поддержкой часовых поясов
- `requirements.txt`: добавлена зависимость `pytz==2024.1`
- `test_date_format.py`: обновлена тестовая функция для соответствия новой логике

## Тестирование
Проведены тесты, подтверждающие корректную работу:
- UTC время "2025-06-29 09:15:00" → "29 июня в 12:15" ✅
- UTC время "2025-06-29 09:12:00" → "29 июня в 12:12" ✅

## Статус
✅ Исправлено и протестировано
📝 Изменения отправлены в ветку `dev`
🔄 Готово к созданию pull request в `main` 