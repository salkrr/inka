import pytest

test_cases = {
    # empty
    '': [],

    # one basic note
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    ): [
        '1. Some question?\n'
        '\n'
        '> Answer'
    ],

    # basic note, only one newline between question and answer
    (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '> Answer'
    ): [
        '1. Some question?\n'
        '> Answer'
    ],

    # two basic notes
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '2. Q\n'
        '\n'
        '> A'
    ): [
        (
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '\n'
        ),
        (
            '2. Q\n'
            '\n'
            '> A'
        )
    ],

    # two basic notes, only one newline between end of first note and start of next
    (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '2. Q\n'
        '\n'
        '> A'
    ): [
        (
            '1. Some question?\n'
            '\n'
            '> Answer\n'
        ),
        (
            '2. Q\n'
            '\n'
            '> A'
        )
    ],

    # basic note with multiline question
    (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    ): [
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer'
    ],

    # basic note with multiline answer
    (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ): [
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ],

    # basic note with multiline question and answer
    (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ): [
        '1. Some question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it'
    ],

    # note with only question before basic note
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '2. Another question\n'
        '\n'
        '> Answer'
    ): [
        (
            '1. Some question?\n'
            '\n'
        ),
        (
            '2. Another question\n'
            '\n'
            '> Answer'
        )
    ],

    # basic note with ID
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '<!--ID:123456-->\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    ): [
        '<!--ID:123456-->\n'
        '1. Some question?\n'
        '\n'
        '> Answer'
    ],

    # two basic notes with ID
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '<!--ID:123456-->\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '<!--ID:581925-->\n'
        '2. Q\n'
        '\n'
        '> A'
    ): [
        (
            '<!--ID:123456-->\n'
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '\n'
        ),
        (
            '<!--ID:581925-->\n'
            '2. Q\n'
            '\n'
            '> A'
        )
    ],

    # cloze note
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some {question} here?\n'
        '\n'
    ): [
        (
            '1. Some {question} here?\n'
            '\n'
        )
    ],

    # cloze note with ID
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '<!--ID:123456-->\n'
        '1. Some {question} here?\n'
        '\n'
    ): [
        (
            '<!--ID:123456-->\n'
            '1. Some {question} here?\n'
            '\n'
        )
    ],

    # multiline cloze note
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some {question} here?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
    ): [
        (
            '1. Some {question} here?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
        )
    ],

    # multiple cloze notes
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some {question} here?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '2. {1::another} here?\n'
        '\n'
    ): [
        (
            '1. Some {question} here?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
        ),
        (
            '2. {1::another} here?\n'
            '\n'
        )
    ],

    # multiple cloze notes with IDs
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '<!--ID:1612509025074-->\n'
        '1. Some {question} here?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '<!--ID:1612509015034-->\n'
        '2. {1::another} here?\n'
        '\n'
    ): [
        (
            '<!--ID:1612509025074-->\n'
            '1. Some {question} here?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
        ),
        (
            '<!--ID:1612509015034-->\n'
            '2. {1::another} here?\n'
            '\n'
        )
    ],

    # basic and cloze notes with IDs
    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some {question} here?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '2. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '3. {1::another} here?\n'
        '\n'
    ): [
        (
            '1. Some {question} here?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
        ),
        (
            '2. Some question?\n'
            '\n'
            '> Answer\n'
            '\n'
        ),
        (
            '3. {1::another} here?\n'
            '\n'
        )
    ],

    (
        'Deck: Abraham\n'
        '\n'
        'Tags: one two-three\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        '\n'
        '2. Some {question} here?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '3. Question?\n'
        '\n'
        'More info on question.\n'
        '\n'
        'And even more!'
        '\n'
        '> Answer\n'
        '> \n'
        '> Additional info\n'
        '> \n'
        '> And more to it\n'
        '\n'
    ): [
        (
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '\n'
        ),
        (
            '2. Some {question} here?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
        ),
        (
            '3. Question?\n'
            '\n'
            'More info on question.\n'
            '\n'
            'And even more!'
            '\n'
            '> Answer\n'
            '> \n'
            '> Additional info\n'
            '> \n'
            '> And more to it\n'
            '\n'
        )
    ],
}


@pytest.mark.parametrize('section, expected', test_cases.items())
def test_get_note_strings(fake_parser, section, expected):
    note_strings = fake_parser.get_note_strings(section)

    assert note_strings == expected
