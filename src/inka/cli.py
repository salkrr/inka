import os
import sys
from subprocess import call
from typing import Set, List, Iterable

import click
import requests
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.traceback import install

from . import __version__
from .exceptions import HighlighterError, AnkiApiError
from .models import highlighter, converter, img_handler
from .models.anki_api import AnkiApi
from .models.anki_media import AnkiMedia
from .models.config import Config
from .models.hasher import Hasher
from .models.notes.basic_note import BasicNote
from .models.notes.cloze_note import ClozeNote
from .models.notes.note import Note
from .models.parser import Parser
from .models.writer import Writer

FILE_EXTENSIONS = [".md", ".markdown"]
CONFIG_PATH = f"{os.path.dirname(__file__)}/config.ini"
HASHES_PATH = f"{os.path.dirname(__file__)}/hashes.json"

CONFIG = Config(CONFIG_PATH)
CONSOLE = Console()

# pretty traceback
install(console=CONSOLE)


def get_notes_from_file(file_path: str) -> List[Note]:
    CONSOLE.print("  [cyan1]->[/cyan1] Getting cards from the file...")
    # We need to change working directory because images in file can have relative path
    os.chdir(os.path.dirname(file_path))

    default_deck = CONFIG.get_option_value("defaults", "deck")
    notes = Parser(file_path, default_deck).collect_notes()
    notes_num = len(notes)
    if notes_num == 0:
        CONSOLE.print("  [cyan1]->[/cyan1] Cards weren't found!")
    else:
        CONSOLE.print(
            f'  [cyan1]->[/cyan1] Found {notes_num} {"cards" if notes_num > 1 else "card"}!'
        )

    return notes


def create_notes_from_file(
    file_path: str,
    full_sync: bool,
    anki_api: AnkiApi,
    anki_media: AnkiMedia,
    hasher: Hasher,
) -> None:
    """Get all notes from file and send them to Anki"""
    CONSOLE.print(
        f'[green]==>[/green] Collecting cards from "{file_path}"!', style="bold"
    )

    CONSOLE.print("  [cyan1]->[/cyan1] Calculating hash...")
    curr_hash = hasher.calculate_hash(file_path)
    if not (full_sync or hasher.has_changed(file_path, curr_hash)):
        CONSOLE.print("  [cyan1]->[/cyan1] The file hasn't changed since last sync!")
        return

    notes = get_notes_from_file(file_path)
    if not notes:
        CONSOLE.print("  [cyan1]->[/cyan1] Updating information on file hash...")
        hasher.update_hash(file_path, curr_hash)
        return

    converter.convert_cloze_deletions_to_anki_format(
        note for note in notes if isinstance(note, ClozeNote)
    )
    writer = Writer(file_path, notes)
    writer.update_cloze_notes()

    CONSOLE.print("  [cyan1]->[/cyan1] Handling images...")
    img_handler.handle_images_in(notes, anki_media)

    CONSOLE.print("  [cyan1]->[/cyan1] Converting cards to the html...")
    converter.convert_notes_to_html(notes)

    CONSOLE.print("  [cyan1]->[/cyan1] Synchronizing changes and adding new cards...")
    for note in notes:
        try:
            if note.anki_id:
                anki_api.update_note(note)
                continue

            note.anki_id = anki_api.add_note(note)
        except AnkiApiError as e:
            print_error(str(e), note=e.note)

    CONSOLE.print("  [cyan1]->[/cyan1] Adding IDs to cards in file...")
    writer.update_note_ids()

    CONSOLE.print("  [cyan1]->[/cyan1] Updating information on file hash...")
    hasher.update_hash(file_path, hasher.calculate_hash(file_path))
    CONSOLE.print("  [cyan1]->[/cyan1] Finished!")


