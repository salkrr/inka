from pathlib import Path
from typing import Union, List, Optional

from .card import Card
from .parser import Parser


class Writer:
    """Class for editing file with cards"""

    def __init__(self, file_path: Union[str, Path], cards: List[Card]):
        self._file_path = file_path
        self._cards = cards

        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            self._file_content = f.read()
        self._card_strings = Parser.get_card_substrings(self._file_content)

    def update_card_ids(self):
        """Update lines with IDs of the cards from the file"""
        for card in self._cards:
            # Find card's question in file string
            question_start = self._file_content.find(card.front_md)

            # Find newline character that comes before question
            newline_index = self._file_content[:question_start].rfind('\n')

            # Search for existing line with ID
            line_before_question = self._file_content[:newline_index].splitlines()[-1]
            existing_id = Parser.get_id(line_before_question)

            # Skip if ID hasn't changed
            if existing_id == card.anki_id:
                continue

            id_string = f'<!--ID:{card.anki_id}-->\n'
            if not card.anki_id:
                # To delete ID from card in file if Card object has no ID
                id_string = ''

            if existing_id is None:
                # Add line with ID after newline
                self._file_content = (self._file_content[:newline_index + 1] +
                                      id_string +
                                      self._file_content[newline_index + 1:])
            else:
                # Substitute existing ID with the new one
                self._file_content = self._file_content.replace(f'<!--ID:{existing_id}-->\n', id_string)

        self._save()

    def update_card_fields(self):
        """Update question and answer fields in cards in file"""
        for card in self._cards:
            if not card.changed:
                continue

            # Find string with this card by its ID
            card_string = self._get_card_string_by_id(card.anki_id)

            # Substitute question field
            current_question = Parser.get_question(card_string)
            self._file_content = self._file_content.replace(current_question, card.front_md)

            # Create new answer field (with '>')
            current_answer = Parser.get_answer(card_string).rstrip()
            lines = card.back_md.replace('\n\n', '\n').splitlines()
            new_answer = '\n'.join(map(lambda line: f'> {line}', lines))

            # Substitute answer field
            self._file_content = self._file_content.replace(current_answer, new_answer)

        self._save()

    def delete_cards(self):
        """Delete cards marked for deletion from the file"""
        for card in self._cards:
            if not card.to_delete:
                continue

            # Find string with this card by its ID
            card_string = self._get_card_string_by_id(card.anki_id)

            # Delete card text from file
            self._file_content = self._file_content.replace(card_string, '')

        self._save()

    def _save(self):
        """Save file state into the file system"""
        with open(self._file_path, mode='wt', encoding='utf-8') as f:
            f.write(self._file_content)
        self._card_strings = Parser.get_card_substrings(self._file_content)

    def _get_card_string_by_id(self, card_id: int) -> Optional[str]:
        """Gets card string from the file by cards ID. If card wasn't found returns None"""
        for string in self._card_strings:
            if string.find(str(card_id)) != -1:
                return string

    def __repr__(self):
        return f'{type(self).__name__}(file_path={self._file_path!r}, cards={self._cards!r})'
