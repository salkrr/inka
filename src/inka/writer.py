from pathlib import Path
from typing import Union, List

from .card import Card
from .parser import Parser


class Writer:
    """Class for editing file with cards"""

    def __init__(self, file_path: Union[str, Path], cards: List[Card]):
        self._file_path = file_path
        self._cards = cards

        with open(self._file_path, mode='rt', encoding='utf-8') as f:
            self._file_content = f.read()

    def write_card_ids(self):
        """Add lines with IDs to the cards from the file"""
        for card in self._cards:
            # Skip cards without ID
            if card.anki_id is None:
                continue

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

            id_string = f'<!--ID:{card.anki_id}-->'
            if existing_id is None:
                # Add line with ID after newline
                self._file_content = (self._file_content[:newline_index + 1] +
                                      id_string + '\n' +
                                      self._file_content[newline_index + 1:])
            else:
                # Substitute existing ID with the new one
                self._file_content = self._file_content.replace(f'<!--ID:{existing_id}-->', id_string)

        self._save()

    def _save(self):
        """Save file state into the file system"""
        with open(self._file_path, mode='wt', encoding='utf-8') as f:
            f.write(self._file_content)

    def __repr__(self):
        return f'{type(self).__name__}(file_path={self._file_path!r}, cards={self._cards!r})'
