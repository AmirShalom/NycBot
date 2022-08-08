import logging
import os
from sodapy import Socrata
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def show_days(update, context):
    logging.info("Starting show_days function")
    menu = [
    [InlineKeyboardButton('Sunday', callback_data=f"Sunday")],
    [InlineKeyboardButton('Monday', callback_data=f"Monday")],
    [InlineKeyboardButton('Tuesday', callback_data=f"Tuesday")],
    [InlineKeyboardButton('Wednesday', callback_data=f"Wednesday")],
    [InlineKeyboardButton('Thursday', callback_data=f"Thursday")],
    [InlineKeyboardButton('Friday', callback_data=f"Friday")],
    [InlineKeyboardButton('Saturday', callback_data=f"Saturday")],
    [InlineKeyboardButton('Closest Market', callback_data=f"closest")]
    ]
    reply_markup = InlineKeyboardMarkup(menu)
    query = update.callback_query
    query.answer()
    query.edit_message_text(f"""
    Welcome to the NYC farmers' markets bot,
Please select a day and I will show what farmers' markets we have that day.
    """, reply_markup=reply_markup)


def get_results():
    logging.info('Getting farmers markets data')
    client = Socrata("data.cityofnewyork.us", os.getenv('OPENDATA_API_TOKEN'))
    results = client.get("8vwk-6iz2")
    return results


def fetch_data(update, context):
    logging.info('Fetching user input')
    if update.callback_query:
        query = update.callback_query
        logging.info('User input is: {}'.format(query['data']))
        if query['data'] == 'closest':
            return
        else:
            results = get_results()
            message = "The farmers' markets open on {} are: \n\n".format(query['data'])
            for market in results:
                if market['daysoperation'] == query['data']:
                    message += "\U0001F33D {} @ {}\n\n".format(market['streetaddress'], market['hoursoperations'])
            message += "Thank you for using the NYC bot.\nYou are welcome to run the NYC bot again using the /start option"
            query.edit_message_text(parse_mode=telegram.ParseMode.HTML, text=message)
            return ConversationHandler.END


def calculate_closest(update, context, user_latitude, user_longitude):
    results = get_results()
    logging.info("Calculating the closest market")
    markets_dst = {}
    for market in results:
        market_latitude = float(market['latitude'])
        market_longitude = float(market['longitude'])
        dst_from_user = abs(abs(user_latitude) - abs(market_latitude)) + abs(abs(user_longitude) - abs(market_longitude))
        markets_dst[market['streetaddress']] = dst_from_user

    closest_market = min(markets_dst, key=markets_dst.get)
    message_content = "The closest farmers' market is here: {} \n\n".format(closest_market)

    update.edited_message.reply_text(parse_mode=telegram.ParseMode.HTML, text=message_content)


def is_open(hoursoperations):
    logging.info('Checking if the market is open now')
    start = []
    end = []
    time_list = hoursoperations.split('-')

    for i in time_list[0]:
        start.append(i)
    if start[-2] == 'p':
        start = int(start[0] + 12)
    else:
        if start[0] != '1':
            start = int(start[0])
        else:
            start = int(start[0])*10 + int(start[1])

    for i in time_list[1]:
        end.append(i)
    if end[-2] == 'p':
        end = int(end[0]) + 12
    else:
        end = int(end[0])*10 + int(end[1])

    hour_now = int(datetime.now().strftime("%H"))
    if (hour_now < end) and (hour_now > start):
        return True
