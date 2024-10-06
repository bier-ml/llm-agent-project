import os

import telebot
from dotenv import load_dotenv

from client.coin_client import get_coin_price_history

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
print(TELEGRAM_TOKEN)

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, 'Hello! Use /price <symbol> to get daily price data, e.g., /price hamster')


@bot.message_handler(commands=['price'])
def send_price(message):
    try:
        symbol = message.text.split()[1].lower()
    except IndexError:
        bot.reply_to(message, "Please specify a cryptocurrency symbol, e.g., /price hamster.")
        return

    days = 7  # Fetch data for the past 7 days
    df = get_coin_price_history(symbol, days=days)

    if df is not None:
        prices_text = df['price'].tail(days).to_string()
        bot.reply_to(message, f"Daily prices for {symbol}:\n{prices_text}")
    else:
        bot.reply_to(message, f"Could not retrieve data for {symbol}. Please try again.")


if __name__ == '__main__':
    bot.infinity_polling()
