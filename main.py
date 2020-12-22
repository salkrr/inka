import argparse
import os
import sys

from classes.AnkiApi import AnkiApi
from classes.Converter import Converter
from classes.Parser import Parser


def init_argparse():
    arg_parser = argparse.ArgumentParser(
        prog="ankify",
        usage="%(prog)s [FILE]...",
        description="Extract Anki cards from your Markdown notes."
    )

    arg_parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        type=str,
        help="the path to the file")

    return arg_parser


def create_cards(file_path):
    print(f"Starting to create cards from \"{file_path}\"!")
    note_parser = Parser(file_path)

    print("Getting cards from the file...")
    cards_list = note_parser.collect_cards()

    # Error
    if cards_list is None:
        print(f"Cards from the file \"{file_path}\" weren't added to Anki!")
        return

    number_of_cards = len(cards_list)
    if number_of_cards == 0:
        print("ERROR: Cards weren't found in the file.\n")
        return

    print(f"Found {number_of_cards} cards!")

    print("Converting cards to the html...")
    Converter.convert_cards(cards_list)

    print("Sending cards...")
    AnkiApi.add_cards(cards_list)


def main():
    arg_parser = init_argparse()
    args = arg_parser.parse_args()

    for file in args.files:
        if not os.path.isfile(file):
            print(f"The file specified doesn't exist: \"{file}\"")
            sys.exit()

    for file in args.files:
        create_cards(file)


if __name__ == "__main__":
    main()
