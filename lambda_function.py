import json

import requests
from geopy.geocoders import Nominatim


class GeoCoder:

    def __init__(self):
        self.BASE_URL = 'http://router.project-osrm.org/route/v1/driving/'
        self.geo_locator = Nominatim(user_agent='driving-distance/1')

    def geocode(self, zip_code):
        """Returns geo-coded location for the zip code, see: https://geopy.readthedocs.io/en/stable/#
        :param zip_code: the zip code the geocode
        :return: a Location object for the geo-coded zip code
        """
        return self.geo_locator.geocode(zip_code, country_codes='NL')

    def get_locations(self, zip_codes):
        """Geo-codes two zip codes into a Location object.
        :param zip_codes:
        :return: a list of two geo-coded location objects
        """
        return [self.geocode(zip_codes[z]) for z in ['zip_from', 'zip_to']]

    def get_driving_distance(self, origin, destination):
        """Returns the driving distance between two locations.
        :param origin: the start location
        :param destination: the end location
        :return: the driving distance between origin an destination
        """
        distance = 0
        url = '{}{},{};{},{}?overview=false'.format(self.BASE_URL,
                                                    origin.longitude, origin.latitude, destination.longitude,
                                                    destination.latitude)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            route = json.loads(r.text)['routes'][0]
            distance = route['distance'] / 1000  # to km
        else:
            r.raise_for_status()

        return distance


def lambda_handler(event, context):
    """Handles the incoming lambda request.
    :param event: the HTTP request
    :param context:
    :return: a HTTP response in JSON format
    """
    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': {
            'message': 'ok',
            'distance': 0
        }
    }

    gc = GeoCoder()
    try:
        locations = gc.get_locations(event['pathParameters'])
        response['body']['distance'] = gc.get_driving_distance(locations[0], locations[1])
    except Exception as e:
        response['body']['message'] = 'An error occurred: {}'.format(e)

    response['body'] = json.dumps(response['body'])
    return response
