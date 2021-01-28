import pytest


def test_no_question_raises_error(parser):
    text = 'Some text'

    with pytest.raises(AttributeError):
        parser._get_question(text)


def test_oneliner_question(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = parser._get_question(text)

    assert question == expected


def test_two_digit_question_prefix(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '12. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = parser._get_question(text)

    assert question == expected


def test_three_digit_question_prefix(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '123. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = parser._get_question(text)

    assert question == expected


def test_multiline_question(parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    )
    expected = 'Some question?\n\nMore info on question.\n\nAnd even more!'

    question = parser._get_question(text)

    assert question == expected

