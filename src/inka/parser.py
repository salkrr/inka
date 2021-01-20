import filecmp
import os
import random
import re
import shutil
import sys

from .card import Card
from .image import Image

DEFAULT_ANKI_FOLDERS = {
    'win32': r'~\AppData\Roaming\Anki2',
    'linux': '~/.local/share/Anki2',
    'darwin': '~/Library/Application Support/Anki2'
}


class Parser:
    deck_name_regex = '(?<=^Deck:).*?$'
    tags_line_regex = '(?<=^Tags:).*?$'

    def __init__(
            self, file_path: str,
            anki_user_name: str = 'User 1',
            section_regex: str = '^---\n(.+?)^---$'
    ):
        self._file_path = file_path

        anki_folder_path = os.path.expanduser(DEFAULT_ANKI_FOLDERS[sys.platform])
        self._anki_media_path = f'{anki_folder_path}/{anki_user_name}/collection.media'

        self.section_regex = section_regex

    def collect_cards(self) -> list[Card]:
        """Get all cards from the file which path was passed to the Parser"""
        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            file_string = f.read()

        question_sections = self._get_question_sections(file_string)

        cards = []
        for section in question_sections:
            cards.extend(self._get_cards_from_section(section))

        return cards

    def _get_question_sections(self, file_contents: str) -> list[str]:
        """Get all sections (groups of cards) from the file string"""
        return re.findall(self.section_regex,
                          file_contents,
                          re.MULTILINE | re.DOTALL)

    def _get_cards_from_section(self, section: str) -> list[Card]:
        """Get all Cards from the section string"""
        section = self._handle_images(section)

        tags = self._get_tags_from_section(section)
        deck_name = self._get_deck_name_from_section(section)

        questions = re.findall(r'^\d+\..+?(?=^>)',
                               section,
                               re.DOTALL | re.MULTILINE)
        # Clean questions from whitespace at the start and the end of string
        questions = list(map(lambda q: re.sub(r'\d+\.', '', q, 1).strip(), questions))

        answers = re.findall(r'(?:>.*?\n)+',
                             section,
                             re.DOTALL | re.MULTILINE)

        # Clean (remove '>' and unnecessary whitespace) answer strings
        answers = list(map(self._clean_answer_string, answers))

        if len(questions) != len(answers):
            raise ValueError(f'Different number of questions and answers in section:\n{section}')

        cards = []
        for question, answer in zip(questions, answers):
            cards.append(Card(question, answer, tags, deck_name))

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
        path_to_image = f'{self._anki_media_path}/{image.file_name}'

        # Check if image already exists in Anki Media folder
        if os.path.exists(path_to_image):
            # If same image is already in folder then skip
            if filecmp.cmp(image.abs_path, path_to_image):
                image.path = image.file_name
                return

            # If not same then rename our image
            image.rename(f'{random.randint(100000, 999999)}_{image.file_name}')
            path_to_image = f'{self._anki_media_path}/{image.file_name}'

        # Copy image
        shutil.copyfile(image.abs_path, path_to_image)

        # Change path to be just file name (for it to work in Anki)
        image.path = image.file_name

    def _get_tags_from_section(self, section: str) -> list[str]:
        """Get tags specified for this section"""
        matches = re.findall(self.tags_line_regex,
                             section,
                             re.MULTILINE)
        if not matches:
            return []

        if len(matches) > 1:
            raise ValueError(f'More than one tag field in section:\n{section}')

        tags = matches[0].strip().split()
        return tags

    def _get_deck_name_from_section(self, section: str) -> str:
        """Get deck name specified for this section"""
        matches = re.findall(self.deck_name_regex,
                             section,
                             re.MULTILINE)

        if not matches:
            raise ValueError(f"Couldn't find deck name in section:\n{section}")

        if len(matches) > 1:
            raise ValueError(f'More than one deck name field in section:\n{section}')

        deck_name = matches[0].strip()
        if not deck_name:
            raise ValueError(f"Empty deck name field in section:\n{section}")

        return deck_name

    def _clean_answer_string(self, answer: str) -> str:
        """Get answer string without prefix in the line start"""
        # Remove first char ('>') and whitespace at the start
        # and the end of each line
        lines = answer.splitlines()
        lines = map(lambda l: l[1:].strip(), lines)

        return '\n'.join(lines)
