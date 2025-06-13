import aiosqlite
from datetime import datetime
import json

DATABASE_NAME = 'habits.db'

class Database:
    def __init__(self):
        self.db_name = DATABASE_NAME

    async def init(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_name) as db:
            # Создаем таблицу привычек
            await db.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицу для записи выполнений
            await db.execute('''
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    count INTEGER NOT NULL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
                )
            ''')
            await db.commit()

    async def add_habit(self, user_id: int, name: str) -> int:
        """Добавление новой привычки"""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute(
                'INSERT INTO habits (user_id, name) VALUES (?, ?)',
                (user_id, name)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_user_habits(self, user_id: int) -> list:
        """Получение списка привычек пользователя"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                'SELECT id, name FROM habits WHERE user_id = ?',
                (user_id,)
            ) as cursor:
                habits = await cursor.fetchall()
                return [{"id": h[0], "name": h[1]} for h in habits]

    async def delete_habit(self, habit_id: int):
        """Удаление привычки"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
            await db.commit()

    async def add_completion(self, habit_id: int, count: int):
        """Добавление записи о выполнении привычки"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(
                'INSERT INTO completions (habit_id, count) VALUES (?, ?)',
                (habit_id, count)
            )
            await db.commit()

    async def get_statistics(self, habit_id: int, period: str) -> int:
        """Получение статистики по привычке за период"""
        periods = {
            'today': "date(completed_at) = date('now')",
            'week': "date(completed_at) >= date('now', '-7 days')",
            'month': "date(completed_at) >= date('now', '-1 month')",
            'year': "date(completed_at) >= date('now', '-1 year')"
        }
        
        where_clause = periods.get(period, "1=1")
        
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(
                f'''
                SELECT COALESCE(SUM(count), 0)
                FROM completions
                WHERE habit_id = ? AND {where_clause}
                ''',
                (habit_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

# Создаем экземпляр базы данных
db = Database() 