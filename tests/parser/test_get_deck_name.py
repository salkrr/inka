import pytest

test_cases = {
    ('1. Question?\n'
     '\n'
     'Answer\n'): 'Default',

    ('Deck: yolo\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): 'yolo',

    ('Deck: Very Long Deck Name\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): 'Very Long Deck Name',

    ('1. Question?\n'
     '\n'
     'Answer\n'
     '\n'
     'Deck: yolo\n'
     '\n'
     '2. Q?\n'
     '\n'
     'A\n'): 'yolo',

    ('Some text; Deck: yolo\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): 'Default',

}

test_cases_error = [
    ('Some text; Deck: yolo\n'
     '1. Question?\n'
     '\n'
     'Answer\n'),

    ('Deck: Abraham\n'
     '1. Question?\n'
     '\n'
     'Deck: Default\n'
     'Answer\n'),

    ('1. Question?\n'
     '\n'
     'Answer\n'),

    ('Deck:\n'
     '1. Question?\n'
     '\n'
     'Answer\n'),

    ('Deck:   \n'
     '1. Question?\n'
     '\n'
     'Answer\n')
]


@pytest.mark.parametrize('section, expected', test_cases.items())
def test_get_deck_name(fake_parser, section, expected):
    fake_parser._default_deck = 'Default'

    deck = fake_parser._get_deck_name(section)

    assert expected == deck


@pytest.mark.parametrize('section', test_cases_error)
def test_get_deck_name_raises_error(fake_parser, section):
    with pytest.raises(ValueError):
        fake_parser._get_deck_name(section)
