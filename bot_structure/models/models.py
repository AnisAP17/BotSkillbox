from peewee import (Model,
                    SqliteDatabase,
                    IntegerField,
                    CharField,
                    ForeignKeyField,
                    DateTimeField,
                    TextField)
import datetime
import os

# Определите путь к директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Создайте путь к базе данных в папке 'database'
db_path = os.path.join(project_root, 'database', 'database.db')

# Инициализируйте базу данных
db = SqliteDatabase(db_path)

# Базовая модель, от которой наследуются все модели
class BaseModel(Model):
    class Meta:
        # Указываем, что база данных для всех моделей - это 'db'
        database = db

# Модель для хранения информации о пользователях
class User(BaseModel):
    user_id = IntegerField(unique=True)  # Идентификатор пользователя, уникальный
    first_name = CharField(null=True)     # Имя пользователя
    last_name = CharField(null=True)      # Фамилия пользователя
    username = CharField(null=True)       # Имя пользователя в Telegram

    def __str__(self):
        # Строковое представление пользователя (имя пользователя или ID)
        return f"User: {self.user_id}; Username: {self.username}"

# Модель для хранения истории поиска фильмов
class History(BaseModel):
    user_id = ForeignKeyField(User, backref='history', on_delete='CASCADE')  # Внешний ключ на пользователя
    date = DateTimeField(default=datetime.datetime.now)  # Дата и время поиска (по умолчанию текущее время)
    movie_name = CharField()     # Название фильма
    description = TextField()   # Описание фильма
    rating = IntegerField()     # Рейтинг фильма
    year = IntegerField()       # Год выпуска фильма
    genres = CharField()        # Жанры фильма
    ageRating = IntegerField()  # Возрастной рейтинг фильма
    poster = CharField(max_length=300)  # URL постера фильма

    def __str__(self):
        # Строковое представление записи в истории (имя пользователя и название фильма)
        return f"Search by : {self.movie_name} at {self.date}"

# Подключаемся к базе данных и создаем таблицы
db.connect()
db.create_tables([User, History])
