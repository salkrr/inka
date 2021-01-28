import pytest


def test_no_answer_raises_error(parser):
    text = 'Some text'

    with pytest.raises(AttributeError):
        parser._get_answer(text)


def test_oneliner_answer(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Some answer'
    )
    expected = 'Some answer'

    answer = parser._get_answer(text)

    assert answer == expected


def test_multiline_answer(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    )
    expected = 'Answer\n\nAdditional info\n\nAnd more to it'

    answer = parser._get_answer(text)

    assert answer == expected


def test_answer_prefix_inside_answer(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> > Answer\n'
    )
    expected = '> Answer'

    answer = parser._get_answer(text)

    assert answer == expected
