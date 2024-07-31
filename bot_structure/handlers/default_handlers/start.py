from telebot.types import Message
from loader import bot
from models.models import User

# Обработка команды /start
@bot.message_handler(commands=["start"])
def start_bot(message: Message):
    # Получаем информацию о пользователе из сообщения
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "N/A"
    last_name = message.from_user.last_name or "N/A"

    # Создаем нового пользователя или получаем существующего
    user, created = User.get_or_create(
        user_id=user_id,
        defaults={'username': username, 'first_name': first_name, 'last_name': last_name}
    )

    # Отправляем приветственное сообщение в зависимости от того, был ли пользователь создан
    if created:
        bot.reply_to(message, "Welcome!")
    else:
        bot.reply_to(message, f"Nice to see you again, {first_name}!")