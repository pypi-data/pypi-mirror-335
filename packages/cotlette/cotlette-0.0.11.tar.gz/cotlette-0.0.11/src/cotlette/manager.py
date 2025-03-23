from .query import QuerySet

class Manager:
    def __init__(self, model_class):
        self.model_class = model_class

    def filter(self, **kwargs):
        return QuerySet(self.model_class).filter(**kwargs)

    def all(self):
        return QuerySet(self.model_class).all()

    def create(self, **kwargs):
        """
        Создает новую запись в базе данных.
        :param kwargs: Значения полей для новой записи.
        :return: Созданный экземпляр модели.
        """
        return QuerySet(self.model_class).create(**kwargs)