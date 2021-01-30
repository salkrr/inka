import pytest


def test_empty(fake_parser):
    card_substrings = fake_parser._get_card_substrings('')

    assert card_substrings == []


def test_one_card(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = [
        '1. Some question?\n'
        '\n'
        '> Answer'
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_without_empty_line_between_question_and_answer(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '> Answer'
    )
    expected = [
        '1. Some question?\n'
        '> Answer'
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_two_cards(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '2. Q\n'
        '\n'
        '> A'
    )
    expected = [
        ('1. Some question?\n'
         '\n'
         '> Answer\n'),
        ('2. Q\n'
         '\n'
         '> A')
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_two_cards_without_empty_line_between_answer_and_new_question(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '2. Q\n'
        '\n'
        '> A'
    )
    expected = [
        ('1. Some question?\n'
         '\n'
         '> Answer\n'),
        ('2. Q\n'
         '\n'
         '> A')
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_one_card_with_multiline_question(fake_parser):
    section = (
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
    expected = [
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_one_card_with_multiline_answer(fake_parser):
    section = (
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
    expected = [
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_one_card_with_multiline_question_and_answer(fake_parser):
    section = (
        'Deck: Abraham\n'
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
        '> And more to it'
    )
    expected = [
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
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected


def test_card_with_incorrect_question_syntax_ignored(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '>> Some question?\n'
        '\n'
        '> Answer\n'
    )

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == []


def test_card_with_incorrect_answer_syntax_ignored(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        'Answer\n'
    )

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == []


# TODO: fix the bug spotted by this test
@pytest.mark.skip('WIP')
def test_two_questions_one_answer(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '2. Another question\n'
        '\n'
        '> Answer'
    )
    expected = [
        '2. Another question\n'
        '\n'
        '> Answer'
    ]

    card_substrings = fake_parser._get_card_substrings(section)

    assert card_substrings == expected
