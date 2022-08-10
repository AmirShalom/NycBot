import argparse
import json
import requests
import os
from sodapy import Socrata
import urllib
import time


def get_bath_data():
    OPENDATA_API_TOKEN = os.getenv('OPENDATA_API_TOKEN')
    client = Socrata("data.cityofnewyork.us", OPENDATA_API_TOKEN)
    results = client.get("hjae-yuav")
    return results


def get_geo_location(bath_data, work_dir):
    GOOGLE_MAPS_KEY = os.getenv('MAPS_API_TOKEN')
    counter = 0
    while counter < len(bath_data):
        if counter > 498:
            time.sleep(2)  # https://developers.google.com/maps/faq#usage-limits - 500 qps limit
        if 'location' in bath_data[counter]:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + \
                  urllib.parse.quote(bath_data[counter]['location']) + \
                  '&key={}'.format(GOOGLE_MAPS_KEY)
            response = requests.get(url)
            resp_json_payload = response.json()
            if resp_json_payload['results']:
                with open(work_dir+'/'+'bath_geo_location.json', 'r+') as file:
                    file_data = json.load(file)
                    file_data['data'].append(resp_json_payload['results'][0])
                    file.seek(0)
                    json.dump(file_data, file, indent=4)
        counter += 1


def main():
    """
    Querying Google Maps API pricing model: https://mapsplatform.google.com/pricing/
    To reduce costs and to efficient the workflow, this script will dump all data to a json file
    and the bot will fetch the data from it
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--work-dir', help="Full path of the working directory with no following /")
    args = parser.parse_args()

    bath_data = get_bath_data()
    get_geo_location(bath_data, args.work_dir)

if __name__ == '__main__':
    main()
