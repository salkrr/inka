from src.inka.card import Card


def test_section_with_only_deck_field(fake_parser):
    section = (
        'Deck: Abraham\n'
    )

    cards = fake_parser._get_cards_from_section(section)

    assert cards == []


def test_section_with_only_deck_and_tags_fields(fake_parser):
    section = (
        'Deck: Abraham\n'
        'Tags: some tags here'
    )

    cards = fake_parser._get_cards_from_section(section)

    assert cards == []


def test_one_card_without_tags(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = [Card(front='Some question?',
                     back='Answer',
                     tags=[],
                     deck_name='Abraham')]

    cards = fake_parser._get_cards_from_section(section)

    assert cards == expected


def test_one_card_with_tags(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = [Card(front='Some question?',
                     back='Answer',
                     tags=['one', 'two-three'],
                     deck_name='Abraham')]

    cards = fake_parser._get_cards_from_section(section)

    assert cards == expected


def test_two_cards_without_tags(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '2. Q\n'
        '\n'
        '> A'
    )
    expected = [Card(front='Some question?', back='Answer', tags=[], deck_name='Abraham'),
                Card(front='Q', back='A', tags=[], deck_name='Abraham')]

    cards = fake_parser._get_cards_from_section(section)

    assert cards == expected


def test_two_cards_with_tags(fake_parser):
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
    expected = [Card(front='Some question?', back='Answer', tags=['one', 'two-three'], deck_name='Abraham'),
                Card(front='Q', back='A', tags=['one', 'two-three'], deck_name='Abraham')]

    cards = fake_parser._get_cards_from_section(section)

    assert cards == expected
