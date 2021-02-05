from typing import Union, List

import requests

from .card import Card


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
        request = self._create_request('version')

        try:
            requests.post(self._api_url, json=request)
        except requests.exceptions.ConnectionError:
            return False

        return True

    def add_cards(self, cards: List[Card]):
        for card in cards:
            self._add_card(card)
        print('All cards sent successfully!')
        print()

    def _add_card(self, card: Card):
        note_params = self._create_note_params(card)
        request_dict = self._create_request('addNote', note_params)

        # Send request to AnkiConnect
        response = requests.post(self._api_url, json=request_dict).json()

        # Show error message
        if response['result'] is None:
            card.print_card_info()
            print("ERROR: Can't create the card!")
            print(f'Reason: "{response["error"]}"')
            input('Press Enter to continue...')
            print()

    def _create_note_params(self, card: Card) -> dict:
        return {
            'note': {
                'deckName': card.deck_name,
                'modelName': self._note_type,
                'fields': {
                    self._front_field_name: card.front_converted,
                    self._back_field_name: card.back_converted
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
        }

    @staticmethod
    def _create_request(action: str, params: dict = None) -> dict:
        request = {'action': action, 'version': 6}
        if params is not None:
            request['params'] = params

        return request
