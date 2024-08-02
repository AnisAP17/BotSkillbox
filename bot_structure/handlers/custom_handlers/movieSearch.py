from loader import bot
from telebot.types import Message
from script.scripts import limit_search_movie

# Обработка команды /movie_search
@bot.message_handler(commands=['movie_search'])
def movie_search(message: Message):
    # Запрашиваем у пользователя название фильма
    msg = bot.reply_to(message, "Введите название фильма:")
    # Регистрируем следующий шаг после получения ответа пользователя
    bot.register_next_step_handler(msg, limit_search_movie)