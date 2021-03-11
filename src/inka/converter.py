from typing import List

import mistune
from markdownify import markdownify

from .card import Card


def convert_cards_to_html(cards: List[Card]):
    """Convert front_md and back_md fields to html and write result into front_md and back_md fields """
    for card in cards:
        # rstrip() is needed because mistune (for some reason) adds \n at the end of the string
        card.front_html = mistune.html(card.front_md).replace('\n', '')
        card.back_html = mistune.html(card.back_md).replace('\n', '')


def convert_card_to_md(card: Card):
    f"""Convert front_html and back_html fields to markdown and write result into front_md and back_md fields """
    # TODO: add options in config to specify heading_style and bullets style
    # rstrip() is needed to remove \n\n at the end because they interfere when we updating cards in file
    card.front_md = markdownify(card.front_html, heading_style='ATX', bullets='-').rstrip()
    # in answer we need \n for newline instead of \n\n
    card.back_md = markdownify(card.back_html, heading_style='ATX', bullets='-').rstrip().replace('\n\n', '\n')
