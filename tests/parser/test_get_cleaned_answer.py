import pytest

test_cases = {
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Some answer"
    ): "Some answer",
    (
        "Deck: Abraham\n"
        "\n"
        "1. Some question?\n"
        "\n"
        "> Answer\n"
        "> Additional info\n"
        "> \n"
        "> And more to it"
    ): "Answer\n\nAdditional info\n\n\n\nAnd more to it",
    "Deck: Abraham\n\n1. Some question?\n\n> > Answer\n": "> Answer",
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "<!--ID:123456-->\n"
        "1. Some question?\n"
        "\n"
        "> Answer"
    ): "Answer",
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. A little bit of python code...\n"
        "\n"
        "> ```python\n"
        "> def hello(name: str) -> str:\n"
        ">     return f'Hello, {name}!'\n"
        ">\n"
        "> if __name__ == '__main__':\n"
        ">     print(hello('bro'))\n"
        "> ```\n"
        "> some text"
    ): (
        "```python\n"
        "def hello(name: str) -> str:\n"
        "    return f'Hello, {name}!'\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        "```\n\n"
        "some text"
    ),
    (
        "Deck: Abraham\n"
        "\n"
        "Tags: one two-three\n"
        "\n"
        "1. A little bit of python code...\n"
        "\n"
        "> Some text before:\n"
        "> ```python\n"
        "> def hello(name: str) -> str:\n"
        ">     return f'Hello, {name}!'\n"
        ">\n"
        "> if __name__ == '__main__':\n"
        ">     print(hello('bro'))\n"
        "> ```\n"
        "> text in between\n"
        "> ```python\n"
        "> def hello(name: str) -> str:\n"
        ">     return f'Hello, {name}!\n"
        "> ```\n"
        ">\n"
        "> text after\n"
        ">\n"
        "> ```commandline\n"
        "> inka collect -u path/to/file.md\n"
        "> ```\n"
    ): (
        "Some text before:\n\n"
        "```python\n"
        "def hello(name: str) -> str:\n"
        "    return f'Hello, {name}!'\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    print(hello('bro'))\n"
        "```\n\n"
        "text in between\n\n"
        "```python\n"
        "def hello(name: str) -> str:\n"
        "    return f'Hello, {name}!\n"
        "```\n\n"
        "\n\n"
        "text after\n\n"
        "\n\n"
        "```commandline\n"
        "inka collect -u path/to/file.md\n"
        "```"
    ),
    # inline mathjax
    "> $\n> X^{2}\n> $": "$\n\nX^{2}\n\n$",
    "> \\$\n> X^{2}\n> $": "\\$\n\nX^{2}\n\n$",
    "> $\n> X^{2}\n> \\$": "$\n\nX^{2}\n\n\\$",
    # mathjax blocks
    "> $$\n> X^{2}\n> $$": "$$\nX^{2}\n$$",
    "> \\$$\n> X^{2}\n> $$": "\\$$\n\nX^{2}\n\n$$",
    "> $\\$\n> X^{2}\n> $$": "$\\$\n\nX^{2}\n\n$$",
    "> $$\n> X^{2}\n> \\$$": "$$\n\nX^{2}\n\n\\$$",
    "> $$\n> X^{2}\n> $\\$": "$$\n\nX^{2}\n\n$\\$",
    "> \\$\\$\n> X^{2}\n> $$": "\\$\\$\n\nX^{2}\n\n$$",
    "> \\$$\n> X^{2}\n> \\$$": "\\$$\n\nX^{2}\n\n\\$$",
    "> \\$$\n> X^{2}\n> $\\$": "\\$$\n\nX^{2}\n\n$\\$",
    "> $\\$\n> X^{2}\n> \\$$": "$\\$\n\nX^{2}\n\n\\$$",
    "> $\\$\n> X^{2}\n> $\\$": "$\\$\n\nX^{2}\n\n$\\$",
    "> \\$\\$\n> X^{2}\n> \\$$": "\\$\\$\n\nX^{2}\n\n\\$$",
    "> \\$\\$\n> X^{2}\n> $\\$": "\\$\\$\n\nX^{2}\n\n$\\$",
    "> $\\$\n> X^{2}\n> \\$\\$": "$\\$\n\nX^{2}\n\n\\$\\$",
    "> \\$\\$\n> X^{2}\n> \\$\\$": "\\$\\$\n\nX^{2}\n\n\\$\\$",
    # If no answer
    "Some text": None,
}


@pytest.mark.parametrize("text, expected", test_cases.items())
def test_get_answer(fake_parser, text, expected):
    answer = fake_parser._get_cleaned_answer(text)

    assert answer == expected
