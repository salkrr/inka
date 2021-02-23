from dataclasses import dataclass
from typing import List, Union


@dataclass
class Card:
    front_md: str
    back_md: str
    tags: List[str]
    deck_name: str
    front_html: str = None
    back_html: str = None
    anki_id: Union[str, int] = None
