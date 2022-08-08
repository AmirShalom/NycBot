import logging
import os
import requests
from sodapy import Socrata
import telegram
import urllib
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
    GOOGLE_MAPS_KEY = os.getenv('MAPS_API_TOKEN')
    bathrooms_dst = {}
    results = get_results()
    for bathroom in results:
        if 'location' in bathroom:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + urllib.parse.quote(bathroom['location']) + '&key={}'.format(GOOGLE_MAPS_KEY)
            response = requests.get(url)
            resp_json_payload = response.json()
            if resp_json_payload['results']:
                # print(resp_json_payload['results'])
                bathroom_latitude = resp_json_payload['results'][0]['geometry']['location']['lat']
                bathroom_longitude = resp_json_payload['results'][0]['geometry']['location']['lng']
                dst_from_user = abs(abs(user_latitude) - abs(bathroom_latitude)) + abs(abs(user_longitude) - abs(bathroom_longitude))
                bathrooms_dst[bathroom['location']] = dst_from_user

    closest_bathroom = min(bathrooms_dst, key=bathrooms_dst.get)
    message_content = "The closest public bathroom is here: {} \n\n".format(closest_bathroom)

    message_content += "Thank you for using the NYC bot.\nYou are welcome to run the NYC bot again using the /start option"
    update.edited_message.reply_text(parse_mode=telegram.ParseMode.HTML, text=message_content)
    return ConversationHandler.END
