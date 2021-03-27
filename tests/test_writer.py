import random
from pathlib import Path
from typing import List

import pytest

from src.inka.card import Card
from src.inka.parser import Parser
from src.inka.writer import Writer


@pytest.fixture
def file(tmp_path: Path) -> Path:
    """Temporary markdown file with cards"""
    file_path = tmp_path / 'file.md'
    with open(file_path, mode='wt', encoding='utf-8') as f:
        f.write(
            '---\n'
            '\n'
            'Deck: Abraham\n'
            '\n'
            'Tags: one two-three\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> First answer\n'
            '\n'
            '2. Another question\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!\n'
            '\n'
            '> Second answer\n'
            '> \n'
            '> Additional info\n'
            '> \n'
            '> And more to it\n'
            '\n'
            '---'
        )

    return file_path


@pytest.fixture
def cards(file: Path) -> List[Card]:
    """Cards from the temporary file with randomly generated ids"""
    parser = Parser(file, '')
    cards = parser.collect_cards()
    for card in cards:
        card.anki_id = random.randint(1000000000, 9999999999)

    return cards


@pytest.fixture
def writer(file: Path, cards: List[Card]) -> Writer:
    """Fake writer which uses temporary file"""
    return Writer(file, cards)


@pytest.fixture
def writer_with_ids(file: Path, cards: List[Card]) -> Writer:
    """Fake writer which uses temporary file and has IDs on cards"""
    writer = Writer(file, cards)
    writer.update_card_ids()
    return writer


def test_repr_method(writer, file, cards):
    expected = f'Writer(file_path={file!r}, cards={cards!r})'

    assert repr(writer) == expected


def test_update_ids_saves_to_file_system(writer, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.update_card_ids()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_update_ids_skips_card_if_it_was_not_found(writer, cards):
    writer._file_content = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer.update_card_ids()

    assert writer._file_content == expected


def test_update_ids_does_not_add_id_if_it_no_id_in_card(writer, cards):
    cards[0].anki_id = None
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer.update_card_ids()

    assert writer._file_content == expected


def test_update_ids_removes_id_from_file_if_card_object_has_no_id(writer, cards):
    writer._file_content = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )
    cards[0].anki_id = None

    writer.update_card_ids()

    assert writer._file_content == expected


def test_update_ids_writes_id_before_question(writer, cards):
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer.update_card_ids()

    assert writer._file_content == expected


def test_updates_id_if_another_is_written(writer, cards):
    writer._file_content = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:-12395124812321-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer.update_card_ids()

    assert writer._file_content == expected


def test_update_card_fields_saves_to_file_system(writer, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.update_card_fields()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_update_card_fields_skips_not_changed_cards(writer_with_ids, cards):
    cards[0].changed = False
    cards[0].front_md = 'Amazing new text'
    cards[0].back_md = 'Amazing new answer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer_with_ids.update_card_fields()

    assert writer_with_ids._file_content == expected


def test_updates_question_field(writer_with_ids, cards):
    cards[0].changed = True
    cards[0].front_md = 'Amazing new text'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        f'1. {cards[0].front_md}\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer_with_ids.update_card_fields()

    assert writer_with_ids._file_content == expected


def test_updates_multiline_question_field(writer_with_ids, cards):
    cards[1].changed = True
    cards[1].front_md = 'Something new\n\nhere'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        f'2. {cards[1].front_md}\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer_with_ids.update_card_fields()

    assert writer_with_ids._file_content == expected


def test_updates_answer_field(writer_with_ids, cards):
    cards[0].changed = True
    cards[0].back_md = 'New answer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        f'> {cards[0].back_md}\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer_with_ids.update_card_fields()

    assert writer_with_ids._file_content == expected


def test_updates_multiline_answer_field(writer_with_ids, cards):
    cards[1].changed = True
    cards[1].back_md = 'New\n\nmultiline\n\nanswer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{cards[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> New\n'
        '> multiline\n'
        '> answer\n'
        '\n'
        '---'
    )

    writer_with_ids.update_card_fields()

    assert writer_with_ids._file_content == expected


def test_delete_saves_changes_to_file_system(writer, cards, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.delete_cards()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_delete_skips_cards_that_are_not_marked_for_deletion(writer_with_ids, cards):
    cards[0].to_delete = False
    cards[1].to_delete = False
    expected = writer_with_ids._file_content

    writer_with_ids.delete_cards()

    assert writer_with_ids._file_content == expected


def test_deletes_card_marked_for_deletion(writer_with_ids, cards):
    cards[0].to_delete = True
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '\n'
        f'<!--ID:{cards[1].anki_id}-->\n'
        '2. Another question\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        '---'
    )

    writer_with_ids.delete_cards()

    assert writer_with_ids._file_content == expected


def test_deletes_multiple_cards_marked_for_deletion(writer_with_ids, cards):
    cards[0].to_delete = True
    cards[1].to_delete = True
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '\n'
        '\n'
        '---'
    )

    writer_with_ids.delete_cards()

    assert writer_with_ids._file_content == expected
