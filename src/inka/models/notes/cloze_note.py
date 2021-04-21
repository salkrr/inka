from typing import Iterable, Any, Callable, Dict

from .note import Note
from ..config import Config


class ClozeNote(Note):
    """Cloze note type"""

    def __init__(self, text_md: str, tags: Iterable[str], deck_name: str, anki_id: int = None):
        super().__init__(tags, deck_name, anki_id)
        self.raw_text_md = text_md
        self.updated_text_md = text_md  # With updated image links and cloze deletions
        self.text_html = None

    def convert_fields_to_html(self, convert_func: Callable) -> None:
        """Convert note fields from markdown to html using provided function"""
        self.text_html = convert_func(self.updated_text_md)

    def get_search_field(self) -> str:
        """Get field (with html) that will be used for search in Anki"""
        return self.text_html

    def get_raw_question_field(self) -> str:
        """Get value of question field"""
        return self.raw_text_md

    def get_html_fields(self, cfg: Config) -> Dict[str, str]:
        """Return dictionary with Anki field names as keys and html strings as values"""
        return {
            cfg.get_option_value('anki', 'cloze_field'): self.text_html,
        }

    def get_note_info(self) -> str:
        """String used to display info about note in case of error"""
        text_shortened = self.shorten_text(self.raw_text_md)
        info = 'Cloze Note\n'
        info += '--------------------------------------------------\n'
        info += f'Text: {text_shortened}\n'
        info += '--------------------------------------------------\n'
        return info

    @staticmethod
    def get_anki_note_type(cfg: Config) -> str:
        """Get name of Anki note type"""
        return cfg.get_option_value('anki', 'cloze_type')

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        return self.raw_text_md == other.raw_text_md

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(text_md={self.raw_text_md!r}, tags={self.tags!r}, '
            f'deck_name={self.deck_name!r}, anki_id={self.anki_id!r})'
        )
