import os
import sys
from subprocess import call
from typing import Tuple, Set, List

import click
import requests

from . import __version__
from .models import highlighter, converter, img_handler
from .models.anki_api import AnkiApi
from .models.anki_media import AnkiMedia
from .models.config import Config
from .models.notes.basic_note import BasicNote
from .models.notes.cloze_note import ClozeNote
from .models.parser import Parser
from .models.writer import Writer

FILE_EXTENSIONS = ['.md', '.markdown']
CONFIG_PATH = f'{os.path.dirname(__file__)}/config.ini'

CONFIG = Config(CONFIG_PATH)


def get_notes_from_file(file_path: str) -> List[BasicNote]:
    click.echo('Getting cards from the file...')

    # We need to change working directory because images in file can have relative path
    os.chdir(os.path.dirname(file_path))

    default_deck = CONFIG.get_option_value('defaults', 'deck')
    parser = Parser(file_path, default_deck)
    notes = parser.collect_notes()

    return notes


def create_notes_from_file(file_path: str, anki_api: AnkiApi, anki_media: AnkiMedia) -> None:
    """Get all notes from file and send them to Anki"""
    click.echo(f'Starting to collect cards from "{os.path.basename(file_path)}"!')

    notes = get_notes_from_file(file_path)
    notes_num = len(notes)
    if notes_num == 0:
        click.echo(f"Cards weren't found!")
        return
    click.echo(f'Found {notes_num} cards!')

    converter.convert_cloze_deletions_to_anki_format(
        [note for note in notes if isinstance(note, ClozeNote)]
    )
    writer = Writer(file_path, notes)
    writer.update_cloze_notes()

    img_handler.handle_images_in(notes, anki_media)

    click.echo('Converting cards to the html...')
    converter.convert_notes_to_html(notes)

    click.echo('Synchronizing changes...')
    notes_with_id = [note for note in notes
                     if note.anki_id]
    anki_api.update_notes(notes_with_id)

    click.echo('Sending new cards...')
    notes_without_id = [note for note in notes
                        if not note.anki_id]
    anki_api.add_notes(notes_without_id)

    click.echo('Adding IDs to cards...')
    writer.update_note_ids()


def update_note_ids_in_file(file_path: str, anki_api: AnkiApi, anki_media: AnkiMedia):
    """Update IDs of notes in file by getting their IDs from Anki"""
    click.echo(f'Starting to update IDs of cards from "{os.path.basename(file_path)}"!')

    notes = get_notes_from_file(file_path)
    notes_num = len(notes)
    if notes_num == 0:
        click.echo(f"Cards weren't found!")
        return

    click.echo(f'Found {notes_num} cards!')
    converter.convert_cloze_deletions_to_anki_format(
        [note for note in notes if isinstance(note, ClozeNote)]
    )
    writer = Writer(file_path, notes)
    writer.update_cloze_notes()

    img_handler.handle_images_in(notes, anki_media)

    click.echo('Converting cards to the html...')
    converter.convert_notes_to_html(notes)

    click.echo('Getting card IDs from Anki...')
    anki_api.update_note_ids(notes)

    click.echo('Adding IDs to cards...')
    writer.update_note_ids()


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


def get_profile_from_user(profiles: List[str], message: str = None) -> str:
    if message:
        click.echo(message)
    profile = click.prompt('Enter the name of profile you want to use',
                           type=click.Choice(profiles))

    # Ask user to save profile as default
    if click.confirm('Save profile as default?'):
        CONFIG.update_option_value('defaults', 'profile', profile)

    return profile


def get_profile(prompt_user: bool, anki_api: AnkiApi) -> str:
    click.echo('Getting list of profiles from Anki...')
    profiles = anki_api.get_profiles()

    # If user has only one profile
    if len(profiles) == 1:
        return profiles[0]

    # If user used '-p' flag
    if prompt_user:
        return get_profile_from_user(profiles)

    click.echo('Getting profile from config...')
    profile = CONFIG.get_option_value('defaults', 'profile')
    if not profile:
        profile = get_profile_from_user(profiles, 'Default profile is not specified.')
    elif profile not in profiles:
        profile = get_profile_from_user(profiles, f'Incorrect profile name in config: {profile}')

    return profile


def check_anki_connection(anki_api: AnkiApi) -> None:
    click.echo("Attempting to connect to Anki...")
    if not anki_api.check_connection():
        click.secho("Couldn't connect to Anki. "
                    "Please, check that Anki is running and AnkiConnect plugin is installed.", fg='red')
        sys.exit(1)

    click.echo("Connected")


def edit_config_file(ctx, param, value) -> None:
    if not value or ctx.resilient_parsing:
        return

    editor = os.getenv('EDITOR')
    if not editor:
        editor = 'nano'

    with open(CONFIG_PATH, mode='at', encoding='utf-8') as f:
        call([editor, f.name])

    ctx.exit()


