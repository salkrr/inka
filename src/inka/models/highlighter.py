import re
from typing import Type, Dict

import requests
from requests import HTTPError

from .anki_api import AnkiApi
from .anki_media import AnkiMedia
from .notes.note import Note
from ..exceptions import HighlighterError

HLJS_VERSION = "10.7.1"
BASE_URL = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{HLJS_VERSION}"

# Thanks u/arthurmilchior for the initial idea.
# https://www.reddit.com/r/Anki/comments/kzttw2/syntax_coloring_of_code_in_anki/
AUTOSTART_SCRIPT = """<script>
function color() {
    var selector = 'pre code';
    if (typeof hljs !== 'undefined') {
        codes = document.querySelectorAll(selector)
        codes.forEach(element => {
            hljs.highlightBlock(element);
        });
    } else {
        setTimeout(color, 50)
    }
}
color()
</script>"""


def add_code_highlight_to(
        note_type: Type[Note],
        style_name: str,
        anki_api: AnkiApi,
        anki_media: AnkiMedia
) -> None:
    """Add highlighting of code blocks to the current note type

    Args:
        note_type: the type of note to which the highlight will be added
        style_name: name of the highlight.js style to use
        anki_api: instance of AnkiApi used to modify note type
        anki_media: instance of AnkiMedia used to save highlight.js files
    Raises:
        ConnectionError: if something gone wrong during download of highlight.js style or script
    """
    try:
        _update_style_in(note_type, style_name, anki_api)
    except HTTPError as e:
        raise HighlighterError(f"couldn't download styles for code highlighting. Reason: {e}")
    except requests.exceptions.ConnectionError:
        raise HighlighterError(f"couldn't download styles for code highlighting. Check your internet connection.")

    try:
        _handle_highlighjs_files_for(note_type, anki_media, anki_api)
    except HTTPError as e:
        raise HighlighterError(f"couldn't download highlight.js script for code highlighting. Reason: {e}")
    except requests.exceptions.ConnectionError:
        raise HighlighterError(
            f"couldn't download highlight.js script for code highlighting. Check your internet connection.")


def _update_style_in(note_type: Type[Note], style_name: str, anki_api: AnkiApi) -> None:
    """Adds highlight.js style to the note type

    Args:
        note_type: the type of note to which styles will be added
        style_name: name of the highlight.js style to use
        anki_api: instance of AnkiApi used to modify note type
    Raises:
        ValueError: style_name is empty string or None
        HTTPError: something gone wrong during process of downloading style
    """
    if not style_name:
        raise ValueError("highlight style value in config must not be empty")

    current_styles = anki_api.fetch_note_type_styling(note_type)

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

    anki_api.update_note_type_styling(note_type, new_styles)


def _handle_highlighjs_files_for(note_type: Type[Note], anki_media: AnkiMedia, anki_api: AnkiApi) -> None:
    """Adds highlight.js library and script that executes it to note type fields

    Args:
        note_type: the type of note to which links to files and autostart script will be added
        anki_api: instance of AnkiApi used to modify note type
        anki_media: instance of AnkiMedia used to save highlight.js files
    Raises:
        HTTPError: something gone wrong during process of downloading style
    """
    script_name = "_hl.pack.js"
    if not anki_media.exists(script_name):
        # Download script from CDN
        response = requests.get(f"{BASE_URL}/highlight.min.js")
        response.raise_for_status()
        script_content = response.text

        anki_media.create_file(script_name, script_content)

    # Get templates from note type
    templates = anki_api.fetch_note_type_templates(note_type)

    # Add link to script and script for automatic execution at the end of all fields of templates
    script_elements = f'<script src="{script_name}"></script>\n{AUTOSTART_SCRIPT}'
    new_templates: Dict[str, Dict[str, str]] = {}
    for template, fields in templates.items():
        new_templates[template] = {}
        for field, value in fields.items():
            new_templates[template][field] = value
            if value.find(script_elements) == -1:
                new_templates[template][field] += f"\n{script_elements}"

    # Don't update templates if nothing changed
    if templates == new_templates:
        return

    anki_api.update_note_type_templates(note_type, new_templates)
