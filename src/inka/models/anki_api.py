from typing import Union, List, Any, Dict, Type

import requests
from requests import RequestException

from .config import Config
from .notes.basic_note import BasicNote
from .notes.cloze_note import ClozeNote
from .notes.note import Note
from ..exceptions import AnkiApiError


class AnkiApi:
    """Class for working with server created by Anki Connect"""

    def __init__(self, cfg: Config):
        self._cfg = cfg
        self._api_url = f'http://localhost:{cfg.get_option_value("anki_connect", "port")}'
        self._change_tag = 'changed'
        self._delete_tag = 'delete'

    def check_connection(self) -> bool:
        """Check connection with Anki Connect plugin"""
        try:
            self._send_request('version')
        except requests.exceptions.ConnectionError:
            return False

        return True

    def get_profiles(self) -> List[str]:
        """Get list of user profiles from Anki"""
        return self._send_request('getProfiles')

    def select_profile(self, profile: str) -> None:
        """Select profile in Anki"""
        params = {'name': profile}
        self._send_request('loadProfile', **params)

    def add_notes(self, notes: List[Union[BasicNote, ClozeNote]]) -> None:
        """Add new notes to Anki"""
        # Create decks that doesn't exist
        decks = {note.deck_name for note in notes}
        for deck in decks:
            self._create_deck(deck)

        # Send notes to Anki
        for note in notes:
            note_params = self._create_note_params(note)
            try:
                note.anki_id = self._send_request('addNote', note=note_params)
            except RequestException as e:
                raise AnkiApiError(str(e), note=note)

    def update_note_ids(self, notes: List[Union[BasicNote, ClozeNote]]) -> None:
        """Update incorrect or absent IDs of notes"""
        # Handle None
        note_ids = [note.anki_id if note.anki_id else -1
                    for note in notes]

        notes_info = self._send_request('notesInfo', notes=note_ids)
        for i, note in enumerate(notes):
            # Don't update ID if note with this ID exists
            if notes_info[i]:
                continue

            found_notes = self._send_request('findNotes', query=note.search_query)
            note.anki_id = found_notes[0] if found_notes else None

    def update_notes(self, notes: List[Union[BasicNote, ClozeNote]]) -> None:
        """Synchronize changes in notes with Anki"""
        # Get info about notes from Anki
        notes_info = self._send_request('notesInfo', notes=[note.anki_id for note in notes])

        for i, note in enumerate(notes):
            # If note wasn't found
            if not notes_info[i]:
                raise AnkiApiError(
                    f'note with ID {note.anki_id} was not found. '
                    f'You can update IDs on notes with the command "inka collect --update-ids path/to/file.md".'
                )

            # If note is staged for deletion
            # if self._delete_tag in notes_info[i]['tags']:
            #     note.to_delete = True
            #     continue

            # If note is marked as changed
            # if self._change_tag in notes_info[i]['tags']:
            #     # Convert updated note fields to markdown
            #     note.front_html = notes_info[i]['fields'][self._front_field_name]['value']
            #     note.back_html = notes_info[i]['fields'][self._back_field_name]['value']
            #     # converter.convert_note_to_md(note)
            #
            #     # Mark note as changed
            #     note.changed = True
            #     continue

            try:
                # Push changes from file to Anki
                note_params = self._create_note_params(note)
                note_params['id'] = note.anki_id
                self._send_request('updateNoteFields', note=note_params)
            except RequestException as e:
                raise AnkiApiError(str(e), note=note)

    def delete_notes(self, notes: List[Union[BasicNote, ClozeNote]]) -> None:
        """Delete notes from Anki"""
        self._send_request('deleteNotes',
                           notes=[note.anki_id for note in notes])

    def remove_change_tag_from_notes(self, notes: List[Union[BasicNote, ClozeNote]]) -> None:
        """Remove the tag which marks note as changed from notes in Anki"""
        self._send_request('removeTags',
                           notes=[note.anki_id for note in notes],
                           tags=self._change_tag)

    def fetch_note_type_styling(self, note_type: Type[Note]) -> str:
        """Get styling of note type that is used to add notes"""
        return self._send_request('modelStyling', modelName=note_type.get_anki_note_type(self._cfg))['css']

    def update_note_type_styling(self, note_type: Type[Note], new_styles: str) -> None:
        """Update styling of note type that is used to add notes"""
        params = {
            'model': {
                'name': note_type.get_anki_note_type(self._cfg),
                'css': new_styles
            }
        }
        self._send_request('updateModelStyling', **params)

    def fetch_note_type_templates(self, note_type: Type[Note]) -> Dict[str, Dict[str, str]]:
        """Get templates of note type"""
        return self._send_request('modelTemplates', modelName=note_type.get_anki_note_type(self._cfg))

    def update_note_type_templates(self, note_type: Type[Note], templates: Dict[str, Dict[str, str]]) -> None:
        """Update note type templates"""
        params = {
            'model': {
                'name': note_type.get_anki_note_type(self._cfg),
                'templates': templates
            }
        }
        self._send_request('updateModelTemplates', **params)

    def _create_deck(self, deck: str) -> Any:
        """Create deck in Anki if it doesn't exist"""
        params = {'deck': deck}
        return self._send_request('createDeck', **params)

    def _create_note_params(self, note: Union[BasicNote, ClozeNote]) -> dict:
        """Create dict with params required to add note to Anki"""
        return {
            'deckName': note.deck_name,
            'modelName': note.get_anki_note_type(self._cfg),
            'fields': note.get_html_fields(self._cfg),
            'options': {
                'allowDuplicate': False,
                'duplicateScope': None,
                'duplicateScopeOptions': {
                    'checkChildren': False
                }
            },
            'tags': note.tags,
        }

    def _send_request(self, action: str, **params) -> Any:
        """Send request to Anki Connect and return result"""
        request_dict = self._create_request(action, **params)
        response = requests.post(self._api_url, json=request_dict).json()

        if len(response) != 2:
            raise RequestException('response has an unexpected number of fields')
        if 'error' not in response:
            raise RequestException('response is missing required error field')
        if 'result' not in response:
            raise RequestException('response is missing required result field')
        if response['error'] is not None:
            raise RequestException(response['error'])

        return response['result']

    @staticmethod
    def _create_request(action: str, **params) -> dict:
        """Create request dictionary"""
        return {'action': action, 'version': 6, 'params': params}
