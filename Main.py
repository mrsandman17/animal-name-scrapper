from AnimalsScrapper import AnimalsScrapper
from json2html import *
import json
import traceback
import argparse

TARGET_URL = "https://en.wikipedia.org/wiki/List_of_animal_names"
OUTPUT_HTML_FILE_NAME = "animals_by_collateral_adjectives.html"
DEFAULT_DOWNLOAD_PATH = r'/tmp'
DEBUG = True

def main():
    """

    :return:
    """
    # Set up a parser with 2 optional arguments
    parser = argparse.ArgumentParser(description='Scrapping Animal names from wikipedia')
    parser.add_argument('--d', default=False, action='store_true', help='Download animals images')
    parser.add_argument('--path', default=DEFAULT_DOWNLOAD_PATH, type=str, help='Images download path')
    args = parser.parse_args()
    # init the scrapper
    scrapper = AnimalsScrapper(TARGET_URL, download_pics=args.d, download_path=args.path)
    try:
        scrapper.run()
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        raise SystemExit(e)
    # Print the data as json (more pretty)
    print (json.dumps(scrapper.get_animals(), indent=2, default=str))
    print(json.dumps(scrapper.get_synonyms(), indent=2, default=str))
    write_to_html(scrapper.get_animals())

def write_to_html(animals_dict):
    """
    :param animals_dict: Writes the dict to html
    :return:
    """
    html_data = json2html.convert(animals_dict)
    with open(OUTPUT_HTML_FILE_NAME, "w") as f:
        f.write(unescape(html_data))

def unescape(s):
    """
    :param s: string to restore escaped chars to the originals
    :return: the string with no escaped chars
    """
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", '"')
    # this has to be last:
    s.replace("&amp;", "&")
    return s

if __name__ == '__main__':
    main()