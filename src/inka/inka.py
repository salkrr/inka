import os
import sys
from typing import Tuple, Set

import click
import requests

from . import __version__
from .anki_api import AnkiApi
from .config import Config
from .converter import Converter
from .parser import Parser

FILE_EXTENSIONS = ['.md', '.markdown']
CONFIG_PATH = f'{os.path.dirname(__file__)}/config.ini'

cfg = Config(CONFIG_PATH)


def create_cards_from_file(file_path: str):
    """Get all cards from file and send them to Anki"""
    print(f'Starting to create cards from "{os.path.basename(file_path)}"!')

    # We need to change working directory because images in file can have relative path
    os.chdir(os.path.dirname(file_path))

    note_parser = Parser(file_path)

    print('Getting cards from the file...')
    cards_list = note_parser.collect_cards()

    number_of_cards = len(cards_list)

    print(f'Found {number_of_cards} cards!')

    print('Converting cards to the html...')
    Converter.convert_cards(cards_list)

    print('Sending cards...')
    try:
        AnkiApi.add_cards(cards_list)
    except requests.exceptions.ConnectionError:
        print("Couldn't connect to Anki. Please, check that Anki is running and try again.")
        sys.exit()


def get_file_paths_from_directory(dir_path: str, search_recursive: bool) -> Set[str]:
    os.chdir(dir_path)

    paths_to_files = set()
    sub_directories = []
    for item in os.scandir():
        # Get markdown files
        extension = os.path.splitext(item.name)[1]
        if item.is_file() and extension in FILE_EXTENSIONS:
            paths_to_files.add(os.path.realpath(item.path))
        # And all directories
        elif search_recursive and item.is_dir():
            sub_directories.append(os.path.realpath(item.path))

    # Get all markdown files from each sub directory
    for directory in sub_directories:
        paths_to_files |= get_file_paths_from_directory(directory, search_recursive)
        os.chdir(dir_path)

    return paths_to_files


def get_paths_to_files(paths: Set[str], recursive: bool) -> Set[str]:
    paths_to_files = set()
    initial_directory = os.getcwd()
    for path in paths:
        full_path = os.path.realpath(path)

        if os.path.isdir(full_path):
            paths_to_files |= get_file_paths_from_directory(full_path, recursive)
            os.chdir(initial_directory)
            continue

        paths_to_files.add(full_path)

    return paths_to_files


def check_anki_connection():
    print("Attempting to connect to Anki...")
    if not AnkiApi.check_connection():
        print("Couldn't connect to Anki. "
              "Please, check that Anki is running and AnkiConnect plugin is installed.")
        sys.exit()

    print("Connected")


def list_config_entries(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    for entry in cfg.get_formatted_entries():
        click.echo(entry)
    ctx.exit()


@click.group()
@click.version_option(version=__version__)
def cli():
    # TODO: add docstring
    # TODO: change program name in usage (because used __main__.py when executed as module)
    pass


@cli.command()
@click.option('-l',
              '--list',
              'list_entries',
              is_flag=True,
              callback=list_config_entries,
              is_eager=True,
              help='List all values set in config file, along with their values.')
@click.argument('name',
                required=True)
@click.argument('value',
                required=False)
def config(list_entries, name, value):
    # TODO: add docstring
    try:
        section, key = name.split('.')

        if not value:
            click.echo(cfg.get_entry_value(section, key))
            sys.exit()

        cfg.update_entry_value(section, key, value)
    except (KeyError, ValueError):
        click.echo('Incorrect name of a config entry!')
        click.echo('To get list of all entries use "--list" flag.')
        sys.exit()


@cli.command()
@click.option('-r',
              '--recursive',
              is_flag=True,
              help='Recursive')
@click.argument('paths',
                metavar='PATH...',
                nargs=-1,
                type=click.Path(exists=True),
                required=True)
def collect(recursive: bool, paths: Tuple[str]):
    # TODO: add docstring
    # Check connection with Anki
    check_anki_connection()

    # Get paths to all files
    files = get_paths_to_files(set(paths), recursive)

    # Create and send cards from each file
    initial_directory = os.getcwd()
    for file in files:
        try:
            create_cards_from_file(file)
            os.chdir(initial_directory)
        except (OSError, ValueError) as e:
            print(e)
            print('Skipping file...')
            input('Press Enter to continue...\n')
