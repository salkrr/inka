import filecmp
import os
import random
import re
import shutil
import sys
from pathlib import Path
from typing import List, Union, Optional

from .card import Card
from .image import Image

DEFAULT_ANKI_FOLDERS = {
    'win32': r'~\AppData\Roaming\Anki2',
    'linux': '~/.local/share/Anki2',
    'darwin': '~/Library/Application Support/Anki2'
}


class Parser:
    """Class for getting cards and various information about them from the text file"""

    _section_regex = r'^---\n(.+?)^---$'
    _deck_name_regex = '(?<=^Deck:).*?$'
    _tags_line_regex = '(?<=^Tags:).*?$'
    _card_substring_regex = r'^(?:<!--ID:.+-->\n)?\d+\.[\s\S]+?(?:^>.*?(?:\n|$))+'
    _id_regex = r'^<!--ID:(\S+)-->$'
    _question_regex = r'^\d+\.([\s\S]+?)(?=^>)'
    _answer_regex = r'(?:^>.*?(?:\n|$))+'

    def __init__(
            self,
            file_path: Union[str, Path],
            default_deck: str,
            anki_profile: str
    ):
        self._file_path = file_path
        self._default_deck = default_deck

        anki_folder_path = os.path.expanduser(DEFAULT_ANKI_FOLDERS[sys.platform])
        self._anki_media_path = f'{anki_folder_path}/{anki_profile}/collection.media'

    def collect_cards(self) -> List[Card]:
        """Get all cards from the file which path was passed to the Parser"""
        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            file_string = f.read()

        question_sections = self.get_sections(file_string)

        cards = []
        for section in question_sections:
            cards.extend(self._get_cards_from_section(section))

        return cards

    @classmethod
    def get_sections(cls, file_contents: str) -> List[str]:
        """Get all sections (groups of cards) from the file string"""
        return re.findall(cls._section_regex,
                          file_contents,
                          re.MULTILINE | re.DOTALL)

    def _get_cards_from_section(self, section: str) -> List[Card]:
        """Get all Cards from the section string"""
        section = self._handle_images(section)

        tags = self._get_tags(section)
        deck_name = self._get_deck_name(section)

        # Get all section's substrings which contain question-answer pairs
        card_substrings = self.get_card_substrings(section)

        # Create cards
        cards = []
        for substring in card_substrings:
            anki_id = self.get_id(substring)
            question = self.get_question(substring)
            answer = self._get_cleaned_answer(substring)

            cards.append(Card(front_md=question,
                              back_md=answer,
                              tags=tags,
                              deck_name=deck_name,
                              anki_id=anki_id))

        return cards

    def _handle_images(self, section: str) -> str:
        """
        Copy images to Anki media folder and change their source
        to be just filename (for Anki to find them)
        """
        # Find all unique images in the text
        image_links = set(re.findall(r'!\[.*?]\(.*?\)', section))
        images = [Image(link) for link in image_links]

        # Copy images to Anki Media folder
        # And change all image links in section string
        for image in images:
            try:
                self._copy_image_to_anki_media(image)
            except OSError:
                raise OSError(f"Couldn't find image '{image.original_md_link}' in path '{image.abs_path}'!")

            # Update all image link occurrences with new one which has updated source
            section = section.replace(image.original_md_link, image.updated_md_link)

        return section

    def _copy_image_to_anki_media(self, image: Image):
        """Copy image to Anki media folder"""
        path_to_anki_image = f'{self._anki_media_path}/{image.file_name}'

        # Check if image already exists in Anki Media folder
        if os.path.exists(path_to_anki_image):
            # If same image is already in folder then skip
            if filecmp.cmp(image.abs_path, path_to_anki_image):
                image.path = image.file_name
                return

            # If not same then rename our image
            image.rename(f'{random.randint(100000, 999999)}_{image.file_name}')
            path_to_anki_image = f'{self._anki_media_path}/{image.file_name}'

        # Copy image
        shutil.copyfile(image.abs_path, path_to_anki_image)

        # Change path to be just file name (for it to work in Anki)
        image.path = image.file_name

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
    def get_card_substrings(cls, section: str) -> List[str]:
        """Get all section substrings with question-answer pairs and an ID"""
        # TODO: rename method and variables/comments from 'substring' to 'string'
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
        # Remove first char ('>') and whitespace at the start
        # and the end of each line
        lines = cls.get_answer(text).splitlines()
        # TODO: make more tests for this fix of the bug.
        #  Why doesn't add one space symbol when converted to html?
        # lines = map(lambda l: l[1:].rstrip(), lines)
        lines = map(lambda l: l[1:].strip(), lines)

        answer = '\n\n'.join(lines)

        return answer
