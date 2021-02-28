from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    front_md: str
    back_md: str
    tags: List[str]
    deck_name: str
    anki_id: int = None
    front_html: str = None
    back_html: str = None
