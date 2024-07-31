from loader import bot
from telebot.types import Message
from config_data.config import HEADERS
import requests
from models.models import History


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