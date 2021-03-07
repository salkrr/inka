from src.inka import util


def test_escapes_backward_slashes():
    text = r'$\sqrt{5}$'
    expected = r'$\\sqrt{5}$'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_stars():
    text = 'some *italic* text'
    expected = r'some \\*italic\\* text'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_double_quotes():
    text = 'text and "quote"'
    expected = r'text and \\"quote\\"'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_underscores():
    text = 'I have some_long_name in here'
    expected = r'I have some\\_long\\_name in here'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_parenthesis():
    text = 'We have (much) to say'
    expected = r'We have \\(much\\) to say'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_hyphen():
    text = 'The hyphen - is a punctuation mark'
    expected = r'The hyphen \\- is a punctuation mark'

    result = util.escape_special_chars(text)

    assert result == expected


def test_escapes_colon():
    text = 'I like: colons'
    expected = r'I like\\: colons'

    result = util.escape_special_chars(text)

    assert result == expected
