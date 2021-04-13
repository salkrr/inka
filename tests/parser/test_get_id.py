import pytest

test_cases = {
    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '<!--ID:1235523-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): 1235523,

    ('<!--ID:215321-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): 215321,

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): None,

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '<!--ID:-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): None,

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     f'<!--ID:123a-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): None
}


@pytest.mark.parametrize('text, expected', test_cases.items())
def test_get_id(fake_parser, text, expected):
    assert fake_parser.get_id(text) == expected
