FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание volume для базы данных
VOLUME ["/app/data"]

# Запуск бота
CMD ["python", "-m", "bot.main"] 