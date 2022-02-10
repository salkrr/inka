# Parts of code were impudently borrowed from AnkiConnect(https://github.com/FooSoft/anki-connect)
# and apy (https://github.com/lervag/apy) projects. Thanks to all their developers.

import os
from typing import Dict, Iterable, List, Type

import anki
import anki.collection
import anki.consts
import anki.errors
import anki.models
import anki.notes
import aqt

from ..exceptions import AnkiApiError
from .config import Config
from .notes.note import Note


class AnkiApi:
    """Class for working with Anki collection"""

    def __init__(self, cfg: Config, anki_path: str):
        self._cfg = cfg

        # Check correctness of the anki path
        meta_path = os.path.join(anki_path, "prefs21.db")
        if not os.path.exists(meta_path):
            raise AnkiApiError(f'incorrect path to Anki folder: "{anki_path}"')

        # Initialize profile manager to get access to profile and database actions
        self._profile_manager = aqt.ProfileManager(anki_path)
        self._profile_manager.setupMeta()

    def get_profiles(self) -> List[str]:
        """Get list of user profiles from Anki"""
        return self._profile_manager.profiles()

    def load_collection(self, profile: str) -> None:
        """Select profile in Anki and load collection"""
        # opening collection changes current directory so
        # we need to rollback it to initial
        initial_dir = os.getcwd()

        try:
            self._profile_manager.load(profile)
            self._collection = anki.collection.Collection(
                self._profile_manager.collectionPath()
            )
        except anki.errors.DBError:
            raise AnkiApiError(
                "the collection is open in Anki. "
                "You need to either close Anki or switch to a different profile."
            )

        os.chdir(initial_dir)

    def sync(self):
        """Sync collection to AnkiWeb"""
        # todo: handle case when to sync we need user decision (download or upload)
        auth = self._profile_manager.sync_auth()
        if auth is None:
            raise AnkiApiError("Isn't authenticated with AnkiWeb")

        self._collection.save(trx=False)

        # Perform main sync
        try:
            self._collection.sync_collection(auth)
        except anki.errors.NetworkError:
            raise AnkiApiError("Please check your internet connection")

        # Perform media sync
        initial_dir = os.getcwd()
        os.chdir(self._collection.media.dir())
        self._collection.sync_media(auth)
        os.chdir(initial_dir)

    def add_note(self, note: Note) -> int:
        model = self._collection.models.by_name(note.get_anki_note_type(self._cfg))
        anki_note = anki.notes.Note(self._collection, model)
        anki_note.tags = list(note.tags)
        anki_note.fields = list(note.get_html_fields(self._cfg).values())

        if anki_note.dupeOrEmpty():
            raise AnkiApiError("duplicate! Note wasn't added.", note=note)

        # gets id of the deck. if deck doesn't exist - it will be created.
        deck_id = self._collection.decks.id(note.deck_name, create=True)
        if not deck_id:
            raise AnkiApiError(f"the deck {note.deck_name} couldn't be created.")

        self._collection.add_note(anki_note, deck_id)
        return anki_note.id

    def update_note_ids(self, notes: Iterable[Note]) -> None:
        """Update incorrect or absent IDs of notes"""
        for note in notes:
            # Update id only if note with this id doesn't exist
            try:
                note_id = anki.collection.NoteId(note.anki_id if note.anki_id else -1)
                self._collection.get_note(note_id)
            except anki.errors.NotFoundError:
                found_notes = self._collection.find_notes(note.search_query)
                note.anki_id = found_notes[0] if found_notes else None

    def update_note(self, note: Note) -> None:
        """Synchronize changes in notes with Anki"""
        try:
            note_id = anki.collection.NoteId(note.anki_id if note.anki_id else -1)
            anki_note = self._collection.get_note(note_id)
        except anki.errors.NotFoundError:
            raise AnkiApiError(
                f"note with ID {note.anki_id} was not found. "
                f'You can update IDs on notes with the command "inka collect --update-ids path/to/file.md".'
            )

        for field, value in note.get_html_fields(self._cfg).items():
            if field in anki_note:
                anki_note[field] = value
        anki_note.flush()

    def fetch_note_types(self) -> List[str]:
        """Get list of names of the existing note types"""
        return [n.name for n in self._collection.models.all_names_and_ids()]

    def create_note_type(
        self,
        name: str,
        fields: List[str],
        css: str,
        card_templates: List[Dict[str, str]],
        is_cloze: bool,
    ) -> None:
        """Create new note type"""
        model = self._collection.models.new(name)
        if is_cloze:
            model["type"] = anki.consts.MODEL_CLOZE

        # Create fields and add them to Note
        for field in fields:
            model_field = self._collection.models.new_field(field)
            self._collection.models.add_field(model, model_field)

        # Add shared css to model if exists. Use default otherwise
        if css:
            model["css"] = css

        # Generate new card template(s)
        counter = 1
        for card in card_templates:
            card_name = "Card " + str(counter)
            if "Name" in card:
                card_name = card["Name"]

            tmpl = self._collection.models.new_template(card_name)
            tmpl["qfmt"] = card["Front"]
            tmpl["afmt"] = card["Back"]
            self._collection.models.add_template(model, tmpl)
            counter += 1

        self._collection.models.add(model)

    def fetch_note_type_styling(self, note_type: Type[Note]) -> str:
        """Get styling of note type that is used to add notes"""
        return self._get_model(note_type)["css"]

    def update_note_type_styling(self, note_type: Type[Note], new_styles: str) -> None:
        """Update styling of the note type in Anki"""
        anki_model = self._get_model(note_type)
        anki_model["css"] = new_styles
        self._collection.models.update_dict(anki_model)

    def fetch_note_type_templates(
        self, note_type: Type[Note]
    ) -> Dict[str, Dict[str, str]]:
        """Get templates of note type"""
        model = self._get_model(note_type)

        templates = {}
        for template in model["tmpls"]:
            templates[template["name"]] = {
                "Front": template["qfmt"],
                "Back": template["afmt"],
            }

        return templates

    def update_note_type_templates(
        self, note_type: Type[Note], templates: Dict[str, Dict[str, str]]
    ) -> None:
        """Update note type templates"""
        anki_model = self._get_model(note_type)

        for anki_template in anki_model["tmpls"]:
            template = templates.get(anki_template["name"])
            if template:
                qfmt = template.get("Front")
                if qfmt:
                    anki_template["qfmt"] = qfmt

                afmt = template.get("Back")
                if afmt:
                    anki_template["afmt"] = afmt

        self._collection.models.update_dict(anki_model)

    def close(self):
        """Save and close the collection."""
        self._collection.close()

    def _get_model(self, note_type: Type[Note]) -> anki.models.NoteType:
        model_name = note_type.get_anki_note_type(self._cfg)
        anki_model = self._collection.models.by_name(model_name)
        if not anki_model:
            raise AnkiApiError(f"couldn't get note type {model_name} from Anki!")

        return anki_model
