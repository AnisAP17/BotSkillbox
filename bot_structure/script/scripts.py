from loader import bot
from telebot.types import Message
from config_data.config import HEADERS
import requests
from models.models import History, User
import datetime

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
            bot.reply_to(message,
                    text=(f"Название: {title}\n"
                        f"Описание: {truncated_description}\n"
                        f"Рейтинг: {rating}\n"
                        f"Год: {year}\n"
                        f"Жанры: {genres_list}\n"
                        f"Возрастное ограничение: {ageRating}+\n"
                        f"Постер: {poster}")
                        )
    else:
        return "Movie not found."



def limit_search_movie(message: Message):
    msg = bot.reply_to(message, "Введите количество вариантов:")
    bot.register_next_step_handler(msg, search_movie, message.text)


def search_movie(message: Message, film):
    # Подготавливаем запрос для поиска фильма по имени
    movie_name = film.split(" ")
    movie_name_url = "%20".join(movie_name)
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?limit={message.text}&query={movie_name_url}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    # Если фильмы найдены, обрабатываем их
    if data['docs']:
        movies = data['docs']
        for movie in movies:
            user_info = User.select().where(User.user_id == message.from_user.id)
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
                user_id = user_info or 'N/A',
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



def search_movie_by_rating(message: Message):
    # Подготавливаем запрос для поиска фильмов по рейтингу
    rating = message.text
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?limit=5&rating.imdb={rating}-10"
    response = requests.get(url, headers=HEADERS)
    # Отправляем информацию о фильмах пользователю
    movie_info(message, response)


def truncate_description(description, word_limit):
    # Обрезаем описание до указанного лимита слов
    words = description.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + '...'
    return description


def get_start_date(message: Message):
    try:
        start_date = datetime.datetime.strptime(message.text, '%Y-%m-%d')
        bot.send_message(message.chat.id, 'Напишите конечную дату в формате ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(message, get_end_date, start_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(message, get_start_date)


def get_end_date(message: Message, start_date):
    try:
        end_date = datetime.datetime.strptime(message.text, '%Y-%m-%d')
        search_history_user(message, start_date, end_date)
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(message, get_end_date, start_date)


def search_history_user(message: Message, start_date, end_date):
    user = User.select().where(User.user_id == message.from_user.id)

    if user:
        history = History.select().where(
            (History.user_id == user) &
            (History.date.between(start_date, end_date))
        )

        if history:
            for user_history in history:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=(f"Название: {user_history.movie_name}\n"
                        f"Описнаие: {user_history.description}\n"
                        f"Рейтинг: {user_history.rating}\n"
                        f"Год: {user_history.year}\n"
                        f"Жанры: {user_history.genres}\n"
                        f"Возрастное ограничение: {user_history.ageRating}+\n"
                        f"Постер: {user_history.poster}")
                            )
        else:
            bot.send_message(message.chat.id, 'История не найдена.')
    else:
        bot.send_message(message.chat.id, 'Пользователь не найден.')

