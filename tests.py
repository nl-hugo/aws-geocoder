import json
from unittest import TestCase

from lambda_function import GeoCoder, lambda_handler


class TestGeoCoder(TestCase):
    def setUp(self):
        self.geo_coder = GeoCoder()


class TestInit(TestGeoCoder):
    def test_initial_geo_locator(self):
        self.assertEqual(self.geo_coder.geo_locator.domain, 'nominatim.openstreetmap.org')


class TestGeoCode(TestGeoCoder):
    def test_zip_code_none(self):
        self.assertIsNotNone(self.geo_coder.geocode(None))

    def test_zip_code_invalid(self):
        self.assertIsNone(self.geo_coder.geocode('invalid zip code'))

    def test_zip_code_valid(self):
        location = self.geo_coder.geocode('3512JC')
        self.assertAlmostEqual(location.latitude, 52.0910, 3)
        self.assertAlmostEqual(location.longitude, 5.1211, 3)

    def test_zip_code_lowercase_with_spaces(self):
        location = self.geo_coder.geocode('3512 jc')
        self.assertAlmostEqual(location.latitude, 52.0910, 3)
        self.assertAlmostEqual(location.longitude, 5.1211, 3)


class TestGetLocations(TestGeoCoder):
    def test_zip_codes_none(self):
        self.assertRaises(TypeError, self.geo_coder.get_locations, zip_codes=None)

    def test_zip_codes_valid(self):
        args = {
            'zip_from': '3512JC',
            'zip_to': '3584AA'
        }
        locations = self.geo_coder.get_locations(args)
        self.assertEqual(len(locations), 2)
        self.assertAlmostEqual(locations[0].latitude, 52.0910, 3)
        self.assertAlmostEqual(locations[1].latitude, 52.0781, 3)


class TestGetDrivingDistance(TestGeoCoder):
    def test_locations_none(self):
        self.assertRaises(AttributeError, self.geo_coder.get_driving_distance, origin=None, destination=None)

    def test_locations_valid(self):
        args = {
            'zip_from': '3512JC',
            'zip_to': '3584AA'
        }
        locations = self.geo_coder.get_locations(args)
        self.assertAlmostEqual(self.geo_coder.get_driving_distance(locations[0], locations[1]), 3.0265, 2)


class TestLambdaHandler(TestCase):
    def test_query_none(self):
        response = lambda_handler(None, None)['body']
        self.assertEqual(json.loads(response)['message'],
                         'An error occurred: \'NoneType\' object is not subscriptable')

    def test_missing_query_string_parameters(self):
        response = lambda_handler({}, None)['body']
        self.assertEqual(json.loads(response)['message'],
                         'An error occurred: \'pathParameters\'')

    def test_missing_zip_code(self):
        event = {
            'pathParameters': {
                'zip_from': '3512JC',
            }
        }
        response = lambda_handler(event, None)['body']
        self.assertEqual(json.loads(response)['message'],
                         'An error occurred: \'zip_to\'')

    def test_valid_query(self):
        event = {
            'pathParameters': {
                'zip_from': '3512JC',
                'zip_to': '3584AA'
            }
        }
        response = lambda_handler(event, None)['body']
        self.assertEqual(json.loads(response)['distance'], 3.0265)
