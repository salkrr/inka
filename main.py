from classes.Parser import Parser


def main():
    parser = Parser("test_data/test_1.md")
    cards_list = parser.collect_cards()
    for card in cards_list:
        print("------------------------------------")
        print(f"Forward: {card.forward}")
        print(f"Backward: {card.backward}")
        print(f"Source: {card.source}")
        print(f"Tags: {str(card.tags)}")


if __name__ == "__main__":
    main()
