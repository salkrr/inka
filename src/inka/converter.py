import re
from typing import List

import mistune
from markdownify import markdownify

from .card import Card


def convert_cards_to_html(cards: List[Card]):
    """Convert front_md and back_md fields to html and write result into front_md and back_md fields"""
    for card in cards:
        # We delete '\n' before and after each html tag because Anki is rendering them as newlines
        card.front_html = re.sub(r'\n?(<.+?>)\n?',
                                 lambda tag_match: tag_match.group(1),
                                 mistune.html(card.front_md))
        card.back_html = re.sub(r'\n?(<.+?>)\n?',
                                lambda tag_match: tag_match.group(1),
                                mistune.html(card.back_md))


def convert_card_to_md(card: Card):
    """Convert front_html and back_html fields to markdown and write result into front_md and back_md fields"""
    # TODO: add options in config to specify heading_style and bullets style
    # We needed to remove '\n\n' at the end of strings because
    # this line brakes aren't needed for updating cards in file
    card.front_md = markdownify(card.front_html, heading_style='ATX', bullets='-').rstrip()
    card.back_md = markdownify(card.back_html, heading_style='ATX', bullets='-').rstrip()
