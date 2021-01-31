class Card:
    def __init__(self, front, back, tags, deck_name):
        self.front_raw = front
        self.back_raw = back
        self.front_converted = None
        self.back_converted = None
        self.tags = tags
        self.deck_name = deck_name

    def print_card_info(self):
        print('------------------------------------')
        print(f'Front: {self.front_raw.strip()}')
        print(f'Back: {self.back_raw.strip()}')
        print(f'Tags: {self.tags}')
        print(f'Deck: {self.deck_name}')
        print('------------------------------------')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (self.front_raw == other.front_raw and
                self.back_raw == other.back_raw and
                self.tags == other.tags and
                self.deck_name == other.deck_name)
