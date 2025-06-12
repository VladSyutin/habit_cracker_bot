# Habit Cracker Bot 🎯

Telegram-бот для отслеживания привычек и достижения целей. Бот помогает пользователям формировать полезные привычки и избавляться от вредных, предоставляя удобный интерфейс для отслеживания прогресса.

## Основные функции 🚀

- Создание и отслеживание привычек
- Ежедневные напоминания
- Статистика прогресса
- Поддержка нескольких пользователей

## Требования 📋

- Python 3.11+
- Docker и Docker Compose (для продакшн-развертывания)

## Локальная установка 🛠

1. Клонируйте репозиторий:
```bash
git clone https://github.com/VladSyutin/habit_cracker_bot.git
cd habit_cracker_bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

5. Отредактируйте .env файл, добавив свой токен бота и другие настройки.

## Запуск бота 🚀

### Локальный запуск (для разработки)

```bash
python -m bot.main
```

### Продакшн-запуск с Docker 🐳

1. Убедитесь, что файл .env настроен правильно
2. Запустите контейнеры:
```bash
docker-compose up -d
```

## Структура проекта 📁

```
habit_cracker_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers/
│   └── keyboards.py
├── config/
│   └── settings.py
├── database/
│   └── models.py
├── utils/
│   └── helpers.py
├── data/
│   └── habits.db
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Переменные окружения ⚙️

Создайте файл `.env` со следующими переменными:

- `BOT_TOKEN` - токен вашего Telegram бота
- `WEBHOOK_HOST` - домен сервера (для продакшн)
- `WEBHOOK_PATH` - путь для вебхука
- `PORT` - порт для веб-сервера
- `ENVIRONMENT` - режим работы (development/production)

## Развертывание на сервере 🌐

1. Подготовьте сервер:
   - Установите Docker и Docker Compose
   - Настройте домен и SSL-сертификат

2. Скопируйте файлы на сервер:
```bash
git clone https://github.com/VladSyutin/habit_cracker_bot.git
cd habit_cracker_bot
```

3. Настройте .env файл с продакшн-параметрами

4. Запустите бота:
```bash
docker-compose up -d
```

## Логирование 📝

Логи доступны через:
```bash
docker-compose logs -f bot
```

## Поддержка 💬

По всем вопросам обращайтесь в Issues или напрямую к разработчику. 