import pypandoc


class Converter:

    @classmethod
    def convert_cards(cls, cards_list):
        for card in cards_list:
            cls.convert_card(card)

    @classmethod
    def convert_card(cls, card):
        card.front = cls.convert_string(card.front)
        card.back = cls.convert_string(card.back)

    @staticmethod
    def convert_string(raw_str):
        args = ["--mathjax"]
        html_str = pypandoc.convert_text(raw_str, "html", extra_args=args, format="md")

        return html_str

