import pytest

test_cases = {
    # basic
    ("1. Some question?\n" "\n" "> Answer"): True,
    # basic with curly braces
    ("1. Some {question}?\n" "\n" "> Answer"): True,
    # basic with ID
    ("<!--ID:1612509025074-->\n" "1. Some question?\n" "\n" "> Answer"): True,
    # basic multiline question
    (
        "1. Some question?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "> Answer"
    ): True,
    # basic multiline answer
    (
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "> \n"
        "> Additional info\n"
        "> \n"
        "> And more to it"
    ): True,
    # basic multiline question and answer
    (
        "1. Some question?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "> Answer\n"
        "> \n"
        "> Additional info\n"
        "> \n"
        "> And more to it"
    ): True,
    # cloze
    ("1. Some {question?}\n" "\n"): False,
    # cloze anki format
    ("2. Some {{c1::question?}}\n" "\n"): False,
    # cloze with ID
    ("<!--ID:1612579125074-->\n" "32. Some {question?}\n" "\n"): False,
    # multiline cloze
    (
        "1. Some {question?}\n"
        "\n"
        "More {{c1::info on question}}.\n"
        "\n"
        "{1::And::hint} even more!"
    ): False,
    # not basic and not cloze
    ("3. Some question?\n" "\n"): False,
    # not basic and not cloze with ID
    ("<!--ID:1112809025074-->\n" "3. Some question?\n" "\n"): False,
    # empty
    "": False,
}


@pytest.mark.parametrize("string, expected", test_cases.items())
def test_is_basic_note_str(fake_parser, string, expected):
    result = fake_parser._is_basic_note_str(string)

    assert result == expected
