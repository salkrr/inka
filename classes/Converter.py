import pypandoc


class Converter:

    @staticmethod
    def convert_card(card):
        card.front = Converter.convert_string(card.front)
        card.back = Converter.convert_string(card.back)

    @staticmethod
    def convert_string(raw_str):
        args = ["--mathjax"]
        html_str = pypandoc.convert_text(raw_str, "html", extra_args=args, format="md")

        return html_str

