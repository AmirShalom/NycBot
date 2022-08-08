import itertools
import logging
import os
from sodapy import Socrata
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data(update, context):
    logging.info('Fetching user input')
    return get_results()


def get_results():
    logging.info('Getting Wifi data')
    client = Socrata("data.cityofnewyork.us", os.getenv('OPENDATA_API_TOKEN'))
    results = client.get_all("varh-9tsp")
    all_results = list(itertools.islice(results, 10000))
    return all_results


def calculate_closest(update, context, user_latitude, user_longitude):
    logging.info("Calculating the closest wifi")
    results = get_results()
    wifi_dst = {}
    for wifi in results:
        wifi_latitude = float(wifi['the_geom']['coordinates'][0])
        wifi_longitude = (wifi['the_geom']['coordinates'][1])
        dst_from_user = abs(abs(user_latitude) - abs(wifi_latitude)) + abs(abs(user_longitude) - abs(wifi_longitude))
        wifi_dst[wifi['location']] = dst_from_user

    sorted_wifi_dst = {k: v for k, v in sorted(wifi_dst.items(), key=lambda item: item[1])}
    message_content = "The closest free wifi spots are here: \n\n"
    for i in range(0, 5):
        message_content += "\U0001F4F6 {} \n\n".format(list(sorted_wifi_dst.keys())[i])

    message_content += "Thank you for using the NYC bot.\nYou are welcome to run the NYC bot again using the /start option"
    update.edited_message.reply_text(parse_mode=telegram.ParseMode.HTML, text=message_content)
    return ConversationHandler.END