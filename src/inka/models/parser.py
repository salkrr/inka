import re
from pathlib import Path
from typing import List, Union, Optional

from .card import Card


class Parser:
    """Class for getting cards and various information about them from the text file"""

    _section_regex = r'^---\n(.+?)^---$'
    _deck_name_regex = r'(?<=^Deck:).*?$'
    _tags_line_regex = r'(?<=^Tags:).*?$'
    _card_substring_regex = r'^(?:<!--ID:\S+-->\n)?\d+\.[\s\S]+?(?:^>.*?(?:\n|$))+'
    _id_regex = r'^<!--ID:(\S+)-->$'
    _question_regex = r'^\d+\.([\s\S]+?)(?=^>)'
    _answer_regex = r'(?:^>.*?(?:\n|$))+'

    def __init__(
            self,
            file_path: Union[str, Path],
            default_deck: str,
    ):
        self._file_path = file_path
        self._default_deck = default_deck

    def collect_cards(self) -> List[Card]:
        """Get all cards from the file which path was passed to the Parser"""
        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            file_string = f.read()

        question_sections = self._get_sections(file_string)

        cards = []
        for section in question_sections:
            cards.extend(self._get_cards_from_section(section))

        return cards

    def _get_cards_from_section(self, section: str) -> List[Card]:
        """Get all Cards from the section string"""
        tags = self._get_tags(section)
        deck_name = self._get_deck_name(section)

        # Get all section's substrings which contain question-answer pairs
        card_strings = self.get_card_strings(section)

        # Create cards
        cards = []
        for string in card_strings:
            anki_id = self.get_id(string)
            question = self.get_question(string)
            answer = self._get_cleaned_answer(string)

            cards.append(Card(front_md=question,
                              back_md=answer,
                              tags=tags,
                              deck_name=deck_name,
                              anki_id=anki_id))

        return cards

    def _get_deck_name(self, section: str) -> str:
        """Get deck name specified for this section"""
        matches = re.findall(Parser._deck_name_regex,
                             section,
                             re.MULTILINE)

        # If no deck name 
        if not matches:
            if not self._default_deck:
                raise ValueError(f"Couldn't find deck name in section:\n{section}")

            return self._default_deck

        if len(matches) > 1:
            raise ValueError(f'More than one deck name field in section:\n{section}')

        deck_name = matches[0].strip()
        if not deck_name:
            raise ValueError(f'Empty deck name field in section:\n{section}')

        return deck_name

    @classmethod
    def _get_sections(cls, file_contents: str) -> List[str]:
        """Get all sections (groups of cards) from the file string"""
        return re.findall(cls._section_regex,
                          file_contents,
                          re.MULTILINE | re.DOTALL)

    @classmethod
    def _get_tags(cls, section: str) -> List[str]:
        """Get tags specified for this section"""
        matches = re.findall(cls._tags_line_regex,
                             section,
                             re.MULTILINE)
        if not matches:
            return []

        if len(matches) > 1:
            raise ValueError(f'More than one tag field in section:\n{section}')

        tags = matches[0].strip().split()
        return tags

    @classmethod
    def get_card_strings(cls, section: str) -> List[str]:
        """Get all section strings with question-answer pairs and an ID"""
        return re.findall(cls._card_substring_regex,
                          section,
                          re.MULTILINE)

    @classmethod
    def get_id(cls, text: str) -> Optional[int]:
        """Get card's ID from text. Returns None if id wasn't found or if it is incorrect."""
        id_match = re.search(cls._id_regex,
                             text,
                             re.MULTILINE)

        try:
            return int(id_match.group(1))
        except (ValueError, AttributeError):
            return None

    @classmethod
    def get_question(cls, text: str) -> str:
        """Get clean question string from text
         (without digit followed by period and trailing whitespace)"""
        question_match = re.search(cls._question_regex,
                                   text,
                                   re.MULTILINE)

        question = question_match.group(1).strip()

        return question

    @classmethod
    def get_answer(cls, text: str) -> str:
        """Get answer string from text"""
        answer_match = re.search(cls._answer_regex,
                                 text,
                                 re.MULTILINE)
        return answer_match.group()

    @classmethod
    def _get_cleaned_answer(cls, text: str) -> str:
        """Get clean answer string from text (without '>' and trailing whitespace)"""
        # Remove '>' and first whitespace char after it (if there is any)
        lines = cls.get_answer(text).splitlines()
        cleaned_lines = []
        for line in lines:
            if len(line) > 1 and line[1].isspace():
                cleaned_lines.append(line[2:].rstrip())
            else:
                cleaned_lines.append(line[1:].rstrip())

        # Join lines differently: if inside code block '\n' else '\n\n'
        answer = ''
        inside_code_block = False
        for i, line in enumerate(cleaned_lines):
            delimiter = '\n\n'
            # If start or end of code block
            if line.find('```') != -1:
                if inside_code_block:
                    inside_code_block = False
                    delimiter = '\n'
                else:
                    inside_code_block = True
                    delimiter = '\n\n'
            elif inside_code_block:
                delimiter = '\n'

            # First line doesn't need delimiter
            if i == 0:
                delimiter = ''

            answer = answer + delimiter + line

        return answer
