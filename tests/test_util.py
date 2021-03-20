from src.inka import util


def test_escapes_backward_slashes():
    text = r'$\sqrt{5}$'
    expected = r'"$\\sqrt{5}$"'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_escapes_stars():
    text = 'some *italic* text'
    expected = r'"some \*italic\* text"'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_escapes_double_quotes():
    text = 'text and "quote"'
    expected = r'"text and \"quote\""'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_escapes_underscores():
    text = 'I have some_long_name in here'
    expected = r'"I have some\_long\_name in here"'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_does_not_escape_parenthesis():
    text = 'We have (much) to say'
    expected = r'"We have (much) to say"'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_does_not_escape_hyphen():
    text = 'The hyphen - is a punctuation mark'
    expected = r'"The hyphen - is a punctuation mark"'

    result = util.create_anki_search_query(text)

    assert result == expected


def test_escapes_colon():
    text = 'I like: colons a:b:c, yeah'
    expected = r'"I like\: colons a\:b\:c, yeah"'

    result = util.create_anki_search_query(text)

    assert result == expected
