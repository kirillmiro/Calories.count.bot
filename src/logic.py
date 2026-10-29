import sqlite3
from Database.config import DATABASE

class FoodDatabase:

    def __init__(self, db_path):
        self.db_path = db_path

    def create_tables(self):
    # Создание в бд таблицы food.
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute("""
                    CREATE TABLE IF NOT EXISTS food (
                        food_id INTEGER PRIMARY KEY,
                        food_name TEXT,
                        food_calories INTEGER,
                        food_unit TEXT
                    )
                """)

    # Получение информации о продукте по его названию.
    def get_food_info(self, food_name):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT food_calories, food_unit FROM food WHERE food_name = ?",
                (food_name,),
            )
            return cursor.fetchone()

    # Добавление нового продукта в базу данных.
    def add_food(self, food_name, food_calories, food_unit):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO food (food_name, food_calories, food_unit) VALUES (?, ?, ?)",
                (food_name, food_calories, food_unit),
            )

if __name__ == '__main__':
    manager = FoodDatabase(DATABASE)
    manager.create_tables()