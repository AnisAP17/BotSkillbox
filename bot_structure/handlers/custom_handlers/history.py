from loader import bot
from telebot.types import Message
from script.scripts import get_start_date

# Обработка команды /history
@bot.message_handler(commands=['history'])
def start_date_func(message: Message):
    bot.send_message(message.chat.id, 'Напишите начальную дату в формате ГГГГ-ММ-ДД:')
    bot.register_next_step_handler(message, get_start_date)

