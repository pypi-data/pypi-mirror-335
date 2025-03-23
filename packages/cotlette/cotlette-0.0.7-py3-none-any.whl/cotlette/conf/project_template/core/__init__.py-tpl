from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cotlette.models import Model
from cotlette.fields import CharField, IntegerField

# Создаем экземпляр FastAPI
app = FastAPI()

# Pydantic-модель для создания нового пользователя
class UserCreate(BaseModel):
    name: str
    age: int

# Pydantic-модель для представления пользователя
class User(BaseModel):
    id: int
    name: str
    age: int

# Определение модели пользователя через ORM
class UserModel(Model):
    name = CharField(max_length=50)
    age = IntegerField()

# Создание таблицы при запуске приложения
@app.on_event("startup")
def create_tables():
    UserModel.create_table()

# Пример GET-эндпоинта: приветствие
@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в FastAPI!"}

# Создание нового пользователя (POST)
@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    new_user = UserModel.objects.create(
        name=user.name,
        age=user.age
    )
    return {"id": 1, "name": new_user.name, "age": new_user.age}

# Получение всех пользователей (GET)
@app.get("/users/", response_model=None)
def get_users():
    users = UserModel.objects.all()
    return list(users)
