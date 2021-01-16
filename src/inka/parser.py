import filecmp
import os
import sys
import random
import re
import shutil

from .card import Card
from .image import Image

DEFAULT_ANKI_FOLDERS = {
    'win32': r'~\AppData\Roaming\Anki2',
    'linux': '~/.local/share/Anki2',
    'darwin': '~/Library/Application Support/Anki2'
}


class Parser:

    def __init__(self, file_path, anki_user_name='User 1'):
        self.file_path = file_path

        anki_folder_path = os.path.expanduser(DEFAULT_ANKI_FOLDERS[sys.platform])
        self.anki_media_path = f'{anki_folder_path}/{anki_user_name}/collection.media'

    def collect_cards(self):
        note_string = self.get_note_string()

        question_sections = self.get_question_sections(note_string)

        cards = []
        for section in question_sections:
            cards.extend(self.get_cards_from_section(section))

        return cards

    def get_cards_from_section(self, section):
        section = self.handle_images(section)

        tags = self.get_tags_from_section(section)
        deck_name = self.get_deck_name_from_section(section)

        questions = re.findall(r'^\d+\..+?(?=^>)',
                               section,
                               re.DOTALL | re.MULTILINE)
        # Clean questions from whitespace at the start and the end of string
        questions = list(map(lambda q: re.sub(r'\d+\.', '', q, 1).strip(), questions))

        answers = re.findall(r'(?:>.*?\n)+',
                             section,
                             re.DOTALL | re.MULTILINE)

        # Clean (remove '>' and unnecessary whitespace) answer strings
        answers = list(map(self.clean_answer_string, answers))

        if len(questions) != len(answers):
            raise ValueError(f'Different number of questions and answers in section:\n{section}')

        cards = []
        for question, answer in zip(questions, answers):
            cards.append(Card(question, answer, tags, deck_name))

        return cards

    def handle_images(self, section):
        # Find all unique image links in the text
        image_links = set(re.findall(r'!\[.*?]\(.*?\)', section))
        images = [Image(link) for link in image_links]

        # Change image name if image with this name already exists in Anki Media folder

        # Copy images to Anki Media folder
        # And change all image links in section string
        for image in images:
            try:
                self.copy_image_to_anki_media(image)
            except OSError:
                raise OSError(f"Couldn't find image '{image.original_md_link}' in path '{image.abs_path}'!")

            section = section.replace(image.original_md_link, image.updated_md_link)

        return section

    def copy_image_to_anki_media(self, image):
        path_to_image = f'{self.anki_media_path}/{image.file_name}'

        # Check if image already exists in Anki Media folder
        if os.path.exists(path_to_image):
            # If same image is already in folder then skip
            if filecmp.cmp(image.abs_path, path_to_image):
                image.path = image.file_name
                return

            # If not same then rename our image
            image.rename(f'{random.randint(100000, 999999)}_{image.file_name}')
            path_to_image = f'{self.anki_media_path}/{image.file_name}'

        # Copy image
        shutil.copyfile(image.abs_path, path_to_image)

        # Change path to be just file name (for it to work in Anki)
        image.path = image.file_name

    def get_tags_from_section(self, section):
        match = re.search(r'(?<=^Tags:).*?$',
                          section,
                          re.MULTILINE)
        if not match:
            return []

        tags = match.group().strip().split()
        return tags

    def get_deck_name_from_section(self, section):
        match = re.search(r'(?<=^Deck:).*?$',
                          section,
                          re.MULTILINE)

        if not match or not match.group().strip():
            raise ValueError(f"Couldn't find deck name in:\n{section}")

        deck_name = match.group().strip()
        return deck_name

    def clean_answer_string(self, answer):
        lines = answer.splitlines()
        # Remove first char ('>') and whitespace at the start
        # and the end of each line
        lines = map(lambda l: l[1:].strip(), lines)

        return '\n'.join(lines)

    def get_question_sections(self, note_string):
        return re.findall(r'^---$.+?^---$',
                          note_string,
                          re.MULTILINE | re.DOTALL)

    def get_note_string(self):
        with open(self.file_path, mode='rt', encoding='utf-8') as note:
            note_string = note.read()

        return note_string
