from .database import db

class QuerySet:
    def __init__(self, model_class):
        self.model_class = model_class
        self.query = f"SELECT * FROM {model_class.__name__}"
        self.params = None

    def filter(self, **kwargs):
        conditions = " AND ".join([f"{key}=?" for key in kwargs])
        self.query += f" WHERE {conditions}"
        self.params = tuple(kwargs.values())
        return self

    def all(self):
        result = db.execute(self.query, self.params, fetch=True)
        return [self.model_class(**dict(zip(self.model_class._fields.keys(), row))) for row in result]

    def create(self, **kwargs):
        """
        Создает новую запись в базе данных.
        :param kwargs: Значения полей для новой записи.
        :return: Созданный экземпляр модели.
        """
        # Формируем список полей и значений для INSERT
        fields = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = tuple(kwargs.values())

        # Формируем SQL-запрос
        insert_query = f"INSERT INTO {self.model_class.__name__} ({fields}) VALUES ({placeholders})"

        # Выполняем запрос
        db.execute(insert_query, values)
        db.commit()  # Фиксируем изменения

        # Возвращаем созданный объект модели
        return self.model_class(**kwargs)