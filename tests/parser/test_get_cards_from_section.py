import pytest

from src.inka.card import Card

test_cases = {
    'Deck: Abraham\n': [],

    ('Deck: Abraham\n'
     'Tags: some tags here'): [],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): [Card(front_md='Some question?',
                        back_md='Answer',
                        tags=[],
                        deck_name='Abraham')],

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): [Card(front_md='Some question?',
                        back_md='Answer',
                        tags=['one', 'two-three'],
                        deck_name='Abraham')],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer\n'
     '\n'
     '2. Q\n'
     '\n'
     '> A'): [Card(front_md='Some question?', back_md='Answer', tags=[], deck_name='Abraham'),
              Card(front_md='Q', back_md='A', tags=[], deck_name='Abraham')],

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer\n'
     '\n'
     '2. Q\n'
     '\n'
     '> A'): [Card(front_md='Some question?', back_md='Answer', tags=['one', 'two-three'], deck_name='Abraham'),
              Card(front_md='Q', back_md='A', tags=['one', 'two-three'], deck_name='Abraham')],

}


@pytest.mark.parametrize('section, expected', test_cases.items())
def test_get_cards_from_section(fake_parser, section, expected):
    cards = fake_parser._get_cards_from_section(section)

    assert cards == expected
