import re
from typing import List

import mistune

from .notes.basic_note import BasicNote
from ..mistune_plugins.mathjax import plugin_mathjax

MD = mistune.create_markdown(plugins=['strikethrough', 'footnotes', 'table', plugin_mathjax])


def convert_notes_to_html(notes: List[BasicNote]):
    """Convert note fields to html"""
    for note in notes:
        note.front_html = convert_md_to_html(note.updated_front_md)
        note.back_html = convert_md_to_html(note.updated_back_md)


def convert_md_to_html(text: str) -> str:
    # We delete '\n' before and after each html tag because Anki is rendering them as newlines
    return re.sub(r'\n?(<.+?>)\n?',
                  lambda tag_match: tag_match.group(1),
                  MD(text))

# def convert_note_to_md(note: BasicNote):
#     """Convert front_html and back_html fields to markdown and write result into raw_front_md and raw_back_md fields"""
#     # We needed to remove '\n\n' at the end of strings because
#     # this line brakes aren't needed for updating notes in file
#     note.raw_front_md = markdownify(note.front_html, heading_style='ATX', bullets='-').rstrip()
#     note.raw_back_md = markdownify(note.back_html, heading_style='ATX', bullets='-').rstrip()
