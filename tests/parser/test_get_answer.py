import pytest


def test_no_answer_raises_error(fake_parser):
    text = 'Some text'

    with pytest.raises(AttributeError):
        fake_parser._get_cleaned_answer(text)


def test_oneliner_answer(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Some answer'
    )
    expected = 'Some answer'

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected


def test_multiline_answer(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    )
    expected = 'Answer\n\nAdditional info\n\n\n\nAnd more to it'

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected


def test_answer_prefix_inside_answer(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> > Answer\n'
    )
    expected = '> Answer'

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected


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

    expected = 'Answer'

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected


def test_card_with_code_block(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. A little bit of python code...\n'
        '\n'
        '> ```python\n'
        '> def hello(name: str) -> str:\n'
        ">     return f'Hello, {name}!'\n"
        '>\n'
        "> if __name__ == '__main__':\n"
        ">     print(hello('bro'))\n"
        '> ```\n'
        '> some text'
    )
    expected = (
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```\n\n'
        'some text'
    )

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected


def test_card_with_multiple_code_blocks(fake_parser):
    text = (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. A little bit of python code...\n'
        '\n'
        '> Some text before:\n'
        '> ```python\n'
        '> def hello(name: str) -> str:\n'
        ">     return f'Hello, {name}!'\n"
        '>\n'
        "> if __name__ == '__main__':\n"
        ">     print(hello('bro'))\n"
        '> ```\n'
        '> text in between\n'
        '> ```python\n'
        '> def hello(name: str) -> str:\n'
        ">     return f'Hello, {name}!\n"
        '> ```\n'
        '>\n'
        '> text after\n'
        '>\n'
        '> ```commandline\n'
        '> inka collect -u path/to/file.md\n'
        '> ```\n'
    )
    expected = (
        'Some text before:\n\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!'\n"
        '\n'
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        '```\n\n'
        'text in between\n\n'
        '```python\n'
        'def hello(name: str) -> str:\n'
        "    return f'Hello, {name}!\n"
        '```\n\n'
        '\n\n'
        'text after\n\n'
        '\n\n'
        '```commandline\n'
        'inka collect -u path/to/file.md\n'
        '```'
    )

    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected
