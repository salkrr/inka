import filecmp
import os
import random
import re
import shutil
import sys
from typing import List

from .card import Card
from .image import Image

DEFAULT_ANKI_FOLDERS = {
    'win32': r'~\AppData\Roaming\Anki2',
    'linux': '~/.local/share/Anki2',
    'darwin': '~/Library/Application Support/Anki2'
}


class Parser:
    _section_regex = r'^---\n(.+?)^---$'
    _deck_name_regex = '(?<=^Deck:).*?$'
    _tags_line_regex = '(?<=^Tags:).*?$'
    _card_substring_regex = r'^\d+\.[\s\S]+?(?:^>.*?(?:\n|$))+'
    _question_regex = r'^\d+\.[\s\S]+?(?=^>)'
    _question_prefix_regex = r'\d+\.'
    _answer_regex = r'(?:^>.*?(?:\n|$))+'

    def __init__(
            self,
            file_path: str,
            anki_profile: str
    ):
        self._file_path = file_path

        anki_folder_path = os.path.expanduser(DEFAULT_ANKI_FOLDERS[sys.platform])
        self._anki_media_path = f'{anki_folder_path}/{anki_profile}/collection.media'

    def collect_cards(self) -> List[Card]:
        """Get all cards from the file which path was passed to the Parser"""
        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            file_string = f.read()

        question_sections = self._get_sections(file_string)

        cards = []
        for section in question_sections:
            cards.extend(self._get_cards_from_section(section))

        return cards

    def _get_sections(self, file_contents: str) -> List[str]:
        """Get all sections (groups of cards) from the file string"""
        return re.findall(self._section_regex,
                          file_contents,
                          re.MULTILINE | re.DOTALL)

    def _get_cards_from_section(self, section: str) -> List[Card]:
        """Get all Cards from the section string"""
        section = self._handle_images(section)

        tags = self._get_tags(section)
        deck_name = self._get_deck_name(section)

        # Get all section's substrings which contain question-answer pairs
        card_substrings = self._get_card_substrings(section)

        # Create cards
        cards = []
        for substring in card_substrings:
            question = self._get_question(substring)

            answer = self._get_answer(substring)

            cards.append(Card(front=question,
                              back=answer,
                              tags=tags,
                              deck_name=deck_name))

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

    @classmethod
    def _get_deck_name(cls, section: str) -> str:
        """Get deck name specified for this section"""
        matches = re.findall(cls._deck_name_regex,
                             section,
                             re.MULTILINE)

        if not matches:
            raise ValueError(f"Couldn't find deck name in section:\n{section}")

        if len(matches) > 1:
            raise ValueError(f'More than one deck name field in section:\n{section}')

        deck_name = matches[0].strip()
        if not deck_name:
            raise ValueError(f'Empty deck name field in section:\n{section}')

        return deck_name

    @classmethod
    def _get_card_substrings(cls, section: str) -> List[str]:
        """Get all section substrings with question-answer pairs"""
        return re.findall(cls._card_substring_regex,
                          section,
                          re.MULTILINE)

    @classmethod
    def _get_question(cls, text: str) -> str:
        """Get clean question string from text
         (without digit followed by period and trailing whitespace)"""
        question_match = re.search(cls._question_regex,
                                   text,
                                   re.MULTILINE)

        question = re.sub(cls._question_prefix_regex, '', question_match.group(), 1).strip()

        return question

    @classmethod
    def _get_answer(cls, text: str) -> str:
        """Get clean answer string from text (without '>' and trailing whitespace)"""
        answer_match = re.search(cls._answer_regex,
                                 text,
                                 re.MULTILINE)

        # Remove first char ('>') and whitespace at the start
        # and the end of each line
        lines = answer_match.group().splitlines()
        lines = map(lambda l: l[1:].strip(), lines)

        answer = '\n'.join(lines)

        return answer
