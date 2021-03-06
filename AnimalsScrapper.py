import requests
import shutil
import logging
import re
import concurrent.futures
from bs4 import BeautifulSoup
import os.path

REQUEST_RETRIES_NUM = 10
REQUEST_RETRY_WAIT_TIME = 2
NUM_OF_IMAGE_DOWNLOAD_THREADS = 12

LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class AnimalsScrapper:

    def __init__(self, target_url, download_pics=False, download_path=''):
        """
        Create an Animal Scrapper object
        :param target_url: Url to scrap from
        """
        self._target_url = target_url
        self._animals_dict = {}
        self._animals_synonyms = {}
        self._download_pics = download_pics
        self._download_path = download_path
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
        self._logger.info(f"Scrapper initialized, download pics set to {self._download_pics}")

    def run(self):
        """
        Request data from the url and parse it into a dict
        :return:
        """
        raw_content = self._get_raw_html_content(self._target_url)
        self._logger.info("Remote data retrieved from URL successfully")
        animals_gen = self._generate_animals(raw_content)
        self._logger.info("Generating animals")
        animal_name_objs_dict = {}
        for name, collateral_adjectives, synonym, animal_name_obj in animals_gen:
            if synonym:
                # Add the name to the synonyms list
                self._animals_synonyms[name] = synonym
            for collateral_adjective in collateral_adjectives:
                if collateral_adjective in self._animals_dict:
                    self._animals_dict[collateral_adjective].append(name)
                else:
                    self._animals_dict[collateral_adjective] = [name]
            if self._download_pics:
                # Save the name_obj
                animal_name_objs_dict [name] = animal_name_obj
                for collateral_adjective in collateral_adjectives:
                    # Save the local links to the images to be downloaded
                    lcl_image_path = os.path.join(self._download_path, f'{name}.png')
                    tagged_image = f'<img src="{lcl_image_path}" alt="{name}">'
                    self._animals_dict[collateral_adjective].append(tagged_image)

        self._logger.info("Animals generated successfully")
        if self._download_pics:
            self._logger.info("Downloading animal pics")
            self._download_images(animal_name_objs_dict)

    def _download_images(self, animal_names_obj_dict, threads_num = NUM_OF_IMAGE_DOWNLOAD_THREADS):
        """
        Downloads the images for the animals names concurrently
        :param animal_names_obj_dict: a dict in the format: {name:name_obj}, (name_obj is beautiful_soup obj)
        :param threads_num: num of threads to run
        :return:
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads_num) as executor:
            futures = []
            for name, name_obj in animal_names_obj_dict.items():
                futures.append((executor.submit(self._download_image, name, name_obj)))

    def _download_image(self, name, name_obj):
        """
        Downloads an image of the animal by following its link from the name_obj
        :param name: The animal name
        :param name_obj: The beautiful_soup object of the animal name
        :return:
        """
        # Go to the animal page and find its picture from the info box
        link = self._get_animal_pic_download_link(name_obj)
        # link is empty if no picture could be found in this method
        if link == '':
            return
        try:
            response = requests.get(link, stream=True)
            self._logger.debug(f"Downloading image for {name}")
        except requests.exceptions.RequestException:
            self._logger.error(f"Error downloading image for {name}")
            return
        with open(os.path.join(self._download_path, f'{name}.png'), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def _get_animal_pic_download_link(self, animal_name):
        """
        Returns the image download link for a animal soup element from the table
        Goes to the animal page and find its picture from the info box
        :param animal_name: Animal to retrieve the pic for
        :return:
        """
        # Get the link to the animal's page
        self._logger.debug(f"Getting image download link for {animal_name}")
        link = animal_name.find_all('a', href=True)[0]['href']
        animal_page_link = f'https://en.wikipedia.org{link}'
        # Go to the animal page
        content = self._get_raw_html_content(animal_page_link)
        soup = BeautifulSoup(content, 'html.parser')
        # go to the infobox
        infobox = soup.find_all('table', {'class':['infobox biota', 'infobox biota biota-infobox']})
        if not infobox:
            self._logger.warning(f"Couldn't find info box for {animal_name}")
            return ""
        # Go for the image in the infobox
        image = infobox[0].find_all('img', src=True)
        if not image:
            self._logger.warning(f"Couldn't find info box image for {animal_name}")
            return ""
        return f'http:{image[0]["src"]}'

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
        :return: A generator that yields a tuple: (name, collateral_adjectives_list, animal_synonym, animal_name_obj)
        """
        image_download_link = ""
        soup = BeautifulSoup(raw_content, 'html.parser')
        # Look at the third table in the page
        table = soup.findAll('table')[2]
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) != 0:
                animal_name_obj = cols[0]
                animal_adj_obj = cols[5]
                name = animal_name_obj.get_text()
                name, synonym = self._parse_animal_name(name)
                # Read all adjective line by line
                collateral_adjectives = animal_adj_obj.get_text(strip=True, separator="\n").split("\n")
                # Clean and remove unneeded chars
                collateral_adjectives = [adj for adj in collateral_adjectives if re.match('^[A-Za-z?]+$', adj)]
                yield name, collateral_adjectives, synonym, animal_name_obj

    def _parse_animal_name(self, name):
        """
        Parses an animal name, handles 2 edge cases:
        "Also See" - in it's different formats,
        "See" - a reference to another animal name(synonym)
        :param name: the raw name of the animal as parse from beautiful_soup
        :return: a tuple (name, synonym), synonym may be an empty string
        """
        synonym = ""
        # Perform checks for the case of a reference to another Animal
        # For case 1
        other_animal_ref_str_index = name.find("Also see")
        # For case 2
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
        return name, synonym

    def _get_raw_html_content(self, target_url):
        """
        Retrieves content data from the self._target_url
        Handles timeout exception with a retry loop,
        will raise the error received on any other error, bad HTTP status or another network error
        :return: Raw content data from requests retrieved from the url
        """
        try:
            r = requests.get(target_url)
            r.raise_for_status()
        except requests.exceptions.TooManyRedirects as e:
            # Bad URL error
            self._logger.error("Bad Url")
            raise e
        except requests.exceptions.RequestException as e:
            # Some other network or bad HTTP response
            self._logger.error("Error requesting HTML")
            raise e
        return r.content
