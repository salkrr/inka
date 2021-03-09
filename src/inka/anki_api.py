from typing import Union, List, Any

import click
import requests
from requests import RequestException

from . import converter
from .card import Card
from .util import escape_special_chars


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

    def select_profile(self, profile: str):
        """Select profile in Anki"""
        params = {'name': profile}
        self._send_request('loadProfile', **params)

    def add_cards(self, cards: List[Card]):
        """Add new cards to Anki"""
        # Create decks that doesn't exist
        decks = {card.deck_name for card in cards}
        for deck in decks:
            self._create_deck(deck)

        # Send cards to Anki
        for card in cards:
            note_params = self._create_note_params(card)
            try:
                card.anki_id = self._send_request('addNote', note=note_params)
            except RequestException as error:
                self._print_error_message(card, error)

    def update_card_ids(self, cards: List[Card]):
        """Update incorrect or absent IDs of cards"""
        # Handle None
        card_ids = [card.anki_id if card.anki_id else -1
                    for card in cards]

        cards_info = self._send_request('cardsInfo', cards=card_ids)
        for i, card in enumerate(cards):
            # Don't update ID if card with this ID exists
            if cards_info[i]:
                continue

            query = escape_special_chars(card.front_html)
            found_notes = self._send_request('findNotes', query=query)
            card.anki_id = found_notes[0] if found_notes else None

    def update_cards(self, cards: List[Card]):
        """Synchronize changes in cards with Anki"""
        # Get info about cards from Anki
        cards_info = self._send_request('notesInfo', notes=[card.anki_id for card in cards])

        for i, card in enumerate(cards):
            # If card wasn't found
            if not cards_info[i]:
                self._print_error_message(card, Exception(f'Card with ID {card.anki_id} was not found.'))
                continue

            # If card is staged for deletion
            if self._delete_tag in cards_info[i]['tags']:
                card.to_delete = True
                continue

            # If card is marked as changed
            if self._change_tag in cards_info[i]['tags']:
                # Convert updated card fields to markdown
                card.front_html = cards_info[i]['fields'][self._front_field_name]['value']
                card.back_html = cards_info[i]['fields'][self._back_field_name]['value']
                converter.convert_card_to_md(card)

                # Mark card as changed
                card.changed = True
                continue

            try:
                # Push changes from file to Anki
                note_params = self._create_note_params(card)
                note_params['id'] = card.anki_id
                self._send_request('updateNoteFields', note=note_params)
            except RequestException as e:
                # TODO: print error message with hint to '-u' flag
                self._print_error_message(card, e)

    def delete_cards(self, cards: List[Card]):
        """Delete cards from Anki"""
        self._send_request('deleteNotes',
                           notes=[card.anki_id for card in cards])

    def remove_change_mark_from_cards(self, cards: List[Card]):
        """Remove marking that card was changed from cards in Anki"""
        self._send_request('removeTags',
                           notes=[card.anki_id for card in cards],
                           tags=self._change_tag)

    def _create_deck(self, deck: str) -> Any:
        """Create deck in Anki if it doesn't exist"""
        params = {'deck': deck}
        return self._send_request('createDeck', **params)

    def _create_note_params(self, card: Card) -> dict:
        """Create dict with params required to add note to Anki"""
        return {
            'deckName': card.deck_name,
            'modelName': self._note_type,
            'fields': {
                self._front_field_name: card.front_html,
                self._back_field_name: card.back_html
            },
            'options': {
                'allowDuplicate': False,
                'duplicateScope': None,
                'duplicateScopeOptions': {
                    'checkChildren': False
                }
            },
            'tags': card.tags
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
    def _print_error_message(card: Card, error: Exception = None):
        # Card information
        click.secho('------------------------------------', fg='red')
        click.secho(f'Front: {card.front_md.strip()}', fg='red')
        click.secho(f'Back: {card.back_md.strip()}', fg='red')
        click.secho('------------------------------------', fg='red')

        # Error message
        if error is not None:
            click.secho(f'Error: "{error}"', fg='red')
        else:
            click.secho("Error: Can't create the card!", fg='red')
        input('Press Enter to continue...\n')
