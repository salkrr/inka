from typing import Union, List, Any

import requests
from requests import RequestException

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
        """Add list of cards to Anki"""
        # Create decks that doesn't exist
        decks = {card.deck_name for card in cards}
        for deck in decks:
            self._create_deck(deck)

        for card in cards:
            if card.anki_id:
                self._update_card(card)
            else:
                self._add_card(card)

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

    def _create_deck(self, deck: str) -> Any:
        """Create deck in Anki if it doesn't exist"""
        params = {'deck': deck}
        return self._send_request('createDeck', **params)

    def _update_card(self, card: Card):
        """Update existing card with changes from file"""
        note_params = self._create_note_params(card)
        note_params['id'] = card.anki_id

        try:
            self._send_request('updateNoteFields', note=note_params)
        except RequestException as error:
            # If card doesn't exist, create new one
            # TODO: print error message with hint to '-u' flag
            self._add_card(card)

    def _add_card(self, card: Card):
        """Add card to Anki and update it's ID"""
        note_params = self._create_note_params(card)
        try:
            card.anki_id = self._send_request('addNote', note=note_params)
        except RequestException as error:
            self._print_error_message(card, error)

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
        # TODO: change to click.secho with red color
        print("ERROR: Can't create the card!")

        # Card information
        print('------------------------------------')
        print(f'Front: {card.front_md.strip()}')
        print(f'Back: {card.back_md.strip()}')
        print('------------------------------------')

        # Error message
        if error is not None:
            # TODO: change to str(error)
            print(f'Reason: "{error.args[0]}"')
        input('Press Enter to continue...\n')