def update_note_ids_in_file(file_path: str, anki_api: AnkiApi, anki_media: AnkiMedia):
    """Update IDs of notes in file by getting their IDs from Anki"""
    CONSOLE.print(
        f'[green]==>[/green] Updating IDs of cards in "{file_path}"!', style="bold"
    )

    notes = get_notes_from_file(file_path)
    if not notes:
        return

    converter.convert_cloze_deletions_to_anki_format(
        [note for note in notes if isinstance(note, ClozeNote)]
    )
    writer = Writer(file_path, notes)
    writer.update_cloze_notes()

    CONSOLE.print("  [cyan1]->[/cyan1] Handling images...")
    img_handler.handle_images_in(notes, anki_media, copy_images=False)

    CONSOLE.print("  [cyan1]->[/cyan1] Converting cards to the html...")
    converter.convert_notes_to_html(notes)

    CONSOLE.print("  [cyan1]->[/cyan1] Getting card IDs from Anki...")
    anki_api.update_note_ids(notes)

    CONSOLE.print("  [cyan1]->[/cyan1] Adding IDs to cards in file...")
    writer.update_note_ids()
    CONSOLE.print("  [cyan1]->[/cyan1] Finished!")


def sync(anki_api: AnkiApi) -> None:
    try:
        anki_api.sync()
    except AnkiApiError as e:
        CONSOLE.print(f"   {e}. Skipping...", style="yellow")


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


def handle_code_highlight(anki_api: AnkiApi, anki_media: AnkiMedia) -> None:
    for note_type in (BasicNote, ClozeNote):
        highlighter.add_code_highlight_to(
            note_type,  # type: ignore
            CONFIG.get_option_value("highlight", "style"),
            anki_api,
            anki_media,
        )


def handle_note_types(anki_api: AnkiApi) -> None:
    note_types = anki_api.fetch_note_types()
    curr_basic_type = CONFIG.get_option_value("anki", "basic_type")
    curr_front_field = CONFIG.get_option_value("anki", "front_field")
    curr_back_field = CONFIG.get_option_value("anki", "back_field")
    curr_cloze_type = CONFIG.get_option_value("anki", "cloze_type")
    curr_cloze_field = CONFIG.get_option_value("anki", "cloze_field")
    css = """.card {
  font-family: arial;
  font-size: 20px;
  text-align: left;
  color: black;
  background-color: white;
  line-height: 1.5em;
}

.cloze {
  font-weight: bold;
  color: blue;
}
.nightMode .cloze {
  color: lightblue;
}

code {
  background-color: #232831;
  color: #fa4545;
  border: 1px solid #030a1420;
  box-shadow: 0 0.1em #00000010;
  padding: 1px 2px;
  line-height: 1.4em;
  box-sizing: border-box;
  font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
}
"""

    # Basic Note
    if (
        not (curr_basic_type and curr_front_field and curr_back_field)
        or curr_basic_type not in note_types
    ):
        basic_name = "Inka Basic"
        front_field = "Front"
        back_field = "Back"
        if basic_name not in note_types:
            anki_api.create_note_type(
                name=basic_name,
                fields=[front_field, back_field],
                css=css,
                card_templates=[
                    {
                        "Name": "Card 1",
                        "Front": "{{" + f"{front_field}" + "}}\n",
                        "Back": "{{FrontSide}}\n<hr id=answer>\n"
                        + "{{"
                        + f"{back_field}"
                        + "}}\n",
                    }
                ],
                is_cloze=False,
            )
        CONFIG.update_option_value("anki", "basic_type", basic_name)
        CONFIG.update_option_value("anki", "front_field", front_field)
        CONFIG.update_option_value("anki", "back_field", back_field)

    # Cloze Note
    if not (curr_cloze_type and curr_cloze_field) or curr_cloze_type not in note_types:
        cloze_name = "Inka Cloze"
        text_field = "Text"
        if cloze_name not in note_types:
            anki_api.create_note_type(
                name=cloze_name,
                fields=[text_field],
                css=css,
                card_templates=[
                    {
                        "Name": "Cloze",
                        "Front": "{{" + f"cloze:{text_field}" + "}}\n",
                        "Back": "{{" + f"cloze:{text_field}" + "}}\n",
                    }
                ],
                is_cloze=True,
            )
        CONFIG.update_option_value("anki", "cloze_type", cloze_name)
        CONFIG.update_option_value("anki", "cloze_field", text_field)


