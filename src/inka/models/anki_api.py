from typing import Union, List, Any, Dict

import click
import requests
from requests import RequestException

from .notes.basic_note import BasicNote
from ..util import create_anki_search_query


class AnkiApi:
    """Class for working with server created by Anki Connect"""

    def __init__(
            self,
            port: Union[str, int],
            note_type: str,
            front_field_name: str,
            back_field_name: str
    ):
        self._api_url = f'http://localhost:{port}'
        self._note_type = note_type
        self._front_field_name = front_field_name
        self._back_field_name = back_field_name
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

    def add_notes(self, notes: List[BasicNote]) -> None:
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
            except RequestException as error:
                self._print_error_message(note, error)

    def update_note_ids(self, notes: List[BasicNote]) -> None:
        """Update incorrect or absent IDs of notes"""
        # Handle None
        note_ids = [note.anki_id if note.anki_id else -1
                    for note in notes]

        notes_info = self._send_request('notesInfo', notes=note_ids)
        for i, note in enumerate(notes):
            # Don't update ID if note with this ID exists
            if notes_info[i]:
                continue

            query = create_anki_search_query(note.front_html)
            found_notes = self._send_request('findNotes', query=query)
            note.anki_id = found_notes[0] if found_notes else None

    def update_notes(self, notes: List[BasicNote]) -> None:
        """Synchronize changes in notes with Anki"""
        # Get info about notes from Anki
        notes_info = self._send_request('notesInfo', notes=[note.anki_id for note in notes])

        for i, note in enumerate(notes):
            # If note wasn't found
            if not notes_info[i]:
                self._print_error_message(note, Exception(f'Card with ID {note.anki_id} was not found.'))
                continue

            # If note is staged for deletion
            if self._delete_tag in notes_info[i]['tags']:
                note.to_delete = True
                continue

            # If note is marked as changed
            if self._change_tag in notes_info[i]['tags']:
                # Convert updated note fields to markdown
                note.front_html = notes_info[i]['fields'][self._front_field_name]['value']
                note.back_html = notes_info[i]['fields'][self._back_field_name]['value']
                # converter.convert_note_to_md(note)

                # Mark note as changed
                note.changed = True
                continue

            try:
                # Push changes from file to Anki
                note_params = self._create_note_params(note)
                note_params['id'] = note.anki_id
                self._send_request('updateNoteFields', note=note_params)
            except RequestException as e:
                # TODO: print error message with hint to '-u' flag
                self._print_error_message(note, e)

    def delete_notes(self, notes: List[BasicNote]) -> None:
        """Delete notes from Anki"""
        self._send_request('deleteNotes',
                           notes=[note.anki_id for note in notes])

    def remove_change_tag_from_notes(self, notes: List[BasicNote]) -> None:
        """Remove the tag which marks note as changed from notes in Anki"""
        self._send_request('removeTags',
                           notes=[note.anki_id for note in notes],
                           tags=self._change_tag)

    def fetch_note_type_styling(self) -> str:
        """Get styling of note type that is used to add notes"""
        return self._send_request('modelStyling', modelName=self._note_type)['css']

    def update_note_type_styling(self, new_styles: str) -> None:
        """Update styling of note type that is used to add notes"""
        params = {
            'model': {
                'name': self._note_type,
                'css': new_styles
            }
        }
        self._send_request('updateModelStyling', **params)

    def fetch_note_type_templates(self) -> Dict[str, Dict[str, str]]:
        """Get fields of note type"""
        return self._send_request('modelTemplates', modelName=self._note_type)

    def update_note_type_templates(self, templates: Dict[str, Dict[str, str]]) -> None:
        """Update note type"""
        params = {
            'model': {
                'name': self._note_type,
                'templates': templates
            }
        }
        self._send_request('updateModelTemplates', **params)

    def _create_deck(self, deck: str) -> Any:
        """Create deck in Anki if it doesn't exist"""
        params = {'deck': deck}
        return self._send_request('createDeck', **params)

    def _create_note_params(self, note: BasicNote) -> dict:
        """Create dict with params required to add note to Anki"""
        return {
            'deckName': note.deck_name,
            'modelName': self._note_type,
            'fields': {
                self._front_field_name: note.front_html,
                self._back_field_name: note.back_html
            },
            'options': {
                'allowDuplicate': False,
                'duplicateScope': None,
                'duplicateScopeOptions': {
                    'checkChildren': False
                }
            },
            'tags': note.tags
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

    @staticmethod
    def _print_error_message(note: BasicNote, error: Exception = None) -> None:
        # Note information
        click.secho('------------------------------------', fg='red')
        click.secho(f'Front: {note.raw_front_md.strip()}', fg='red')
        click.secho(f'Back: {note.raw_back_md.strip()}', fg='red')
        click.secho('------------------------------------', fg='red')

        # Error message
        if error is not None:
            click.secho(f'Error: "{error}"', fg='red')
        else:
            click.secho("Error: Can't create the card!", fg='red')
        input('Press Enter to continue...\n')
