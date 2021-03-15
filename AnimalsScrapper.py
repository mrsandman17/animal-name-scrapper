import requests
import time
import logging
from bs4 import BeautifulSoup

REQUEST_RETRIES_NUM = 10
REQUEST_RETRY_WAIT_TIME = 2
LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class AnimalsScrapper:

    def __init__(self, target_url):
        self._target_url = target_url
        self._animals_dict = {}
        self._logger = logging.getLogger('scrapper')
        self._logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(LOGGER_FORMAT)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(ch)

    def run(self):
        raw_content = self._get_raw_html_content()
        self._logger.info("Remote data retrieved from URL successfully")
        soup = BeautifulSoup(raw_content, 'html.parser')
        animals_gen = self._generate_animals(soup)
        self._logger.info("Generating animals")
        for name, collateral_adjective in animals_gen:
            if collateral_adjective in self._animals_dict:
                self._animals_dict[collateral_adjective].append(name)
            else:
                self._animals_dict[collateral_adjective] = [name]

    def get_animals(self):
        return self._animals_dict

    def _generate_animals(self, soup):
        table = soup.findAll('table')[2]
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                name = cols[0].text
                collateral_adjective = cols[5].text
                yield name, collateral_adjective

    def _get_raw_html_content(self):
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
