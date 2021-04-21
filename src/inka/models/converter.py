import re
from typing import Union, Tuple, AnyStr, Iterator, Match, Pattern

import mistune

from .notes.basic_note import BasicNote
from .notes.cloze_note import ClozeNote
from ..mistune_plugins.mathjax import plugin_mathjax, BLOCK_MATH, INLINE_MATH

MD = mistune.create_markdown(plugins=['strikethrough', 'footnotes', 'table', plugin_mathjax])

INLINE_CODE_REGEX = re.compile(
    r'`[\S\s]+?`',
    re.MULTILINE
)
BLOCK_CODE_REGEX = re.compile(
    r'```[\s\S]+?```',
    re.MULTILINE
)
CLOZE_DELETION_REGEX = re.compile(
    r'{{c\d+::[\s\S]*?}}|'
    r'{c?\d+::[\s\S]*?}|'
    r'{[\s\S]*?}',
    re.MULTILINE
)
ANKI_CLOZE_REGEX = re.compile(r'{{c\d+::[\s\S]*?}}', re.MULTILINE)
EXPLICIT_SHORT_CLOZE_REGEX = re.compile(r'{c?(\d+)::([\s\S]*?)}', re.MULTILINE)
IMPLICIT_SHORT_CLOZE_REGEX = re.compile(r'{([\s\S]*?)}', re.MULTILINE)

INLINE_CODE_PLACEHOLDER = 'INLINE_CODE_PLACEHOLDER'
BLOCK_CODE_PLACEHOLDER = 'BLOCK_CODE_PLACEHOLDER'
INLINE_MATH_PLACEHOLDER = 'INLINE_MATH_PLACEHOLDER'
BLOCK_MATH_PLACEHOLDER = 'BLOCK_MATH_PLACEHOLDER'


def convert_notes_to_html(notes: Iterator[Union[BasicNote, ClozeNote]]):
    """Convert note fields to html"""
    for note in notes:
        note.convert_fields_to_html(_convert_md_to_html)


def convert_cloze_deletions_to_anki_format(cloze_notes: Iterator[ClozeNote]):
    """Convert short syntax for cloze deletions to anki syntax"""
    for note in cloze_notes:
        # We substitute code and math inline/blocks with placeholders before searching cloze deletions
        # Block code should be removed before inline code
        block_code_matches, redacted_text = \
            _get_matches_and_updated_text(BLOCK_CODE_REGEX, BLOCK_CODE_PLACEHOLDER, note.updated_text_md)
        inline_code_matches, redacted_text = \
            _get_matches_and_updated_text(INLINE_CODE_REGEX, INLINE_CODE_PLACEHOLDER, redacted_text)

        # Block math should be removed before inline math
        block_math_matches, redacted_text = \
            _get_matches_and_updated_text(BLOCK_MATH, BLOCK_MATH_PLACEHOLDER, redacted_text)
        inline_math_matches, redacted_text = \
            _get_matches_and_updated_text(INLINE_MATH, INLINE_MATH_PLACEHOLDER, redacted_text)

        cloze_strings = CLOZE_DELETION_REGEX.findall(redacted_text)
        redacted_text = _replace_short_cloze_syntax(redacted_text, cloze_strings)

        redacted_text = _replace_placeholders_with_content(block_code_matches, BLOCK_CODE_PLACEHOLDER, redacted_text)
        redacted_text = _replace_placeholders_with_content(inline_code_matches, INLINE_CODE_PLACEHOLDER, redacted_text)
        redacted_text = _replace_placeholders_with_content(block_math_matches, BLOCK_MATH_PLACEHOLDER, redacted_text)
        redacted_text = _replace_placeholders_with_content(inline_math_matches, INLINE_MATH_PLACEHOLDER, redacted_text)

        note.updated_text_md = redacted_text


def _convert_md_to_html(text: str) -> str:
    # We delete '\n' before and after each html tag because Anki is rendering them as newlines
    return re.sub(r'\n?(<.+?>)\n?',
                  lambda tag_match: tag_match.group(1),
                  MD(text))


def _get_matches_and_updated_text(regex_pattern: Union[str, Pattern],
                                  placeholder: str,
                                  text: str) -> Tuple[Iterator[Match[AnyStr]], str]:
    """Search for matches with regex pattern and then replace same matches in text with placeholder"""
    matches = re.finditer(regex_pattern, text)
    new_text = re.sub(regex_pattern, placeholder, text)
    return matches, new_text


def _replace_placeholders_with_content(matches: Iterator[Match[AnyStr]], placeholder: str, text: str) -> str:
    """Replace placeholder occurrences with text from regex matches"""
    new_text = text
    for match in matches:
        new_text = new_text.replace(placeholder, match.group(0), 1)
    return new_text


def _replace_short_cloze_syntax(text: str, cloze_strings: Iterator[str]) -> str:
    """Replace short implicit and explicit cloze syntax with Anki cloze syntax in text"""
    new_text = text
    for i, cloze in enumerate(cloze_strings, start=1):
        if re.match(ANKI_CLOZE_REGEX, cloze):
            continue

        explicit_match = re.match(EXPLICIT_SHORT_CLOZE_REGEX, cloze)
        if explicit_match:
            explicit_index = explicit_match.group(1)
            content = explicit_match.group(2)
            new_cloze = '{{' + f'c{explicit_index}::{content}' + '}}'
            new_text = new_text.replace(cloze, new_cloze, 1)
            continue

        implicit_match = re.match(IMPLICIT_SHORT_CLOZE_REGEX, cloze)
        content = implicit_match.group(1)
        new_cloze = '{{' + f'c{i}::{content}' + '}}'
        new_text = new_text.replace(cloze, new_cloze, 1)

    return new_text
