import random
from pathlib import Path
from typing import List

import pytest

from src.inka.card import Card
from src.inka.parser import Parser
from src.inka.writer import Writer


@pytest.fixture
def file(tmp_path) -> Path:
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
            '> Second answer\n'
            '\n'
            '---'
        )

    return file_path


@pytest.fixture
def cards(file: Path) -> List[Card]:
    """Cards from the temporary file with randomly generated ids"""
    parser = Parser(file, '', '')
    cards = parser.collect_cards()
    for card in cards:
        card.anki_id = random.randint(1000000000, 9999999999)

    return cards


@pytest.fixture
def fake_writer(file: Path, cards: List[Card]) -> Writer:
    """Fake writer which uses temporary file"""
    return Writer(file, cards)


def test_saving(fake_writer, file):
    expected = 'Some string'
    fake_writer._file_content = expected

    fake_writer._save()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_does_not_add_id_if_it_no_id_in_card(fake_writer, file, cards):
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
        '> Second answer\n'
        '\n'
        '---'
    )

    fake_writer.write_card_ids()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_writes_id_before_question(fake_writer, file, cards):
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
        '> Second answer\n'
        '\n'
        '---'
    )

    fake_writer.write_card_ids()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_updates_id_if_another_is_written(file, fake_writer, cards):
    fake_writer._file_content = (
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
        '> Second answer\n'
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
        '> Second answer\n'
        '\n'
        '---'
    )

    fake_writer.write_card_ids()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_repr_method(fake_writer, file, cards):
    expected = f'Writer(file_path={file!r}, cards={cards!r})'

    assert repr(fake_writer) == expected
