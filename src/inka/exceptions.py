from inka.models.notes.note import Note


class AnkiApiError(Exception):
    def __init__(self, message: str, note: Note = None):
        super().__init__(message)
        self.note = note


class HighlighterError(Exception):
    pass
