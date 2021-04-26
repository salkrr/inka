import pytest

from inka.models.notes.note import Note

create_search_anki_query_test_cases = {
    # backward slashes
    r"$\sqrt{5}$": r'"$\\sqrt{5}$"',
    # double quotes
    'text and "quote"': r'"text and \"quote\""',
    # underscores
    "I have some_long_name in here": r'"I have some\_long\_name in here"',
    # colons
    "I like: colons a:b:c, yeah": r'"I like\: colons a\:b\:c, yeah"',
    # doesn't escape parenthesis
    "We have (much) to say": r'"We have (much) to say"',
    # doesn't escape hyphen
    "The hyphen - is a punctuation mark": r'"The hyphen - is a punctuation mark"',
}


@pytest.mark.parametrize("text, expected", create_search_anki_query_test_cases.items())
def test_escapes_colon(text, expected):
    assert Note.create_anki_search_query(text) == expected