def reset_config_file(ctx, param, value) -> None:
    if not value or ctx.resilient_parsing:
        return

    CONFIG.reset()
    ctx.exit()


def list_config_options(ctx, param, value) -> None:
    if not value or ctx.resilient_parsing:
        return

    for entry in CONFIG.get_formatted_options():
        click.echo(entry)
    ctx.exit()


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Inka - command-line tool for adding flashcards from Markdown files to Anki.

        Documentation:\n
            https://github.com/lazy-void/inka/wiki

        Github:\n
            https://github.com/lazy-void/inka
    """
    pass


@cli.command()
@click.option('-l',
              '--list',
              'list_options',
              is_flag=True,
              callback=list_config_options,
              is_eager=True,
              help='List all options set in the config file, along with their values.')
@click.option('-r',
              '--reset',
              is_flag=True,
              callback=reset_config_file,
              is_eager=True,
              help='Reset config file to the default state.')
@click.option('-e',
              '--edit',
              is_flag=True,
              callback=edit_config_file,
              is_eager=True,
              help='Open the config file using editor specified in EDITOR environment variable.')
@click.argument('name',
                required=True)
@click.argument('value',
                required=False)
def config(list_options: bool, reset: bool, edit: bool, name: str, value: str) -> None:
    """Get and set inka's configuration options.

        NAME - config option name. VALUE - new value for config option.

        Examples:\n
            inka config defaults.profile "My Profile"
    """
    try:
        section, key = name.split('.')

        if not value:
            click.echo(CONFIG.get_option_value(section, key))
            sys.exit()

        CONFIG.update_option_value(section, key, value)
    except (KeyError, ValueError):
        click.secho('Incorrect name of a config entry!', fg='red')
        click.echo('To get list of all entries use "--list" flag.')
        sys.exit(1)


@cli.command()
@click.option('-r',
              '--recursive',
              is_flag=True,
              help='Search for files in subdirectories.')
@click.option('-p',
              '--prompt',
              is_flag=True,
              help='Show prompt for profile name even if config contains default profile.')
@click.option('-u',
              '--update-ids',
              'update_ids',
              is_flag=True,
              help='Update incorrect or absent IDs of cards from file(s) by searching for these cards in Anki.')
@click.argument('paths',
                metavar='[PATH]...',
                nargs=-1,
                type=click.Path(exists=True),
                required=False)
def collect(recursive: bool, prompt: bool, update_ids: bool, paths: Tuple[str]) -> None:
    """Get flashcards from files and add them to Anki. If flashcard already exists in Anki, the changes will be synced.

     If no PATH argument is passed, the program will use the path from config option 'defaults.folder'.

        [PATH]... - paths to files and/or directories

        Examples:\n
            inka collect path/to/cards.md - get cards from file\n
            inka collect path/to/folder - get cards from all files in folder
    """
    # If no path specified as an argument, search for default path in config
    paths = set(paths)
    if not paths:
        default_path = os.path.expanduser(CONFIG.get_option_value('defaults', 'folder'))
        if not default_path:
            click.secho('Default folder is not specified in the config!\n'
                        'You must pass the path to a file or folder as an argument.', fg='red')
            sys.exit(1)

        paths.add(default_path)

    anki_api = AnkiApi(CONFIG)

    # Check connection with Anki
    check_anki_connection(anki_api)

    # Get name of profile and select it in Anki
    profile = get_profile(prompt, anki_api)
    anki_api.select_profile(profile)

    anki_media = AnkiMedia(profile)
    try:
        highlighter.add_code_highlight_to(
            BasicNote,
            CONFIG.get_option_value('highlight', 'style'),
            anki_api,
            anki_media
        )
        highlighter.add_code_highlight_to(
            ClozeNote,
            CONFIG.get_option_value('highlight', 'style'),
            anki_api,
            anki_media
        )
    except KeyError:
        # Handle backward compatibility issues (config options were changed)
        click.secho('Your config file is corrupted. Please reset its state with the command "inka config --reset".',
                    fg='red')
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.secho(f'Error while adding code highlight: "{e}"', fg='red')
        sys.exit(1)
    except ConnectionError as e:
        click.secho(str(e), fg='yellow')

    # Get paths to all files
    files = get_paths_to_files(paths, recursive)

    # Perform action on notes from each file
    initial_directory = os.getcwd()
    for file in files:
        try:
            if update_ids:
                update_note_ids_in_file(file, anki_api, anki_media)
            else:
                create_notes_from_file(file, anki_api, anki_media)

            os.chdir(initial_directory)
        except (OSError, ValueError, FileNotFoundError, FileExistsError) as e:
            click.secho(f'Error: "{e}"', fg='red')
            click.secho('Skipping file...', fg='red')
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
            click.secho(f'Error while communicating with Anki: "{e}"', fg='red')
            sys.exit(1)

    click.echo('Finished!')
