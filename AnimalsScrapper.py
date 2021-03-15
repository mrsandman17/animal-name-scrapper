import requests
import time
import logging
import re
from bs4 import BeautifulSoup

REQUEST_RETRIES_NUM = 10
REQUEST_RETRY_WAIT_TIME = 2
LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class AnimalsScrapper:

    def __init__(self, target_url):
        """
        Create an Animal Scrapper object
        :param target_url: Url to scrap from
        """
        self._target_url = target_url
        self._animals_dict = {}
        self._logger = logging.getLogger('scrapper')
        self._logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handler
        formatter = logging.Formatter(LOGGER_FORMAT)
        ch.setFormatter(formatter)
        # add the handler to the logger
        self._logger.addHandler(ch)

    def run(self):
        """
        Request data from the url and parse it into a dict
        :return:
        """
        raw_content = self._get_raw_html_content()
        self._logger.info("Remote data retrieved from URL successfully")
        animals_gen = self._generate_animals(raw_content)
        self._logger.info("Generating animals")
        for name, collateral_adjectives in animals_gen:
            for collateral_adjective in collateral_adjectives:
                if collateral_adjective in self._animals_dict:
                    self._animals_dict[collateral_adjective].append(name)
                else:
                    self._animals_dict[collateral_adjective] = [name]
        self._logger.info("Animals generated successfully")

    def get_animals(self):
        """
        :return: The animals_dict built from the data
        """
        return self._animals_dict

    def _generate_animals(self, raw_content):
        """
        Parses the animals list in the page:
        "https://en.wikipedia.org/wiki/List_of_animal_names"
        sensitive to its format.
        :param raw_content: content as retrieved from requests
        :return: A generator that yields a tuple: (name, collateral_adjectives_list)
        """
        soup = BeautifulSoup(raw_content, 'html.parser')
        # Look at the third table in the page
        table = soup.findAll('table')[2]
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                name = re.findall("^[A-Za-z ]+", cols[0].text)[0].rstrip()
                if name.find("Also see") != -1:
                    name = name[:name.find("Also see")]
                collateral_adjectives = re.findall("([A-Za-z]+)", cols[5].text)
                yield name, collateral_adjectives

    def _get_raw_html_content(self):
        """
        Retrieves content data from the self._target_url
        Handles timeout exception with a retry loop,
        will raise the error received on any other error, bad HTTP status or another network error
        :return: Raw content data from requests retrieved from the url
        """
        try:
            r = requests.get(self._target_url)
            r.raise_for_status()
        except requests.exceptions.TooManyRedirects as e:
            # Bad URL error
            self._logger.error("Bad Url")
            raise e
        except requests.exceptions.Timeout as e:
            # Continue in a retry loop
            for attempt in range(REQUEST_RETRIES_NUM):
                time.sleep(REQUEST_RETRY_WAIT_TIME)
                self._logger.error(f"request timed out, number of tries left: {REQUEST_RETRIES_NUM} - {attempt}")
                try:
                    r = requests.get(self._target_url)
                    r.raise_for_status()
                except:
                    continue
                else:
                    # Attempt succeeded
                    return r.content
            else:
                self._logger.error(f"All attempts timed out")
                raise e
        except requests.exceptions as e:
            # Some other network or bad HTTP response
            self._logger.error("Error requesting HTML")
            raise e
        return r.content
