from classes.AnkiApi import AnkiApi
from classes.Converter import Converter
from classes.Parser import Parser


def main():
    parser = Parser("test_data/test_1.md")

    print("Getting cards from the file...")
    cards_list = parser.collect_cards()

    # Error
    if cards_list is None:
        return

    number_of_cards = len(cards_list)
    if number_of_cards == 0:
        print("ERROR: Cards weren't found in file.")
        return

    print(f"Found {number_of_cards} cards!")

    print("Converting cards to the html...")
    Converter.convert_cards(cards_list)

    print("Sending cards...")
    AnkiApi.add_cards(cards_list)


if __name__ == "__main__":
    main()
