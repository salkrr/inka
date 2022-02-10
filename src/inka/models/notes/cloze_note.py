from typing import Any, Callable, Dict, Iterable, List

from rich.table import Column, Table

from ..config import Config
from .note import Note


class ClozeNote(Note):
    """Cloze note type"""

    def __init__(
        self, text_md: str, tags: Iterable[str], deck_name: str, anki_id: int = None
    ):
        super().__init__(tags, deck_name, anki_id)
        self.raw_text_md = text_md
        self.updated_text_md = text_md  # With updated image links and cloze deletions
        self.text_html = ""

    @property
    def search_query(self) -> str:
        """Query to search for note in Anki"""
        return self.create_anki_search_query(self.text_html)

    def convert_fields_to_html(self, convert_func: Callable[[str], str]) -> None:
        """Convert note fields from markdown to html using provided function"""
        self.text_html = convert_func(self.updated_text_md)

    def update_fields_with(self, update_func: Callable[[str], str]) -> None:
        """Updates values of *updated* fields using provided function"""
        self.updated_text_md = update_func(self.updated_text_md)

    def get_raw_fields(self) -> List[str]:
        """Get list of all raw (as in file) fields of this note"""
        return [self.raw_text_md]

    def get_raw_question_field(self) -> str:
        """Get value of raw (as in file) question field"""
        return self.raw_text_md

    def get_html_fields(self, cfg: Config) -> Dict[str, str]:
        """Return dictionary with Anki field names as keys and html strings as values"""
        return {
            cfg.get_option_value("anki", "cloze_field"): self.text_html,
        }

    @staticmethod
    def get_anki_note_type(cfg: Config) -> str:
        """Get name of Anki note type"""
        return cfg.get_option_value("anki", "cloze_type")

    def __rich__(self) -> Table:
        """Table that is used to display info about note in case of error"""
        table = Table(
            Column("Field", justify="left", style="magenta"),
            Column("Value", justify="left", style="green"),
            title="[bold]Basic Note[bold]",
        )
        table.add_row("Text", self.raw_text_md, end_section=True)
        table.add_row("Tags", ", ".join(self.tags), end_section=True)
        table.add_row("Deck", self.deck_name, end_section=True)
        return table

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        return self.raw_text_md == other.raw_text_md

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(text_md={self.raw_text_md!r}, tags={self.tags!r}, "
            f"deck_name={self.deck_name!r}, anki_id={self.anki_id!r})"
        )
