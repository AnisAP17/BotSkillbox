from loader import bot
from utils.set_default_commands import set_default_commands
from handlers.custom_handlers import highBudgetMovie, history, lowBudgetMovie, movieByRating, movieSearch, all_history
from handlers.default_handlers import start, help

if __name__ == "__main__":
    # Устанавливаем команды бота и начинаем его работу
    set_default_commands(bot)
    bot.infinity_polling()
