import requests
import telebot
from config import BOT_TOKEN, DEFAULT_COMMANDS
from telebot.types import Message, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from models import User, db

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_bot(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "N/A"
    last_name = message.from_user.last_name or "N/A"

    user, created = User.get_or_create(
        user_id=user_id,
        defaults={'username': username, 'first_name': first_name, 'last_name': last_name}
    )

    if created:
        bot.reply_to(message, "Добро пожаловать в менеджер задач!")
    else:
        bot.reply_to(message, f"Рад вас снова видеть, {first_name}!")


@bot.message_handler(commands=["help"])
def start_bot(message: Message):
    help_text = ""
    for command, description in DEFAULT_COMMANDS:
        help_text += f"\n/{command} - {description}"
    bot.send_message(message.from_user.id, f"Этот бот для интернет-магазина вот все его возможности: {help_text}")


"""Функция для выбора категории товара"""
@bot.message_handler(commands=["category"])
def category(message: Message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup()
    category_api = requests.get('https://fakestoreapi.com/products/categories').json()

    for i in category_api:
        markup.add(InlineKeyboardButton(f"{i}", callback_data=f"category_{i}"))

    bot.send_message(user_id, "Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def callback_query(call):
    category_name = call.data.replace("category_", "")
    bot.answer_callback_query(call.id, f"You chose {category_name}")
    products = requests.get(f'https://fakestoreapi.com/products/category/{category_name}').json()
    product_markup = InlineKeyboardMarkup()
    for product in products:
        product_markup.add(InlineKeyboardButton(f"{product['title']}", callback_data=f"product_{product['id']}"))

    bot.send_message(call.message.chat.id, f"Products in category {category_name}:", reply_markup=product_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_callback_query(call):
    product_id = call.data.replace("product_", "")
    product = requests.get(f'https://fakestoreapi.com/products/{product_id}').json()

    product_info = (
        f"Title: {product['title']}\n"
        f"Price: ${product['price']}\n"
        f"Description: {product['description']}\n"
        f"Category: {product['category']}\n"
        f"Rating: {product['rating']['rate']} ({product['rating']['count']} reviews)"
    )

    bot.send_message(call.message.chat.id, product_info)


"""Функция обрабатывает команду hello_world"""
@bot.message_handler(commands=["hello_world"])
def hello_world(message: Message):
    """Функция hello_world выводит сообщение Hello, world!"""
    bot.send_message(message.from_user.id, f"Hello, world!")


"""Функция обрабатывает все приветственные сообщения"""
@bot.message_handler()
def hello_bot(message: Message):
    """Функция hello_func принимает проверяет все приветственные сообщения и выдает ответ"""
    if message.text.lower() == "привет" or message.text == "здравствуй":
        bot.send_message(message.from_user.id, f"Привет! {message.from_user.first_name}, чем могу быть полезен, если хочешь узнать все команды то набери команду /help")
    elif message.text.lower() == "hello" or message.text == "hi":
        bot.send_message(message.from_user.id, f"Привет! {message.from_user.first_name}, чем могу быть полезен, если хочешь узнать все команды то набери команду /help")


if __name__ == "__main__":
    bot.set_my_commands([BotCommand(*i) for i in DEFAULT_COMMANDS])
    bot.infinity_polling()
