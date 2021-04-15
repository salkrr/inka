from typing import List

from .base_note import BaseNote


class ClozeNote(BaseNote):
    """Cloze note type"""

    def __init__(self, text_md: str, tags: List[str], deck_name: str, anki_id: int = None):
        super().__init__(tags, deck_name, anki_id)

        self.raw_text_md = text_md
        self.updated_text_md = text_md  # With updated image links

        self.text_html = None

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        return self.raw_text_md == other.raw_text_md
