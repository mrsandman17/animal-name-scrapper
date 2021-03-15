from AnimalsScrapper import AnimalsScrapper
import json
import traceback
TARGET_URL = "https://en.wikipedia.org/wiki/List_of_animal_names"
DEBUG = True
def main():
    scrapper = AnimalsScrapper(TARGET_URL)
    try:
        scrapper.run()
    except Exception as e:
        if DEBUG:
            traceback.print_exc()
        raise SystemExit(e)
    print (json.dumps(scrapper.get_animals(), indent=2, default=str))
    print(json.dumps(scrapper.get_synonyms(), indent=2, default=str))

if __name__ == '__main__':
    main()