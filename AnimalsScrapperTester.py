import unittest
from AnimalsScrapper import AnimalsScrapper
import requests
from  json2html import *

BAD_URL_HTTP_ERROR_404 = 'http://www.google.com/notthere'
BAD_URL_TIMEOUT = 'http://www.google.com:81'
GOOD_URL = 'https://en.wikipedia.org/wiki/List_of_animal_names'

EXPECTED_RESULT_TEST_FILE = "expected_result_test_file.html"


class TestAnimalsScrapper(unittest.TestCase):

    def test_http_error(self):
        scrapper = AnimalsScrapper(BAD_URL_HTTP_ERROR_404)
        self.assertRaises(requests.exceptions.HTTPError,  scrapper.run)

    def test_timeout_error(self):
        scrapper = AnimalsScrapper(BAD_URL_TIMEOUT)
        self.assertRaises(requests.exceptions.ConnectionError,  scrapper.run)

    def test_end_to_end(self):
        """
        Verifies that the parsed result is as expected
        tests the whole pipeline (incl. the requests)
        """
        with open(EXPECTED_RESULT_TEST_FILE, "r") as f:
            expected_dict = f.read()
        scrapper = AnimalsScrapper(GOOD_URL)
        scrapper.run()
        assert json2html.convert(scrapper.get_animals()) == expected_dict

if __name__ == "__main__":
    unittest.main()