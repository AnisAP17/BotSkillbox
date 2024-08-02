import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


DEFAULT_COMMANDS = (
    ('start', 'Регистрация или приветствие'),
    ('help', 'Показать все доступные команды'),
    ('movie_search', 'поиск фильма/сериала по названию'),
    ('movie_by_rating', 'поиск фильмов/сериалов по рейтингу'),
    ('low_budget_movie', 'поиск фильмов/сериалов с низким бюджетом'),
    ('high_budget_movie', 'поиск фильмов/сериалов с высоким бюджетом'),
    ('history', 'возможность просмотра истории поиска фильма/сериала'),
    ('all_history', 'возможность просмотра всей истории поиска фильма/сериала'),
)


HEADERS = {
    "accept": "application/json",
    "X-API-KEY": os.getenv("X-API-KEY")
}