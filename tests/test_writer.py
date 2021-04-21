import random
from pathlib import Path
from typing import List, Union

import pytest

from inka.models.notes.basic_note import BasicNote
from inka.models.notes.cloze_note import ClozeNote
from inka.models.parser import Parser
from inka.models.writer import Writer


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
            '3. Only one {line}\n'
            '\n'
            '4. Mul{1::tip}le\n\n'
            '{lines}\n\n'
            'here\n\n'
            '---'
        )

    return file_path


@pytest.fixture
def notes(file: Path) -> List[Union[BasicNote, ClozeNote]]:
    """Notes from the temporary file with randomly generated ids"""
    parser = Parser(file, '')
    notes = parser.collect_notes()
    for note in notes:
        note.anki_id = random.randint(1000000000, 9999999999)

    return notes


@pytest.fixture
def writer(file: Path, notes: List[Union[BasicNote, ClozeNote]]) -> Writer:
    """Fake writer which uses temporary file"""
    return Writer(file, notes)


@pytest.fixture
def writer_with_ids(file: Path, notes: List[Union[BasicNote, ClozeNote]]) -> Writer:
    """Fake writer which uses temporary file and has IDs on cards"""
    writer = Writer(file, notes)
    writer.update_note_ids()
    return writer


def test_update_ids_saves_to_file_system(writer, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.update_note_ids()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_update_ids_skips_card_if_it_was_not_found(writer, notes):
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
        f'<!--ID:{notes[1].anki_id}-->\n'
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

    writer.update_note_ids()

    assert writer._file_content == expected


def test_update_ids_does_not_add_id_if_it_no_id_in_card(writer, notes):
    notes[0].anki_id = None
    notes[3].anki_id = None
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
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer.update_note_ids()

    assert writer._file_content == expected


def test_update_ids_removes_id_from_file_if_card_object_has_no_id(writer, notes):
    writer._file_content = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
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
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )
    notes[0].anki_id = None

    writer.update_note_ids()

    assert writer._file_content == expected


def test_update_ids_writes_id_before_question(writer, notes):
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer.update_note_ids()

    assert writer._file_content == expected


def test_updates_id_if_another_is_written(writer, notes):
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
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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

    writer.update_note_ids()

    assert writer._file_content == expected


def test_update_card_fields_saves_to_file_system(writer, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.update_fields_of_basic_notes()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_update_card_fields_skips_not_changed_cards(writer_with_ids, notes):
    notes[0].changed = False
    notes[0].raw_front_md = 'Amazing new text'
    notes[0].raw_back_md = 'Amazing new answer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.update_fields_of_basic_notes()

    assert writer_with_ids._file_content == expected


def test_updates_question_field(writer_with_ids, notes):
    notes[0].changed = True
    notes[0].raw_front_md = 'Amazing new text'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        f'1. {notes[0].raw_front_md}\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.update_fields_of_basic_notes()

    assert writer_with_ids._file_content == expected


def test_updates_multiline_question_field(writer_with_ids, notes):
    notes[1].changed = True
    notes[1].raw_front_md = 'Something new\n\nhere'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
        f'2. {notes[1].raw_front_md}\n'
        '\n'
        '> Second answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.update_fields_of_basic_notes()

    assert writer_with_ids._file_content == expected


def test_updates_answer_field(writer_with_ids, notes):
    notes[0].changed = True
    notes[0].raw_back_md = 'New answer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        f'> {notes[0].raw_back_md}\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.update_fields_of_basic_notes()

    assert writer_with_ids._file_content == expected


def test_updates_multiline_answer_field(writer_with_ids, notes):
    notes[1].changed = True
    notes[1].raw_back_md = 'New\n\nmultiline\n\nanswer'
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[0].anki_id}-->\n'
        '1. Some question?\n'
        '\n'
        '> First answer\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.update_fields_of_basic_notes()

    assert writer_with_ids._file_content == expected


def test_delete_saves_changes_to_file_system(writer, notes, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.delete_notes()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_delete_skips_cards_that_are_not_marked_for_deletion(writer_with_ids, notes):
    notes[0].to_delete = False
    notes[1].to_delete = False
    expected = writer_with_ids._file_content

    writer_with_ids.delete_notes()

    assert writer_with_ids._file_content == expected


def test_deletes_card_marked_for_deletion(writer_with_ids, notes):
    notes[0].to_delete = True
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[1].anki_id}-->\n'
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
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.delete_notes()

    assert writer_with_ids._file_content == expected


def test_deletes_multiple_cards_marked_for_deletion(writer_with_ids, notes):
    notes[0].to_delete = True
    notes[1].to_delete = True
    expected = (
        '---\n'
        '\n'
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        f'<!--ID:{notes[2].anki_id}-->\n'
        '3. Only one {line}\n'
        '\n'
        f'<!--ID:{notes[3].anki_id}-->\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer_with_ids.delete_notes()

    assert writer_with_ids._file_content == expected


def test_update_cloze_notes_saves_to_file_system(writer, file):
    expected = 'Some string'
    writer._file_content = expected

    writer.update_cloze_notes()

    with open(file, mode='rt', encoding='utf-8') as f:
        assert f.read() == expected


def test_update_cloze_notes_when_note_has_only_one_line(writer, notes):
    notes[2].updated_text_md = 'Only one {{c1::line}}'
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
        '3. Only one {{c1::line}}\n'
        '\n'
        '4. Mul{1::tip}le\n\n'
        '{lines}\n\n'
        'here\n\n'
        '---'
    )

    writer.update_cloze_notes()

    assert writer._file_content == expected


def test_update_cloze_notes_when_note_has_multiple_lines(writer, notes):
    notes[3].updated_text_md = (
        'Mul{{c1::tip}}le\n\n'
        '{{c2::lines}}\n\n'
        'here'
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
        '3. Only one {line}\n'
        '\n'
        '4. Mul{{c1::tip}}le\n\n'
        '{{c2::lines}}\n\n'
        'here\n\n'
        '---'
    )

    writer.update_cloze_notes()

    assert writer._file_content == expected


# updates multiple cards
def test_update_cloze_notes_when_multiple_notes_has_changes(writer, notes):
    notes[2].updated_text_md = 'Only one {{c1::line}}'
    notes[3].updated_text_md = (
        'Mul{{c1::tip}}le\n\n'
        '{{c2::lines}}\n\n'
        'here'
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
        '3. Only one {{c1::line}}\n'
        '\n'
        '4. Mul{{c1::tip}}le\n\n'
        '{{c2::lines}}\n\n'
        'here\n\n'
        '---'
    )

    writer.update_cloze_notes()

    assert writer._file_content == expected


def test_update_cloze_notes_basic_notes_ignored(writer, notes):
    notes[0].updated_front_md = 'Amazing new question'
    expected = writer._file_content

    writer.update_cloze_notes()

    assert writer._file_content == expected


def test_update_cloze_notes_updates_raw_text_value(writer, notes):
    notes[2].updated_text_md = 'Too many {{c1::lines}}'

    writer.update_cloze_notes()

    assert notes[2].raw_text_md == notes[2].updated_text_md
