import requests

from .card import Card


class AnkiApi:
    _note_type = 'Basic'
    _front_field_name = 'Front'
    _back_field_name = 'Back'
    _api_url = 'http://localhost:8765'

    @staticmethod
    def add_cards(cards_list):
        for card in cards_list:
            AnkiApi._add_card(card)
        print('All cards sent successfully!')
        print()

    @classmethod
    def _add_card(cls, card: Card):
        note_params = cls._create_note_params(card)
        request_dict = cls._create_request('addNote', note_params)

        # Send request to AnkiConnect
        response = requests.post(cls._api_url, json=request_dict).json()

        # Show error message
        if response['result'] is None:
            card.print_card_info()
            print("ERROR: Can't create the card!")
            print(f'Reason: "{response["error"]}"')
            input('Press Enter to continue...')
            print()

    @classmethod
    def _create_note_params(cls, card: Card) -> dict:
        return {
            'note': {
                'deckName': card.deck_name,
                'modelName': cls._note_type,
                'fields': {
                    cls._front_field_name: card.front_converted,
                    cls._back_field_name: card.back_converted
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

    @classmethod
    def _create_request(cls, action: str, params: dict) -> dict:
        return {'action': action, 'version': 6, 'params': params}
