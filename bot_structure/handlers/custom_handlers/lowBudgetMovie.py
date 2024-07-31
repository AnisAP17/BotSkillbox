from telebot.types import Message
from loader import bot
from config_data.config import HEADERS
import requests
from script.scripts import movie_info

# Обработка команды /low_budget_movie
@bot.message_handler(commands=['low_budget_movie'])
def low_budget_movie(message: Message):
    # Подготавливаем запрос для поиска фильмов с низким бюджетом
    url = "https://api.kinopoisk.dev/v1.4/movie?limit=5&selectFields=&notNullFields=budget.value&notNullFields=name&notNullFields=description&sortField=budget.value&sortType=-1"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)