import pytest

test_cases = {
    "": [],
    ("First line" "Second line" "\t 123 51"): [],
    ("---\n" "---"): [],
    ("---123\n" "Not empty\n" "---"): [],
    ("---\n" "Not empty\n" "a---"): [],
    ("---\n" "Not empty\n" "Ok"): [],
    ("---\n" "Text inside section\n" "---"): ["Text inside section\n"],
    ("---\n" "First\n" "Second\n" "Third\n" "---"): ["First\nSecond\nThird\n"],
    ("---\n" "First one\n" "---\n" "---\n" "Second one\n" "---"): [
        "First one\n",
        "Second one\n",
    ],
    (
        "---\n"
        "First one\n"
        "---\n"
        "Some text in between\n"
        "---\n"
        "Second one\n"
        "---"
    ): [
        "First one\n",
        "Second one\n",
    ],
}


@pytest.mark.parametrize("text, expected", test_cases.items())
def test_get_sections(fake_parser, text, expected):
    sections = fake_parser._get_sections(text)

    assert sections == expected
