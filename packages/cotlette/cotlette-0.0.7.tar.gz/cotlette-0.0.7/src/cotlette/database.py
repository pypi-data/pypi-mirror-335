import sqlite3

from cotlette.conf import settings


class Database:
    def __init__(self):
        # Получаем путь к базе данных из настроек
        db_settings = settings.DATABASES['default']
        self.db_url = db_settings['NAME']

    def connect(self):
        """Создает новое соединение с базой данных."""
        return sqlite3.connect(self.db_url)
    
    def execute(self, query, params=None, fetch=False):
        """Выполняет SQL-запрос и возвращает результат (если требуется)."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()

    def commit(self):
        """Фиксирует изменения в базе данных."""
        with self.connect() as conn:
            conn.commit()


# Создаем экземпляр Database
db = Database()