def get_profile_from_user(profiles: List[str]) -> str:
    profile = Prompt.ask(
        "   Enter the name of profile you want to use", choices=profiles
    )

    if Confirm.ask("   Save profile as default?"):
        CONFIG.update_option_value("defaults", "profile", profile)

    return profile


def get_profile(prompt_user: bool, anki_api: AnkiApi) -> str:
    profiles = anki_api.get_profiles()

    if len(profiles) == 1:
        return profiles[0]

    if prompt_user:
        return get_profile_from_user(profiles)

    profile = CONFIG.get_option_value("defaults", "profile")
    if not profile:
        CONSOLE.print("   Default profile is not specified!", style="yellow")
        profile = get_profile_from_user(profiles)
    elif profile not in profiles:
        CONSOLE.print(
            f'   Incorrect profile name in the config: "{profile}"!', style="red"
        )
        profile = get_profile_from_user(profiles)

    return profile


def print_error(message: str, pause: bool = False, note: Note = None) -> None:
    if note:
        CONSOLE.print(note)
    CONSOLE.print(f"ERROR: {message}", style="red bold")

    if pause:
        CONSOLE.input("Press [italic]Enter[/italic] to continue...\n")


def print_warning(message: str) -> None:
    CONSOLE.print(f"WARNING: {message}", style="yellow bold")


def edit_config_file(ctx, param, value) -> None:
    if not value or ctx.resilient_parsing:
        return

    editor = os.getenv("EDITOR")
    if not editor:
        editor = "nano"

    with open(CONFIG_PATH, mode="at", encoding="utf-8") as f:
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

    CONSOLE.print(CONFIG)
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
@click.option(
    "-l",
    "--list",
    "list_options",
    is_flag=True,
    callback=list_config_options,
    is_eager=True,
    help="List all options set in the config file, along with their values.",
)
@click.option(
    "-r",
    "--reset",
    is_flag=True,
    callback=reset_config_file,
    is_eager=True,
    help="Reset config file to the default state.",
)
@click.option(
    "-e",
    "--edit",
    is_flag=True,
    callback=edit_config_file,
    is_eager=True,
    help="Open the config file using editor specified in EDITOR environment variable.",
)
@click.argument("name", required=True)
@click.argument("value", required=False)
def config(list_options: bool, reset: bool, edit: bool, name: str, value: str) -> None:
    """Get and set inka's configuration options.

    NAME - name of the config option. VALUE - new value for the config option.

    Examples:\n
        Get the current value of "defaults.profile" option:\n
            inka config defaults.profile

        Set a new value to the "defaults.profile" option:\n
            inka config defaults.profile "My Profile"
    """
    try:
        section, key = name.split(".")

        if not value:
            CONSOLE.print(CONFIG.get_option_value(section, key), style="green")
            sys.exit(0)

        CONFIG.update_option_value(section, key, value)
    except (KeyError, ValueError):
        print_error(
            "incorrect name of a config option!\n"
            'To get list of all options use "--list" flag.'
        )
        sys.exit(1)


