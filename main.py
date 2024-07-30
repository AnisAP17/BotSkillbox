import requests
import telebot
from config import (BOT_TOKEN,
                    DEFAULT_COMMANDS,
                    HEADERS)
from telebot.types import (Message,
                           BotCommand)
from models import (User,
                    History,
                    db)

# Инициализация бота с токеном
bot = telebot.TeleBot(BOT_TOKEN)

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

# Обработка команды /help
@bot.message_handler(commands=["help"])
def help_command(message: Message):
    # Формируем текст с описанием доступных команд
    help_text = ""
    for command, description in DEFAULT_COMMANDS:
        help_text += f"\n/{command} - {description}"
    bot.send_message(message.from_user.id, f"This movie search bot has all its features: {help_text}")

# Обработка команды /movie_search
@bot.message_handler(commands=['movie_search'])
def movie_search(message: Message):
    # Запрашиваем у пользователя название фильма
    msg = bot.reply_to(message, "Please enter the name of the movie:")
    # Регистрируем следующий шаг после получения ответа пользователя
    bot.register_next_step_handler(msg, search_movie)

def search_movie(message: Message):
    # Подготавливаем запрос для поиска фильма по имени
    movie_name = message.text.split(" ")
    movie_name_url = "%20".join(movie_name)
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?limit=1&query={movie_name_url}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    # Если фильмы найдены, обрабатываем их
    if data['docs']:
        movies = data['docs']
        for movie in movies:
            title = movie.get('name', 'N/A')
            year = movie.get('year', 'N/A')
            description = movie.get('description', 'N/A')
            truncated_description = truncate_description(description, 20)
            rating = movie.get('rating', {}).get('imdb', 'N/A')
            genres = movie.get('genres', [])
            genres_list = ", ".join([genre['name'] for genre in genres]) if genres else 'N/A'
            ageRating = movie.get('ageRating', 'N/A')
            poster = movie.get('poster', {}).get('url', 'N/A')

            # Создаем запись в истории поиска
            History.create(
                user_id = message.from_user.id or 'N/A',
                movie_name = title or 'N/A',
                description = truncated_description or 'N/A',
                rating = rating or 'N/A',
                year = year or 'N/A',
                genres = genres_list or 'N/A',
                ageRating = ageRating or 'N/A',
                poster = poster or 'N/A'
            )

    # Отправляем информацию о фильме пользователю
    movie_info(message, response)

# Обработка команды /movie_by_rating
@bot.message_handler(commands=['movie_by_rating'])
def movie_by_rating(message: Message):
    # Запрашиваем у пользователя рейтинг фильма
    msg = bot.reply_to(message, "Write the rating in the form 1 to 10")
    # Регистрируем следующий шаг после получения рейтинга
    bot.register_next_step_handler(msg, search_movie_by_rating)

def search_movie_by_rating(message: Message):
    # Подготавливаем запрос для поиска фильмов по рейтингу
    rating = message.text
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?limit=5&rating.imdb={rating}-10"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)

# Обработка команды /low_budget_movie
@bot.message_handler(commands=['low_budget_movie'])
def low_budget_movie(message: Message):
    # Подготавливаем запрос для поиска фильмов с низким бюджетом
    url = "https://api.kinopoisk.dev/v1.4/movie?limit=5&selectFields=&notNullFields=budget.value&notNullFields=name&notNullFields=description&sortField=budget.value&sortType=-1"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)

# Обработка команды /high_budget_movie
@bot.message_handler(commands=['high_budget_movie'])
def high_budget_movie(message: Message):
    # Подготавливаем запрос для поиска фильмов с высоким бюджетом
    url = "https://api.kinopoisk.dev/v1.4/movie?limit=5&selectFields=&notNullFields=budget.value&notNullFields=name&notNullFields=description&sortField=budget.value&sortType=1"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)

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

def movie_info(message: Message, movie):
    # Получаем данные о фильмах из ответа API
    data = movie.json()
    if data['docs']:
        movies = data['docs']
        for movie in movies:
            title = movie.get('name', 'N/A')
            year = movie.get('year', 'N/A')
            description = movie.get('description', 'N/A')
            truncated_description = truncate_description(description, 20)
            rating = movie.get('rating', {}).get('imdb', 'N/A')
            genres = movie.get('genres', [])
            genres_list = ", ".join([genre['name'] for genre in genres]) if genres else 'N/A'
            ageRating = movie.get('ageRating', 'N/A')
            poster = movie.get('poster', {}).get('url', 'N/A')
            bot.reply_to(message, f"Title: {title}\n"
                    f"Description: {truncated_description}\n"
                    f"Rating: {rating}\n"
                    f"Year: {year}\n"
                    f"Genres: {genres_list}\n"
                    f"AgeRating: {ageRating}\n"
                    f"Poster: {poster}")
    else:
        return "Movie not found."

def truncate_description(description, word_limit):
    # Обрезаем описание до указанного лимита слов
    words = description.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + '...'
    return description

if __name__ == "__main__":
    # Устанавливаем команды бота и начинаем его работу
    bot.set_my_commands([BotCommand(*i) for i in DEFAULT_COMMANDS])
    bot.infinity_polling()
