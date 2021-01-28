import pytest


def test_section_without_deck_name_field(parser):
    section = (
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_deck_name(section)


def test_section_with_empty_deck_name_field(parser):
    section = (
        'Deck:\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_deck_name(section)


def test_section_with_only_whitespace_deck_name_field(parser):
    section = (
        'Deck:   \n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_deck_name(section)


def test_section_with_not_empty_deck_name_field(parser):
    section = (
        'Deck: yolo\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = 'yolo'

    deck_name = parser._get_deck_name(section)

    assert deck_name == expected


def test_section_with_deck_name_field_with_multiple_words(parser):
    section = (
        'Deck: Very Long Deck Name\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = 'Very Long Deck Name'

    deck_name = parser._get_deck_name(section)

    assert deck_name == expected


def test_section_with_deck_name_field_not_on_top(parser):
    section = (
        '1. Question?\n'
        '\n'
        'Answer\n'
        '\n'
        'Deck: yolo\n'
        '\n'
        '2. Q?\n'
        '\n'
        'A\n'
    )
    expected = 'yolo'

    deck_name = parser._get_deck_name(section)

    assert deck_name == expected


def test_section_with_deck_name_field_inline(parser):
    section = (
        'Some text; Deck: yolo\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_deck_name(section)


def test_section_with_multiple_deck_name_fields(parser):
    section = (
        'Deck: Abraham\n'
        '1. Question?\n'
        '\n'
        'Deck: Default\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_deck_name(section)
