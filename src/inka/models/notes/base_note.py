from typing import List


class BaseNote:
    """Base class for all other note types"""

    def __init__(self, tags: List[str], deck_name: str, anki_id: int = None):
        self.tags = tags
        self.deck_name = deck_name
        self.anki_id = anki_id
        self.changed = False  # Card was marked as changed in Anki
        self.to_delete = False  # Card was marked to be deleted in Anki

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (self.tags == other.tags and
                self.deck_name == other.deck_name)
