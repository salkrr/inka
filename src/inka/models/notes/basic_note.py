from typing import List

from .base_note import BaseNote


class BasicNote(BaseNote):
    """Front/Back note type"""

    def __init__(self, front_md: str, back_md: str, tags: List[str], deck_name: str, anki_id: int = None):
        super().__init__(tags, deck_name, anki_id)

        self.raw_front_md = front_md
        self.raw_back_md = back_md
        self.updated_front_md = front_md  # With updated image links
        self.updated_back_md = back_md  # With updated image links

        self.front_html = None
        self.back_html = None

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        return (self.raw_front_md == other.raw_front_md and
                self.raw_back_md == other.raw_back_md)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(front_md={self.raw_front_md!r}, back_md={self.raw_back_md!r}, '
            f'tags={self.tags!r}, deck_name={self.deck_name!r}, anki_id={self.anki_id!r})'
        )
