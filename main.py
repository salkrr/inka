from classes.AnkiApi import AnkiApi
from classes.Converter import Converter
from classes.Parser import Parser


def main():
    parser = Parser("test_data/test_1.md")
    cards_list = parser.collect_cards()

    if cards_list is None:
        return

    if len(cards_list) == 0:
        print("ERROR: Cards wasn't found in file.")
        return

    for card in cards_list:
        Converter.convert_card(card)

    AnkiApi.add_cards(cards_list)


if __name__ == "__main__":
    main()
