import aiosqlite
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_count INTEGER DEFAULT 0,
                    last_completed TIMESTAMP
                )
            ''')
            await db.commit()
    
    async def create_habit(self, user_id: int, name: str) -> bool:
        """Создание новой привычки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT INTO habits (user_id, name) VALUES (?, ?)',
                    (user_id, name)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при создании привычки: {e}")
            return False
    
    async def get_user_habits(self, user_id: int):
        """Получение всех привычек пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM habits WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            return await cursor.fetchall()
    
    async def delete_habit(self, habit_id: int, user_id: int) -> bool:
        """Удаление привычки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'DELETE FROM habits WHERE id = ? AND user_id = ?',
                    (habit_id, user_id)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при удалении привычки: {e}")
            return False
    
    async def complete_habit(self, habit_id: int, user_id: int) -> bool:
        """Отметить привычку как выполненную"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE habits 
                    SET completed_count = completed_count + 1, 
                        last_completed = CURRENT_TIMESTAMP 
                    WHERE id = ? AND user_id = ?
                ''', (habit_id, user_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при выполнении привычки: {e}")
            return False
    
    async def complete_habit_multiple(self, habit_id: int, user_id: int, count: int) -> bool:
        """Отметить привычку как выполненную указанное количество раз"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE habits 
                    SET completed_count = completed_count + ?, 
                        last_completed = CURRENT_TIMESTAMP 
                    WHERE id = ? AND user_id = ?
                ''', (count, habit_id, user_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Ошибка при выполнении привычки: {e}")
            return False
    
    async def get_habit_stats(self, habit_id: int, user_id: int):
        """Получение статистики привычки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                'SELECT * FROM habits WHERE id = ? AND user_id = ?',
                (habit_id, user_id)
            )
            return await cursor.fetchone() 