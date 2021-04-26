import pytest

from inka.models.notes.basic_note import BasicNote
from inka.models.notes.cloze_note import ClozeNote


@pytest.fixture
def basic_note() -> BasicNote:
    return BasicNote("front content", "back content", ["tag1", "tag2"], "deck name")


def test_search_query(basic_note):
    basic_note.front_html = "<p>front content</p>"
    expected = '"<p>front content</p>"'

    assert basic_note.search_query == expected


def test_convert_fields_to_html_when_function_passed(basic_note):
    new_text = "new text"

    basic_note.convert_fields_to_html(lambda text: new_text)

    assert basic_note.front_html == new_text
    assert basic_note.back_html == new_text


def test_update_fields_with_when_function_passed(basic_note):
    new_text = "new text"

    basic_note.update_fields_with(lambda text: new_text)

    assert basic_note.updated_front_md == new_text
    assert basic_note.updated_back_md == new_text


def test_get_raw_fields(basic_note):
    fields = basic_note.get_raw_fields()

    assert len(fields) == 2
    assert fields[0] == basic_note.raw_front_md
    assert fields[1] == basic_note.raw_back_md


def test_get_raw_question_field(basic_note):
    field = basic_note.get_raw_question_field()

    assert field == basic_note.raw_front_md


def test_get_html_fields(basic_note, config):
    front_name = "myFront"
    back_name = "myBack"
    config.update_option_value("anki", "front_field", front_name)
    config.update_option_value("anki", "back_field", back_name)
    expected = {front_name: basic_note.front_html, back_name: basic_note.back_html}

    assert basic_note.get_html_fields(config) == expected


def test_get_anki_note_type(basic_note, config):
    expected = "my super type"
    config.update_option_value("anki", "basic_type", expected)

    assert basic_note.get_anki_note_type(config) == expected


def test_eq_when_same():
    first_note = BasicNote("front", "back", ["tag1"], "deck")
    second_note = BasicNote("front", "back", ["tag1"], "deck")

    assert first_note == second_note


@pytest.mark.parametrize(
    "second_note",
    (
        BasicNote("oops", "back", ["tag1"], "deck"),
        BasicNote("front", "oops", ["tag1"], "deck"),
        BasicNote("front", "back", ["tag1", "tag2"], "deck"),
        BasicNote("front", "back", ["tag1"], "my deck"),
        None,
        ClozeNote("front", ["tag1"], "my deck"),
        "short string",
    ),
)
def test_eq_when_not_equal(second_note):
    first_note = BasicNote("front", "back", ["tag1"], "deck")

    assert first_note != second_note
