import mistune


class Converter:

    @classmethod
    def convert_cards(cls, cards_list):
        for card in cards_list:
            cls.convert_card(card)

    @classmethod
    def convert_card(cls, card):
        card.front_html = cls.convert_string(card.front_md)
        card.back_html = cls.convert_string(card.back_md)

    @classmethod
    def convert_string(cls, raw_str):
        return mistune.html(raw_str)
