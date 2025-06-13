#!/bin/bash

cd /root/habit_cracker_bot
source venv/bin/activate

# Убиваем предыдущий процесс бота, если он существует
pkill -f "python -m bot.main"

# Запускаем бота в фоновом режиме
nohup python -m bot.main > bot.log 2>&1 &

echo "Bot started in background. Check bot.log for output." 