from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    front_md: str
    back_md: str
    tags: List[str]
    deck_name: str
    changed: bool = False  # Card was marked as changed in Anki
    to_delete: bool = False  # Card was marked to be deleted in Anki
    anki_id: int = None
    front_html: str = None
    back_html: str = None
