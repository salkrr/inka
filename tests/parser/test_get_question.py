import pytest

test_cases = {
    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): 'Some question?',

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '12. Some question?\n'
     '\n'
     '> Answer'): 'Some question?',

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '123. Some question?\n'
     '\n'
     '> Answer'): 'Some question?',

    ('Deck: Abraham\n'
     '\n'
     '1. Some question?\n'
     '\n'
     'More info on question.\n'
     '\n'
     'And even more!'
     '\n'
     '> Answer'): 'Some question?\n\nMore info on question.\n\nAnd even more!',

    ('Deck: Abraham\n'
     '\n'
     'Tags: one two-three\n'
     '\n'
     '<!--ID:123456-->\n'
     '1. Some question?\n'
     '\n'
     '> Answer'): 'Some question?',

    ('Deck: Abraham\n'
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
     '> some text'): ('A little bit of python code...\n'
                      '\n'
                      '```python\n'
                      'def hello(name: str) -> str:\n'
                      "    return f'Hello, {name}!'\n"
                      '\n'
                      "if __name__ == '__main__':\n"
                      "    print(hello('bro'))\n"
                      '```'),

    ('Deck: Abraham\n'
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
     '> here'): ('Some text before:\n'
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
                 '```'),
    # cloze
    (
        '1. Some {question?}\n'
        '\n'
    ): 'Some {question?}',

    # cloze anki format
    (
        '2. Some {{c1::question?}}\n'
        '\n'
    ): 'Some {{c1::question?}}',

    # cloze with ID
    (
        '<!--ID:1612579125074-->\n'
        '32. Some {question?}\n'
        '\n'
    ): 'Some {question?}',

    # multiline cloze
    (
        '1. Some {question?}\n'
        '\n'
        'More {{c1::info on question}}.\n'
        '\n'
        '{1::And::hint} even more!'
    ): (
        'Some {question?}\n'
        '\n'
        'More {{c1::info on question}}.\n'
        '\n'
        '{1::And::hint} even more!'
    ),

    # no question
    'Some text': None,
}


@pytest.mark.parametrize('text, expected', test_cases.items())
def test_get_question(fake_parser, text, expected):
    question = fake_parser.get_question(text)

    assert question == expected
