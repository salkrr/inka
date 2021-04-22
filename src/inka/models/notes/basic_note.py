from typing import Iterable, Any, Callable, Dict, List

from .note import Note
from ..config import Config


class BasicNote(Note):
    """Front/Back note type"""

    def __init__(self, front_md: str, back_md: str, tags: Iterable[str], deck_name: str, anki_id: int = None):
        super().__init__(tags, deck_name, anki_id)
        self.raw_front_md = front_md
        self.raw_back_md = back_md
        self.updated_front_md = front_md  # With updated image links
        self.updated_back_md = back_md  # With updated image links
        self.front_html = None
        self.back_html = None

    def convert_fields_to_html(self, convert_func: Callable[[str], str]) -> None:
        """Convert note fields from markdown to html using provided function"""
        self.front_html = convert_func(self.updated_front_md)
        self.back_html = convert_func(self.updated_back_md)

    def update_fields_with(self, update_func: Callable[[str], str]) -> None:
        """Updates values of *updated* fields using provided function"""
        self.updated_front_md = update_func(self.updated_front_md)
        self.updated_back_md = update_func(self.updated_back_md)

    def get_search_field(self) -> str:
        """Get field (with html) that will be used for search in Anki"""
        return self.front_html

    def get_raw_fields(self) -> List[str]:
        """Get list of all raw (as in file) fields of this note"""
        return [self.raw_front_md, self.raw_back_md]

    def get_raw_question_field(self) -> str:
        """Get value of raw (as in file) question field"""
        return self.raw_front_md

    def get_html_fields(self, cfg: Config) -> Dict[str, str]:
        """Return dictionary with Anki field names as keys and html strings as values"""
        return {
            cfg.get_option_value('anki', 'front_field'): self.front_html,
            cfg.get_option_value('anki', 'back_field'): self.back_html
        }

    def get_note_info(self) -> str:
        """String used to display info about note in case of error"""
        front_shortened = self.shorten_text(self.raw_front_md)
        back_shortened = self.shorten_text(self.raw_back_md)
        info = 'Basic Note\n'
        info += '--------------------------------------------------\n'
        info += f'Front: {front_shortened}\n'
        info += f'Back: {back_shortened}\n'
        info += '--------------------------------------------------\n'
        return info

    @staticmethod
    def get_anki_note_type(cfg: Config) -> str:
        """Get name of Anki note type"""
        return cfg.get_option_value('anki', 'basic_type')

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        return (self.raw_front_md == other.raw_front_md and
                self.raw_back_md == other.raw_back_md)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(front_md={self.raw_front_md!r}, back_md={self.raw_back_md!r}, '
            f'tags={self.tags!r}, deck_name={self.deck_name!r}, anki_id={self.anki_id!r})'
        )
