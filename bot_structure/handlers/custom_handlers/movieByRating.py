from telebot.types import Message
from loader import bot
from script.scripts import search_movie_by_rating

# Обработка команды /movie_by_rating
@bot.message_handler(commands=['movie_by_rating'])
def movie_by_rating(message: Message):
    # Запрашиваем у пользователя рейтинг фильма
    msg = bot.reply_to(message, "Write the rating in the form 1 to 10")
    # Регистрируем следующий шаг после получения рейтинга
    bot.register_next_step_handler(msg, search_movie_by_rating)