import re
from pathlib import Path
from typing import List, Union, Optional

from .notes.basic_note import BasicNote
from .notes.cloze_note import ClozeNote


class Parser:
    """Class for getting notes and various information about them from the text file"""

    _section_regex = re.compile(
        r'^---\n'  # start of section
        r'(.+?)'  # contents
        r'^---$',  # end of section
        re.MULTILINE | re.DOTALL
    )
    _deck_name_regex = re.compile(
        r'(?<=^Deck:)(.*?)$',
        re.MULTILINE
    )
    _tags_regex = re.compile(
        r'(?<=^Tags:)(.*?)$',
        re.MULTILINE
    )
    _all_notes_regex = re.compile(
        r'(?:^<!--ID:\S+-->\n)?'  # optional ID
        r'^\d+\.[\s\S]*?'  # card contents (optionally contains answer)
        r'(?=<!--ID:\S+-->|^\d+\.|\Z|^---$)',  # card ends before ID, start of next card, end of string, end of section
        re.MULTILINE
    )
    _basic_note_regex = re.compile(
        r'(?:^<!--ID:\S+-->\n)?'  # optional ID
        r'^\d+\.[\s\S]+?'  # card question
        r'(?:^>.*?(?:\n|$))+',  # card answer
        re.MULTILINE
    )
    _cloze_note_regex = re.compile(
        r"(?:^<!--ID:\S+-->\n)?"  # optional ID
        r"^\d+\.[\s\S]*?{[\s\S]*?}[\s\S]*?"  # contents that must have '{' and '}' symbols
        r"(?=<!--ID:\S+-->|^\d+\.|\Z|^---$)",  # card ends before ID, start of next card, end of string, end of section
        re.MULTILINE
    )
    _id_regex = re.compile(
        r'^<!--ID:(\S+)-->$',
        re.MULTILINE
    )
    _question_regex = re.compile(
        r'^\d+\.'  # question start 
        r'([\s\S]+?)'  # contents
        r'(?=^>|\Z)',  # answer start or end of string
        re.MULTILINE
    )
    _answer_regex = re.compile(
        r'(?:^>.*?(?:\n|$))+',
        re.MULTILINE
    )

    def __init__(
            self,
            file_path: Union[str, Path],
            default_deck: str,
    ):
        self._file_path = file_path
        self._default_deck = default_deck

    def collect_notes(self) -> List[Union[BasicNote, ClozeNote]]:
        """Get all notes from the file which path was passed to the Parser"""
        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            file_string = f.read()

        question_sections = self._get_sections(file_string)

        notes = []
        for section in question_sections:
            notes.extend(self._get_notes_from_section(section))

        return notes

    def _get_notes_from_section(self, section: str) -> List[Union[BasicNote, ClozeNote]]:
        """Get all Notes from the section string"""
        tags = self._get_tags(section)
        deck_name = self._get_deck_name(section)

        note_strings = self.get_note_strings(section)

        # Create note objects
        notes = []
        for string in note_strings:
            anki_id = self.get_id(string)

            # we check in this order because is_cloze_note_str can match front/back note if it contains curly braces
            if self._is_basic_note_str(string):
                question = self.get_question(string)
                answer = self._get_cleaned_answer(string)

                notes.append(BasicNote(front_md=question,
                                       back_md=answer,
                                       tags=tags,
                                       deck_name=deck_name,
                                       anki_id=anki_id))
            elif self._is_cloze_note_str(string):
                text = self.get_question(string)

                notes.append(ClozeNote(text_md=text,
                                       tags=tags,
                                       deck_name=deck_name,
                                       anki_id=anki_id))
        return notes

    def _get_deck_name(self, section: str) -> str:
        """Get deck name specified for this section"""
        matches = re.findall(Parser._deck_name_regex, section)

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
    def get_note_strings(cls, section: str) -> List[str]:
        """Get all strings of notes from section"""
        return re.findall(cls._all_notes_regex, section)

    @classmethod
    def get_id(cls, text: str) -> Optional[int]:
        """Get note's ID from text. Returns None if id wasn't found or if it is incorrect."""
        id_match = re.search(cls._id_regex, text)

        try:
            return int(id_match.group(1))
        except (ValueError, AttributeError):
            return None

    @classmethod
    def get_question(cls, text: str) -> str:
        """Get clean question string from text
         (without digit followed by period and trailing whitespace)"""
        question_match = re.search(cls._question_regex, text)

        question = question_match.group(1).strip()

        return question

    @classmethod
    def get_answer(cls, text: str) -> str:
        """Get answer string from text"""
        answer_match = re.search(cls._answer_regex, text)
        return answer_match.group()

    @classmethod
    def _get_sections(cls, file_contents: str) -> List[str]:
        """Get all sections (groups of notes) from the file string"""
        return re.findall(cls._section_regex, file_contents)

    @classmethod
    def _get_tags(cls, section: str) -> List[str]:
        """Get tags specified for this section"""
        matches = re.findall(cls._tags_regex, section)
        if not matches:
            return []

        if len(matches) > 1:
            raise ValueError(f'More than one tag field in section:\n{section}')

        tags = matches[0].strip().split()
        return tags

    @classmethod
    def _is_basic_note_str(cls, string: str) -> bool:
        """Check if note string contains basic note type"""
        match = re.search(cls._basic_note_regex, string)
        if not match:
            return False
        return True

    @classmethod
    def _is_cloze_note_str(cls, string: str) -> bool:
        """Check if note string contains cloze note type. Matches basic note type if it contains curly braces"""
        match = re.search(cls._cloze_note_regex, string)
        if not match:
            return False
        return True

    @classmethod
    def _get_cloze_note_strings(cls, section: str) -> List[str]:
        """Get all strings from section with only question and an (optional) ID"""
        return re.findall(cls._cloze_note_regex, section)

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
