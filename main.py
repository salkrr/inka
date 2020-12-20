from classes.Parser import Parser
from classes.Converter import Converter


def main():
    parser = Parser("test_data/test_0.md")
    cards_list = parser.collect_cards()
    if cards_list is None:
        return

    if len(cards_list) == 0:
        print("ERROR: Cards wasn't found in file.")

    for card in cards_list:
        Converter.convert_card(card)
        print("------------------------------------")
        print(f"Front: {card.front}")
        print(f"Back: {card.back}")
        print(f"Tags: {str(card.tags)}")


if __name__ == "__main__":
    main()
