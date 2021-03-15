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
        self._animals_synonyms = []
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
        for name, collateral_adjectives, synonym in animals_gen:
            if synonym:
                # Add the name to the synonyms list
                self._animals_synonyms.append((name, synonym))
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

    def get_synonyms(self):
        return self._animals_synonyms

    def _generate_animals(self, raw_content):
        """
        Parses the animals list in the page:
        "https://en.wikipedia.org/wiki/List_of_animal_names"
        sensitive to its format.
        :param raw_content: content as retrieved from requests
        :return: A generator that yields a tuple: (name, collateral_adjectives_list, name_ref)
        """

        soup = BeautifulSoup(raw_content, 'html.parser')
        # Look at the third table in the page
        table = soup.findAll('table')[2]
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                synonym = ""
                name = cols[0].get_text()
                # Perform checks for the case of a reference to another Animal
                other_animal_ref_str_index = name.find("Also see")
                synonym_match_lst = re.match("([A-Za-z ]+)([(A-Za-z)]*)-* See ([A-Za-z ]+)", name)
                if other_animal_ref_str_index != -1:
                    # Case 1: "Also See" - the animal is appended by "Also See" without whitespace, remove it
                    name = name[:other_animal_ref_str_index]
                if synonym_match_lst:
                    # Case 2: "See" - Add a synonym for this animal
                    name = synonym_match_lst.group(1)
                    synonym = synonym_match_lst.group(3)
                else:
                    names_list = re.findall("^[A-Za-z ]+", name)
                    name = names_list[0].rstrip()
                # The adjectives are all which are strings in the column
                # collateral_adjectives = [content for content in cols[5].contents if isinstance(content, str)]
                collateral_adjectives = cols[5].get_text(strip=True, separator="\n").split("\n")
                yield name, collateral_adjectives, synonym

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