@cli.command()
@click.option(
    "-r", "--recursive", is_flag=True, help="Search for files in subdirectories."
)
@click.option(
    "-p",
    "--prompt",
    is_flag=True,
    help="Show prompt for profile name even if config contains default profile.",
)
@click.option(
    "-u",
    "--update-ids",
    "update_ids",
    is_flag=True,
    help="Update incorrect or absent IDs of cards from file(s) by searching for these cards in Anki.",
)
@click.option(
    "-i",
    "--ignore-errors",
    "ignore_errors",
    is_flag=True,
    help="The program won't pause in case of an error.",
)
@click.option(
    "-f",
    "--full-sync",
    "full_sync",
    is_flag=True,
    help="Collect cards from the file, even if the file hasn't changed since the last sync.",
)
@click.argument(
    "paths", metavar="[PATH]...", nargs=-1, type=click.Path(exists=True), required=False
)
def collect(
    recursive: bool,
    prompt: bool,
    update_ids: bool,
    ignore_errors: bool,
    full_sync: bool,
    paths: Iterable[str],
) -> None:
    """Get flashcards from files and add them to Anki. If flashcard already exists in Anki, the changes will be synced.

    If no PATH argument is passed, the program will use the path from config option 'defaults.folder'.

       [PATH]... - paths to files and/or directories

       Examples:\n
           Get cards from file:\n
               inka collect path/to/cards.md

           Get cards from all Markdown files in the directory:\n
               inka collect path/to/directory
    """
    # If no path specified as an argument, search for default path in config
    paths = set(paths)
    if not paths:
        default_path = os.path.expanduser(CONFIG.get_option_value("defaults", "folder"))
        if not default_path:
            print_error(
                "default folder is not specified in the config!\n"
                "You must pass the path to a file or a folder as an argument."
            )
            sys.exit(1)

        if not os.path.exists(default_path):
            print_error(f'default folder "{default_path}" does not exist!')
            sys.exit(1)

        paths.add(default_path)

    anki_api = AnkiApi(CONFIG)

    # Get name of profile and select it in Anki
    CONSOLE.print("[cyan1]::[/cyan1] Getting profile...", style="bold")
    profile = get_profile(prompt, anki_api)

    CONSOLE.print("[cyan1]::[/cyan1] Loading profile...", style="bold")
    try:
        anki_api.load_collection(profile)
    except AnkiApiError as e:
        print_error(str(e), pause=False)
        sys.exit(1)

    CONSOLE.print("[cyan1]::[/cyan1] Getting changes from AnkiWeb...", style="bold")
    sync(anki_api)

    CONSOLE.print("[cyan1]::[/cyan1] Checking note types...", style="bold")
    anki_media = AnkiMedia(profile)
    try:
        handle_note_types(anki_api)
        handle_code_highlight(anki_api, anki_media)
    except KeyError:
        print_error(
            'your config file is corrupted. Please reset its state with the command "inka config --reset".'
        )
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print_error(f'something gone wrong while handling code highlight: "{e}"')
        sys.exit(1)
    except HighlighterError as e:
        print_warning(str(e))

    # Get paths to all files
    # todo: add message
    files = get_paths_to_files(paths, recursive)

    if not files:
        CONSOLE.print(
            "[cyan1]::[/cyan1] Markdown files not found!", style="yellow bold"
        )
        sys.exit(0)

    # Perform action on notes from each file
    hasher = Hasher(HASHES_PATH)
    initial_directory = os.getcwd()
    for file in files:
        try:
            if update_ids:
                update_note_ids_in_file(file, anki_api, anki_media)
                continue

            create_notes_from_file(file, full_sync, anki_api, anki_media, hasher)
        except (
            OSError,
            ValueError,
            FileNotFoundError,
            FileExistsError,
        ) as e:
            print_error(f"{e}\nSkipping file!", pause=(not ignore_errors))
        except AnkiApiError as e:
            print_error(f"{e}\nSkipping file!", pause=(not ignore_errors), note=e.note)
        finally:
            os.chdir(initial_directory)

    CONSOLE.print("[cyan1]::[/cyan1] Synchronizing changes to AnkiWeb...", style="bold")
    sync(anki_api)

    anki_api.close()
    CONSOLE.print("[cyan1]::[/cyan1] Everything is done!", style="bold")
