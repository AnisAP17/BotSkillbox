from telebot.types import Message
from loader import bot
import requests
from config_data.config import HEADERS
from script.scripts import movie_info

# Обработка команды /high_budget_movie
@bot.message_handler(commands=['high_budget_movie'])
def high_budget_movie(message: Message):
    # Подготавливаем запрос для поиска фильмов с высоким бюджетом
    url = "https://api.kinopoisk.dev/v1.4/movie?limit=5&selectFields=&notNullFields=budget.value&notNullFields=name&notNullFields=description&sortField=budget.value&sortType=1"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)