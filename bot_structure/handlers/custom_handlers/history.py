from loader import bot
from models.models import History
from telebot.types import Message

# Обработка команды /history
@bot.message_handler(commands=['history'])
def search_history_user(message: Message):
    # Получаем историю запросов пользователя
    history = History.select().where(History.user_id == message.from_user.id)

    # Если история пуста, сообщаем об этом пользователю
    if not history:
        bot.send_message(message.chat.id, 'No history found.')

    # Отправляем информацию из истории пользователю
    for user_history in history:
        bot.send_message(message.from_user.id,
            f"Title: {user_history.movie_name}\n"
            f"Description: {user_history.description}\n"
            f"Rating: {user_history.rating}\n"
            f"Year: {user_history.year}\n"
            f"Genres: {user_history.genres}\n"
            f"Age Rating: {user_history.ageRating}\n"
            f"Poster: {user_history.poster}"
        )
