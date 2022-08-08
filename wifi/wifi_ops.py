import itertools
import logging
import os
from sodapy import Socrata
import telegram


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

    closest_wifi = min(wifi_dst, key=wifi_dst.get)
    message_content = "The closest free wifi is here: {} \n\n".format(closest_wifi)

    update.edited_message.reply_text(parse_mode=telegram.ParseMode.HTML, text=message_content)