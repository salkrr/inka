from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    front_md: str
    back_md: str
    tags: List[str]
    deck_name: str

    updated_front_md: str = None  # With updated image links
    updated_back_md: str = None  # With updated image links
    front_html: str = None
    back_html: str = None
    changed: bool = False  # Card was marked as changed in Anki
    to_delete: bool = False  # Card was marked to be deleted in Anki
    anki_id: int = None

    def __post_init__(self):
        self.updated_front_md = self.front_md
        self.updated_back_md = self.back_md
