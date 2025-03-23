from .fields import CharField, IntegerField, Field
from .manager import Manager
from .database import db

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name != "Model":
            fields = {}
            for key, value in attrs.items():
                if isinstance(value, Field):
                    fields[key] = value
            attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)

class Model(metaclass=ModelMeta):
    objects = Manager(None)

    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.objects.model_class = cls

    @classmethod
    def create_table(cls):
        columns = []
        for field_name, field in cls._fields.items():
            column_def = f"{field_name} {field.column_type}"
            if field.primary_key:
                column_def += " PRIMARY KEY"
            columns.append(column_def)
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__} ({', '.join(columns)})"
        db.execute(query)  # Выполняем запрос на создание таблицы
        db.commit()        # Фиксируем изменения