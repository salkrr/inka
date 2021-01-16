import mistune


class Converter:

    @classmethod
    def convert_cards(cls, cards_list):
        for card in cards_list:
            cls.convert_card(card)

    @classmethod
    def convert_card(cls, card):
        card.front_converted = cls.convert_string(card.front_raw)
        card.back_converted = cls.convert_string(card.back_raw)

    @classmethod
    def convert_string(cls, raw_str):
        return mistune.html(raw_str)
