import argparse
import os
import sys
from typing import List

import requests

from .anki_api import AnkiApi
from .converter import Converter
from .parser import Parser


def init_argparse() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        prog="inka",
        usage="%(prog)s [OPTION]... PATH...",
        description="Extract Anki cards from your Markdown notes."
    )

    arg_parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        type=str,
        help="path to file or directory"
    )

    arg_parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='search files in subdirectories of specified directories'
    )

    return arg_parser


def create_cards(file_path: str):
    """Get all cards from file and send them to Anki"""
    print(f"Starting to create cards from \"{file_path}\"!")

    abs_file_path = os.path.realpath(file_path)

    # We need to change working directory because images in file can have relative path
    os.chdir(os.path.dirname(abs_file_path))

    note_parser = Parser(abs_file_path)

    print("Getting cards from the file...")
    cards_list = note_parser.collect_cards()

    number_of_cards = len(cards_list)

    print(f"Found {number_of_cards} cards!")

    print("Converting cards to the html...")
    Converter.convert_cards(cards_list)

    print("Sending cards...")
    try:
        AnkiApi.add_cards(cards_list)
    except requests.exceptions.ConnectionError:
        print("ERROR: Couldn't connect to Anki. "
              "Please, check that Anki is working and you have AnkiConnect plugin is installed.")
        sys.exit()


def get_files_from_directory(dir_path: str, search_recursive: bool) -> List[str]:
    os.chdir(dir_path)

    paths_to_files = []
    sub_directories = []
    for item in os.scandir():
        # Get files with extension '.md'
        if item.is_file() and item.name.endswith('.md'):
            paths_to_files.append(os.path.realpath(item.path))
        # And all directories
        elif search_recursive and item.is_dir():
            sub_directories.append(os.path.realpath(item.path))

    # Get all '.md' files from each sub directory
    for directory in sub_directories:
        paths_to_files.extend(get_files_from_directory(directory, search_recursive))
        os.chdir(dir_path)

    return paths_to_files


def main():
    # Get command-line args
    arg_parser = init_argparse()
    args = arg_parser.parse_args()

    # Check that all paths are correct
    for path in args.paths:
        if not os.path.exists(path):
            print(f"Path '{path}' doesn't exist.")
            sys.exit()

    # Create and send cards from each file
    initial_directory = os.getcwd()
    files = []
    for path in args.paths:
        if os.path.isdir(path):
            full_path = os.path.realpath(path)
            files.extend(get_files_from_directory(full_path, args.recursive))
            continue

        files.append(path)

    for file in files:
        try:
            create_cards(file)
            os.chdir(initial_directory)
        except (OSError, ValueError) as e:
            print(e)
            print('Skipping file...')
            input('Press Enter to continue...\n')
