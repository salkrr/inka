from typing import Optional

from inka.models.notes.note import Note


class AnkiApiError(Exception):
    def __init__(self, message: str, note: Optional[Note] = None):
        super().__init__(message)
        self.note = note


class HighlighterError(Exception):
    pass
