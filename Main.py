from AnimalsScrapper import AnimalsScrapper
from json2html import *
import json
import traceback

TARGET_URL = "https://en.wikipedia.org/wiki/List_of_animal_names"
OUTPUT_HTML_FILE_NAME = "animals_by_collateral_adjectives.html"

DEBUG = True

def main():
    download_path = r'tmp'
    scrapper = AnimalsScrapper(TARGET_URL, download_pics=True, download_path=download_path)
    try:
        scrapper.run()
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        raise SystemExit(e)
    print (json.dumps(scrapper.get_animals(), indent=2, default=str))
    print(json.dumps(scrapper.get_synonyms(), indent=2, default=str))
    write_to_html(scrapper.get_animals())

def write_to_html(animals_dict):
    html_data = json2html.convert(animals_dict)
    with open(OUTPUT_HTML_FILE_NAME, "w") as f:
        f.write(html_data)

if __name__ == '__main__':
    main()