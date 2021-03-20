import pytest


def test_no_question_raises_error(fake_parser):
    text = 'Some text'

    with pytest.raises(AttributeError):
        fake_parser.get_question(text)


def test_oneliner_question(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = fake_parser.get_question(text)

    assert question == expected


def test_two_digit_question_prefix(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '12. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = fake_parser.get_question(text)

    assert question == expected


def test_three_digit_question_prefix(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '123. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = fake_parser.get_question(text)

    assert question == expected


def test_multiline_question(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    )
    expected = 'Some question?\n\nMore info on question.\n\nAnd even more!'

    question = fake_parser.get_question(text)

    assert question == expected


def test_card_with_id(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '<!--ID:123456-->\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    )
    expected = 'Some question?'

    question = fake_parser.get_question(text)

    assert question == expected


def test_card_with_code_block(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. A little bit of python code...\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```\n'
        '\n'
        '> some text'
    )
    expected = (
        'A little bit of python code...\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```'
    )

    question = fake_parser.get_question(text)

    assert question == expected


def test_card_with_multiple_code_blocks(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some text before:\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```\n'
        '\n'
        'text in between\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!\n"
        '```\n'
        '\n'
        'text after\n'
        '\n'
        '```commandline\n'
        'inka collect -u path/to/file.md\n'
        '```\n'
        '\n'
        '> Short answer\n'
        '> here'
    )
    expected = (
        'Some text before:\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```\n'
        '\n'
        'text in between\n'
        '\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!\n"
        '```\n'
        '\n'
        'text after\n'
        '\n'
        '```commandline\n'
        'inka collect -u path/to/file.md\n'
        '```'
    )

    question = fake_parser.get_question(text)

    assert question == expected
