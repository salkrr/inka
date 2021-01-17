import requests


class AnkiApi:
    note_type = "Basic"
    front_field_name = "Front"
    back_field_name = "Back"
    api_url = "http://localhost:8765"

    @staticmethod
    def add_cards(cards_list):
        # TODO
        # Use addNotes api call
        for card in cards_list:
            AnkiApi.add_card(card)

        print("All cards sent successfully!")

    @classmethod
    def add_card(cls, card):
        note_dict = cls.create_note_dict(card)
        request_dict = cls.create_base_dict()
        request_dict["action"] = "addNote"
        request_dict["params"]["note"] = note_dict

        # Send request to AnkiConnect
        response = requests.post(cls.api_url, json=request_dict)

        response_json = response.json()

        # Show error message
        if response_json['result'] is None:
            card.print_card_info()
            print("ERROR: Can't create the card!")
            print(f'Reason: "{response_json["error"]}"')
            input("Press Enter to continue...")
            print()

    @classmethod
    def create_note_dict(cls, card):
        return {
            "deckName": card.deck_name,
            "modelName": cls.note_type,
            "fields": {
                cls.front_field_name: card.front_converted,
                cls.back_field_name: card.back_converted
            },
            "options": {
                "allowDuplicate": False,
                "duplicateScope": None,
                "duplicateScopeOptions": {
                    "checkChildren": False
                }
            },
            "tags": card.tags
        }

    @classmethod
    def create_base_dict(cls):
        return {"action": "", "version": 6, "params": {}}
