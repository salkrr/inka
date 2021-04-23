import pytest

from inka.models.notes.basic_note import BasicNote
from inka.models.notes.cloze_note import ClozeNote


@pytest.fixture
def cloze_note() -> ClozeNote:
    return ClozeNote('text content', ['tag1', 'tag2'], 'deck name')


def test_search_query(cloze_note):
    cloze_note.text_html = '<p>front content</p>'
    expected = '"<p>front content</p>"'

    assert cloze_note.search_query == expected


def test_convert_fields_to_html_when_function_passed(cloze_note):
    new_text = 'new text'

    cloze_note.convert_fields_to_html(lambda text: new_text)

    assert cloze_note.text_html == new_text


def test_update_fields_with_when_function_passed(cloze_note):
    new_text = 'new text'

    cloze_note.update_fields_with(lambda text: new_text)

    assert cloze_note.updated_text_md == new_text


def test_get_raw_fields(cloze_note):
    fields = cloze_note.get_raw_fields()

    assert len(fields) == 1
    assert fields[0] == cloze_note.raw_text_md


def test_get_raw_question_field(cloze_note):
    field = cloze_note.get_raw_question_field()

    assert field == cloze_note.raw_text_md


def test_get_html_fields(cloze_note, config):
    text_field = 'myFront'
    config.update_option_value('anki', 'cloze_field', text_field)
    expected = {
        text_field: cloze_note.text_html,
    }

    assert cloze_note.get_html_fields(config) == expected


def test_get_anki_note_type(cloze_note, config):
    expected = 'my super type'
    config.update_option_value('anki', 'cloze_type', expected)

    assert cloze_note.get_anki_note_type(config) == expected


def test_eq_when_same():
    first_note = ClozeNote('front', ['tag1'], 'deck')
    second_note = ClozeNote('front', ['tag1'], 'deck')

    assert first_note == second_note


@pytest.mark.parametrize('second_note', (
        ClozeNote('oops', ['tag1'], 'deck'),
        ClozeNote('front', ['tag1', 'tag2'], 'deck'),
        ClozeNote('front', ['tag1'], 'my deck'),
        None,
        BasicNote('front', 'back', ['tag1'], 'my deck'),
        'short string'
))
def test_eq_when_not_equal(second_note):
    first_note = ClozeNote('front', ['tag1'], 'deck')

    assert first_note != second_note
