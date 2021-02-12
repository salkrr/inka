import os
import sys
from typing import Tuple, Set, List

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
anki_api = AnkiApi(cfg.get_option_value('anki_connect', 'port'),
                   cfg.get_option_value('anki', 'note_type'),
                   cfg.get_option_value('anki', 'front_field'),
                   cfg.get_option_value('anki', 'back_field'))


def create_cards_from_file(file_path: str, profile: str):
    """Get all cards from file and send them to Anki"""
    print(f'Starting to create cards from "{os.path.basename(file_path)}"!')

    # We need to change working directory because images in file can have relative path
    os.chdir(os.path.dirname(file_path))

    default_deck = cfg.get_option_value('defaults', 'deck')
    note_parser = Parser(file_path, default_deck, profile)

    print('Getting cards from the file...')
    cards_list = note_parser.collect_cards()

    number_of_cards = len(cards_list)
    print(f'Found {number_of_cards} cards!')

    print('Converting cards to the html...')
    Converter.convert_cards(cards_list)

    print('Sending cards...')
    try:
        anki_api.add_cards(cards_list)
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


def get_profile_from_user(profiles: List[str], message: str = None):
    if message:
        click.echo(message)
    profile = click.prompt('Enter the name of profile you want to use',
                           type=click.Choice(profiles))

    # Ask user to save profile as default
    if click.confirm('Save profile as default?'):
        cfg.update_option_value('defaults', 'profile', profile)

    return profile


def get_profile(prompt_user: bool) -> str:
    click.echo('Getting list of profiles from Anki...')
    profiles = anki_api.get_profiles()

    # If user has only one profile
    if len(profiles) == 1:
        return profiles[0]

    # If user used '-p' flag
    if prompt_user:
        return get_profile_from_user(profiles)

    click.echo('Getting profile from config...')
    profile = cfg.get_option_value('defaults', 'profile')
    if not profile:
        profile = get_profile_from_user(profiles, 'Default profile is not specified.')
    elif profile not in profiles:
        profile = get_profile_from_user(profiles, f'Incorrect profile name in config: {profile}')

    return profile


def check_anki_connection():
    print("Attempting to connect to Anki...")
    if not anki_api.check_connection():
        print("Couldn't connect to Anki. "
              "Please, check that Anki is running and AnkiConnect plugin is installed.")
        sys.exit()

    print("Connected")


def reset_config_file(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    cfg.reset()
    ctx.exit()


def list_config_options(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    for entry in cfg.get_formatted_options():
        click.echo(entry)
    ctx.exit()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Inka - command-line tool for adding Markdown cards to Anki"""
    pass


@cli.command()
@click.option('-l',
              '--list',
              'list_options',
              is_flag=True,
              callback=list_config_options,
              is_eager=True,
              help='List all options set in config file, along with their values.')
@click.option('-r',
              '--reset',
              is_flag=True,
              callback=reset_config_file,
              is_eager=True,
              help='Reset config file to default state.')
@click.argument('name',
                required=True)
@click.argument('value',
                required=False)
def config(list_options, reset, name, value):
    """Get and set inka's configuration options.

        NAME - config option name. VALUE - new value for config option.

        Examples:\n
            inka config defaults.profile "My Profile"
    """
    try:
        section, key = name.split('.')

        if not value:
            click.echo(cfg.get_option_value(section, key))
            sys.exit()

        cfg.update_option_value(section, key, value)
    except (KeyError, ValueError):
        click.echo('Incorrect name of a config entry!')
        click.echo('To get list of all entries use "--list" flag.')
        sys.exit()


@cli.command()
@click.option('-r',
              '--recursive',
              is_flag=True,
              help='Search for files in subdirectories.')
@click.option('-p',
              '--prompt',
              is_flag=True,
              help='Show prompt for profile name even if config contains default profile.')
@click.argument('paths',
                metavar='[PATH]...',
                nargs=-1,
                type=click.Path(exists=True),
                required=False)
def collect(recursive: bool, prompt: bool, paths: Tuple[str]):
    """Get cards from files and send them to Anki.
     If no PATH argument is passed, the program will use the path from config option 'defaults.folder'.

        [PATH]... - paths to files and/or directories

        Examples:\n
            inka collect path/to/cards.md - get cards from file\n
            inka collect path/to/folder - get cards from all files in folder
    """
    # If no path specified as an argument, search for default path in config
    paths = set(paths)
    if not paths:
        default_path = os.path.expanduser(cfg.get_option_value('defaults', 'folder'))
        if not default_path:
            click.echo('Default folder is not specified in the config!')
            click.echo('You must pass the path to a file or folder as an argument.')
            click.echo("Try 'inka collect --help' for more info.")
            sys.exit()

        paths.add(default_path)

    # Check connection with Anki
    check_anki_connection()

    # Get name of profile and select it in Anki
    profile = get_profile(prompt)
    anki_api.select_profile(profile)

    # Get paths to all files
    files = get_paths_to_files(paths, recursive)

    # Create and send cards from each file
    initial_directory = os.getcwd()
    for file in files:
        try:
            create_cards_from_file(file, profile)
            os.chdir(initial_directory)
        except (OSError, ValueError) as e:
            print(e)
            print('Skipping file...')
            input('Press Enter to continue...\n')
