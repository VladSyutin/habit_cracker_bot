#!/bin/bash

cd /root/habit_cracker_bot

while true; do
    echo "$(date): Запуск бота..."
    python3 main.py
    
    if [ $? -eq 0 ]; then
        echo "$(date): Бот завершился нормально"
        break
    else
        echo "$(date): Бот завершился с ошибкой, перезапуск через 10 секунд..."
        sleep 10
    fi
done 