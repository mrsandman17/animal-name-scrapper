from AnimalsScrapper import AnimalsScrapper
import json

TARGET_URL = "https://en.wikipedia.org/wiki/List_of_animal_names"

def main():
    scrapper = AnimalsScrapper(TARGET_URL)
    try:
        scrapper.run()
    except Exception as e:
        raise SystemExit(e)
    print (json.dumps(scrapper.get_animals(), indent=2, default=str))

if __name__ == '__main__':
    main()