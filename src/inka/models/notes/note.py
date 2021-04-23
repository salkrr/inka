from abc import ABC, abstractmethod
from typing import Callable, Iterable, Any, Dict, List

from inka.models.config import Config


class Note(ABC):
    """Base class for all other note types"""

    def __init__(self, tags: Iterable[str], deck_name: str, anki_id: int = None):
        self.tags = tags
        self.deck_name = deck_name
        self.anki_id = anki_id
        self.changed = False  # Card was marked as changed in Anki
        self.to_delete = False  # Card was marked to be deleted in Anki

    @property
    @abstractmethod
    def search_query(self) -> str:
        """Query to search for note in Anki"""
        pass

    @abstractmethod
    def convert_fields_to_html(self, convert_func: Callable[[str], str]) -> None:
        """Convert note fields from markdown to html using provided function"""
        pass

    @abstractmethod
    def update_fields_with(self, update_func: Callable[[str], str]) -> None:
        """Updates values of *updated* fields using provided function"""
        pass

    @abstractmethod
    def get_raw_fields(self) -> List[str]:
        """Get list of all raw (as in file) fields of this note"""
        pass

    @abstractmethod
    def get_raw_question_field(self) -> str:
        """Get value of raw (as in file) question field"""
        pass

    @abstractmethod
    def get_html_fields(self, cfg: Config) -> Dict[str, str]:
        """Return dictionary with Anki field names as keys and html strings as values"""
        pass

    @abstractmethod
    def get_note_info(self) -> str:
        """String used to display info about note in case of error"""
        pass

    @staticmethod
    @abstractmethod
    def get_anki_note_type(cfg: Config) -> str:
        """Get name of Anki note type"""
        pass

    @staticmethod
    def shorten_text(text: str) -> str:
        """Shorten text to the first 100 symbols"""
        return f'{text.strip()[:100]}...'

    @staticmethod
    def create_anki_search_query(text: str) -> str:
        """Create Anki search query from the supplied text"""
        special_chars = ['\\', '"', '*', '_', ':']

        search_query = text
        for char in special_chars:
            escaped_char = '\\' + char
            search_query = search_query.replace(char, escaped_char)

        return '"' + search_query + '"'

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return (self.tags == other.tags and
                self.deck_name == other.deck_name)
