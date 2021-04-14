import re
from typing import List

import mistune

from .card import Card
from .mathjax import plugin_mathjax

MD = mistune.create_markdown(plugins=['strikethrough', 'footnotes', 'table', plugin_mathjax])


def convert_cards_to_html(cards: List[Card]):
    """Convert front_md and back_md fields to html and write result into front_md and back_md fields"""
    for card in cards:
        card.front_html = convert_md_to_html(card.updated_front_md)
        card.back_html = convert_md_to_html(card.updated_back_md)


def convert_md_to_html(text: str) -> str:
    # We delete '\n' before and after each html tag because Anki is rendering them as newlines
    return re.sub(r'\n?(<.+?>)\n?',
                  lambda tag_match: tag_match.group(1),
                  MD(text))

# def convert_card_to_md(card: Card):
#     """Convert front_html and back_html fields to markdown and write result into front_md and back_md fields"""
#     # We needed to remove '\n\n' at the end of strings because
#     # this line brakes aren't needed for updating cards in file
#     card.front_md = markdownify(card.front_html, heading_style='ATX', bullets='-').rstrip()
#     card.back_md = markdownify(card.back_html, heading_style='ATX', bullets='-').rstrip()
