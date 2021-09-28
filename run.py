from app import bot, token
from app.main import daily_word,start_sale

if __name__ == '__main__':
    bot.run(token)
    daily_word.start()
    start_sale.start()
    