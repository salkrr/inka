import re
from typing import List

import mistune

from .notes.basic_note import BasicNote
from .notes.cloze_note import ClozeNote
from ..mistune_plugins.mathjax import plugin_mathjax, BLOCK_MATHJAX, INLINE_MATHJAX

MD = mistune.create_markdown(plugins=['strikethrough', 'footnotes', 'table', plugin_mathjax])


def convert_cloze_deletions_to_anki_format(cloze_notes: List[ClozeNote]):
    """Convert short syntax for cloze deletions to anki syntax"""
    code_inline_regex = re.compile(
        r'`[\S\s]+?`',
        re.MULTILINE
    )
    code_block_regex = re.compile(
        r'```[\s\S]+?```',
        re.MULTILINE
    )
    cloze_deletion_regex = re.compile(
        r'{{c\d+::[\s\S]*?}}|'
        r'{c?\d+::[\s\S]*?}|'
        r'{[\s\S]*?}',
        re.MULTILINE)
    anki_cloze_regex = re.compile(r'{{c\d+::[\s\S]*?}}', re.MULTILINE)
    explicit_short_regex = re.compile(r'{c?(\d+)::([\s\S]*?)}', re.MULTILINE)
    implicit_short_regex = re.compile(r'{([\s\S]*?)}', re.MULTILINE)

    for note in cloze_notes:
        # We remove code and math blocks from string before searching cloze deletions
        # Possible issue: if we have inside block string '{ 123 }' and have the same string outside block
        # then it may be replaced by anki cloze syntax
        redacted_text = re.sub(code_block_regex, '', note.raw_text_md)  # block code should be removed before inline
        redacted_text = re.sub(code_inline_regex, '', redacted_text)
        redacted_text = re.sub(BLOCK_MATHJAX, '', redacted_text)  # block math should be removed before inline math
        redacted_text = re.sub(INLINE_MATHJAX, '', redacted_text)
        cloze_strings = re.findall(cloze_deletion_regex, redacted_text)

        for i, cloze in enumerate(cloze_strings, start=1):
            if re.match(anki_cloze_regex, cloze):
                continue

            explicit_match = re.match(explicit_short_regex, cloze)
            if explicit_match:
                explicit_index = explicit_match.group(1)
                content = explicit_match.group(2)
                new_cloze = '{{' + f'c{explicit_index}::{content}' + '}}'
                note.updated_text_md = note.updated_text_md.replace(cloze, new_cloze, 1)
                continue

            implicit_match = re.match(implicit_short_regex, cloze)
            content = implicit_match.group(1)
            new_cloze = '{{' + f'c{i}::{content}' + '}}'
            note.updated_text_md = note.updated_text_md.replace(cloze, new_cloze, 1)


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
