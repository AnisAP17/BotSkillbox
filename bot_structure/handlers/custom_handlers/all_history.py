from telebot import TeleBot, types
from telegram_bot_pagination.pag import InlineKeyboardPaginator
from models import models
from loader import bot


# Количество записей на одной странице
records_per_page = 5

# Функция для получения записей из базы данных
def get_records_for_page(user_id, page, records_per_page):
    query = (models.History
             .select()
             .where(models.History.user_id == user_id)
             .order_by(models.History.date.desc())
             .paginate(page, records_per_page))
    return list(query)

# Функция для получения общего количества страниц
def get_total_pages(user_id, records_per_page):
    total_records = models.History.select().where(models.History.user_id == user_id).count()
    total_pages = (total_records + records_per_page - 1) // records_per_page
    return total_pages

@bot.message_handler(commands=['all_history'])
def send_history(message: types.Message):
    user_id = models.User.select().where(models.User.user_id == message.from_user.id)

    # Получаем общее количество страниц
    total_pages = get_total_pages(user_id, records_per_page)

    # Если история пуста, сообщаем об этом пользователю
    if total_pages == 0:
        bot.send_message(message.chat.id, 'No history found.')
        return

    # Инициализируем пагинатор
    paginator = InlineKeyboardPaginator(
        page_count=total_pages,
        current_page=1,
        data_pattern='page#{page}'
    )

    # Получаем записи для первой страницы
    records = get_records_for_page(user_id, 1, records_per_page)

    # Формируем сообщение
    text = "\n\n".join([f"Title: {record.movie_name}\nDescription: {record.description}\nDate: {record.date}\nPoster: {record.poster}" for record in records])

    # Создаем разметку клавиатуры
    markup = types.InlineKeyboardMarkup()
    for button in paginator.keyboard:
        markup.add(types.InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('page#'))
def callback_inline(call: types.CallbackQuery):
    # Получаем номер страницы из данных callback
    page = int(call.data.split('#')[1])
    user_id = models.User.select().where(models.User.user_id == call.from_user.id)

    # Получаем общее количество страниц
    total_pages = get_total_pages(user_id, records_per_page)

    # Инициализируем пагинатор для текущей страницы
    paginator = InlineKeyboardPaginator(
        page_count=total_pages,
        current_page=page,
        data_pattern='page#{page}'
    )

    # Получаем записи для текущей страницы
    records = get_records_for_page(user_id, page, records_per_page)

    # Формируем сообщение
    text = "\n\n".join([f"Title: {record.movie_name}\nDescription: {record.description}\nDate: {record.date}\nPoster: {record.poster}" for record in records])

    # Создаем разметку клавиатуры
    markup = types.InlineKeyboardMarkup()
    for button in paginator.keyboard:
        markup.add(types.InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))

    bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )