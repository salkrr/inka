import pytest

test_cases = {
    '': [],

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): [
        '1. Some question?\n'
        '\n'
        '> Answer'
    ],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '> Answer'): [
        '1. Some question?\n'
        '> Answer'
    ],

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
     '> A'): [
        ('1. Some question?\n'
         '\n'
         '> Answer\n'),
        ('2. Q\n'
         '\n'
         '> A')
    ],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer\n'
     '2. Q\n'
     '\n'
     '> A'): [
        ('1. Some question?\n'
         '\n'
         '> Answer\n'),
        ('2. Q\n'
         '\n'
         '> A')
    ],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     'More info on question.\n'
     '\n'
     'And even more!'
     '\n'
     '> Answer'): [
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    ],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer\n'
     '> \n'
     '> Additional info\n'
     '> \n'
     '> And more to it'): [
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     'More info on question.\n'
     '\n'
     'And even more!'
     '\n'
     '> Answer\n'
     '> \n'
     '> Additional info\n'
     '> \n'
     '> And more to it'): [
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ],

    ('Deck: Abraham\n'
     '\n'
     '>> Some question?\n'
     '\n'
     '> Answer\n'): [],

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     'Answer\n'): [],

    # TODO: fix the bug spotted by this test
    # ('Deck: Abraham\n'
    #  '\n'
    #  'Tags: one two-three\n'
    #  '\n'
    #  '1. Some question?\n'
    #  '\n'
    #  '2. Another question\n'
    #  '\n'
    #  '> Answer'): [
    #     '2. Another question\n'
    #     '\n'
    #     '> Answer'
    # ],

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '<!--ID:123456-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): [
        '<!--ID:123456-->\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    ],

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '<!--ID:123456-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer\n'
     '\n'
     '<!--ID:581925-->\n'
     '2. Q\n'
     '\n'
     '> A'): [
        ('<!--ID:123456-->\n'
         '1. Some question?\n'
         '\n'
         '> Answer\n'),
        ('<!--ID:581925-->\n'
         '2. Q\n'
         '\n'
         '> A')
    ],

}


@pytest.mark.parametrize('section, expected', test_cases.items())
def test_get_card_substrings(fake_parser, section, expected):
    card_substrings = fake_parser.get_card_substrings(section)

    assert card_substrings == expected
