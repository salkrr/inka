import pypandoc


class Converter:

    @staticmethod
    def convert_card(card):
        card.forward = Converter.convert_string(card.forward)
        card.backward = Converter.convert_string(card.backward)

    @staticmethod
    def convert_string(raw_str):
        args = ["--mathjax"]
        html_str = pypandoc.convert_text(raw_str, "html", extra_args=args, format="md")

        return html_str

