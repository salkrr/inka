from typing import Callable, Iterable, Any


class BaseNote:
    """Base class for all other note types"""

    def __init__(self, tags: Iterable[str], deck_name: str, anki_id: int = None):
        self.tags = tags
        self.deck_name = deck_name
        self.anki_id = anki_id
        self.changed = False  # Card was marked as changed in Anki
        self.to_delete = False  # Card was marked to be deleted in Anki

    def convert_fields_to_html(self, convert_func: Callable) -> None:
        """Convert note fields from markdown to html using provided function"""
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return (self.tags == other.tags and
                self.deck_name == other.deck_name)
