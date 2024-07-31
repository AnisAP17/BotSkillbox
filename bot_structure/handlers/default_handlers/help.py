from telebot.types import Message
from loader import bot
from config_data.config import DEFAULT_COMMANDS


# Обработка команды /help
@bot.message_handler(commands=["help"])
def help_command(message: Message):
    # Формируем текст с описанием доступных команд
    help_text = ""
    for command, description in DEFAULT_COMMANDS:
        help_text += f"\n/{command} - {description}"
    bot.send_message(message.from_user.id, f"This movie search bot has all its features: {help_text}")
