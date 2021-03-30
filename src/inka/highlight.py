import re

import requests

from .anki_api import AnkiApi
from .anki_media import AnkiMedia

HLJS_VERSION = "10.7.1"
BASE_URL = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HLJS_VERSION}"


def add_code_highlight_to_note_type(style_name: str, anki_api: AnkiApi, anki_media: AnkiMedia) -> None:
    # Handle style
    # Handle highlight.js
    pass


def update_style_in_note_type(style_name: str, anki_api: AnkiApi) -> None:
    """Adds highlight.js style to the note type

    Raises:
        ValueError: style_name is empty string or None
        HTTPError: something gone wrong during process of downloading style
    """
    if not style_name:
        raise ValueError("highlight style value in config must not be empty")

    current_styles = anki_api.fetch_note_type_styling()

    # Get current highlight.js style name and version
    start_regex = re.compile(r"/\*STYLE:(.+?) VERSION:(.+?)\*/")
    match = re.search(start_regex, current_styles)
    if match:
        current_highlight_style = match.group(1)
        version = match.group(2)
        if current_highlight_style == style_name and version == HLJS_VERSION:
            return

    # Download style from CDN (raise error if can't)
    url = f"{BASE_URL}/styles/{style_name}.min.css"
    response = requests.get(url)
    response.raise_for_status()
    new_highlight_style = response.text

    # Remove existing style
    highlight_regex = re.compile(r"\n/\*STYLE:(.+?) VERSION:(.+?)\*/[\s\S]+?/\*END\*/")
    current_styles = re.sub(highlight_regex, "", current_styles)

    # Add new style
    start = f"/*STYLE:{style_name} VERSION:{HLJS_VERSION}*/"
    end = "/*END*/"
    new_styles = f"{current_styles}\n{start}\n{new_highlight_style}\n{end}"

    anki_api.update_note_type_styling(new_styles)


def handle_highlighjs_script(anki_media: AnkiMedia, anki_api: AnkiApi) -> None:
    # Search for file in anki media folder. Return if exists
    # Download script from CDN (raise error if can't)
    # Add link to script and script for automatic execution at the end of Front and Back fields
    pass
