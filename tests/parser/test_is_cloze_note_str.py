import pytest

test_cases = {
    # basic
    ("1. Some question?\n" "\n" "> Answer"): False,
    # basic with ID
    ("<!--ID:1612509025074-->\n" "1. Some question?\n" "\n" "> Answer"): False,
    # basic multiline question
    (
        "1. Some question?\n"
        "\n"
        "More info on question.\n"
        "\n"
        "And even more!"
        "\n"
        "> Answer"
    ): False,
    # basic multiline answer
    (
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "> \n"
        "> Additional info\n"
        "> \n"
        "> And more to it"
    ): False,
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
    ): False,
    # cloze
    ("1. Some {question?}\n" "\n"): True,
    # cloze anki format
    ("2. Some {{c1::question?}}\n" "\n"): True,
    # cloze with ID
    ("<!--ID:1612579125074-->\n" "32. Some {question?}\n" "\n"): True,
    # multiline cloze
    (
        "1. Some {question?}\n"
        "\n"
        "More {{c1::info on question}}.\n"
        "\n"
        "{1::And::hint} even more!"
    ): True,
    # not basic and not cloze
    ("3. Some question?\n" "\n"): False,
    # not basic and not cloze with ID
    ("<!--ID:1112809025074-->\n" "3. Some question?\n" "\n"): False,
    # basic with curly braces
    ("1. Some {question}?\n" "\n" "> Answer"): True,
    # empty
    "": False,
}


@pytest.mark.parametrize("string, expected", test_cases.items())
def test_is_cloze_note_str(fake_parser, string, expected):
    result = fake_parser._is_cloze_note_str(string)

    assert result == expected
