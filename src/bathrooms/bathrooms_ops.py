import json
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
    logging.info('Getting Bathrooms data')
    OPENDATA_API_TOKEN = os.getenv('OPENDATA_API_TOKEN')
    client = Socrata("data.cityofnewyork.us", OPENDATA_API_TOKEN)
    results = client.get("hjae-yuav")
    return results


def calculate_closest(update, context, user_latitude, user_longitude):
    logging.info("Calculating the closest Bathroom")
    bathrooms_dst = {}

    with open('./bathrooms/bath_geo_location.json') as data_file:
        data = json.load(data_file)
        for bath in data['data']:
            bathroom_latitude = bath['geometry']['location']['lat']
            bathroom_longitude = bath['geometry']['location']['lng']
            dst_from_user = abs(abs(user_latitude) - abs(bathroom_latitude)) + abs(abs(user_longitude) - abs(bathroom_longitude))
            bathrooms_dst[bath['address_components'][0]['long_name']] = dst_from_user

    sorted_bath_dst = {k: v for k, v in sorted(bathrooms_dst.items(), key=lambda item: item[1])}
    message_content = "The closest public bathrooms are here: \n\n"
    for i in range(0, 5):
        for bath in data['data']:
            if bath['address_components'][0]['long_name'] == list(sorted_bath_dst)[i]:
                url = "https://www.google.com/maps/dir/?api=1&destination={}%2c{}".\
                    format(bath['geometry']['location']['lat'], bath['geometry']['location']['lng'])
                message_content += "\U0001F6BD [{}]({}) \n\n".format(list(sorted_bath_dst.keys())[i], url)
    update.edited_message.reply_text(parse_mode=telegram.ParseMode.MARKDOWN, text=message_content, disable_web_page_preview=True)

    return ConversationHandler.END

