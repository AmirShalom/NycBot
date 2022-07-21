import os
import pyTelegramBotAPI
from sodapy import Socrata


def fetch_data(content):
    OPENDATA_API_TOKEN = os.getenv('OPENDATA_API_TOKEN')
    client = Socrata("data.cityofnewyork.us", os.getenv(OPENDATA_API_TOKEN))
    results = client.get(content)
    return results


def filter_markets(data):
    for market in data:
        if market['daysoperation'] == 'Tuesday':
            print('The market name is: {} \nthe address is: {} \nthe opening hours are: {}'.
                  format(market['marketname'], market['streetaddress'], market['hoursoperations']))


if __name__ == '__main__':
    TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
    bot = pyTelegramBotAPI.TeleBot(TELEGRAM_API_TOKEN)

    @bot.message_handler(command=['markets'])
    def markets(message):
        bot.reply_to(message, 'koko')

    bot.polling()

    markets_code = "8vwk-6iz2"
    data = fetch_data(content=markets_code)
    filter_markets(data)

