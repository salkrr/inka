from typing import Callable, Iterable, Any, Dict

from inka.models.config import Config


class Note:
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

    def get_search_field(self) -> str:
        """Get field (with html) that will be used for search in Anki"""
        pass

    def get_raw_question_field(self) -> str:
        """Get value of raw (as in file) question field"""
        pass

    def get_html_fields(self, cfg: Config) -> Dict[str, str]:
        """Return dictionary with Anki field names as keys and html strings as values"""
        pass

    def get_note_info(self) -> str:
        """String used to display info about note in case of error"""
        pass

    @staticmethod
    def get_anki_note_type(cfg: Config) -> str:
        """Get name of Anki note type"""
        pass

    @staticmethod
    def shorten_text(text: str) -> str:
        """Shorten text to the first 100 symbols"""
        return f'{text.strip()[:100]}...'

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return (self.tags == other.tags and
                self.deck_name == other.deck_name)
