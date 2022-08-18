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
        for network in results:
            if network['location'] == list(sorted_wifi_dst.keys())[i]:
                net_name = network['ntaname']
                url = "https://www.google.com/maps/dir/?api=1&destination={}%2c{}".format(network['lat'], network['lon'])
                message_content += "\U0001F4F6 Wifi Name:\n{} @ [{}]({}) \n\n".format(net_name, (list(sorted_wifi_dst.keys()))[i], url)
    update.edited_message.reply_text(parse_mode=telegram.ParseMode.MARKDOWN, text=message_content, disable_web_page_preview=True)

    return ConversationHandler.END