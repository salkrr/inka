import pytest

from src.inka import converter
from src.inka.card import Card


@pytest.fixture
def card():
    """Card object with dummy data"""
    return Card(front_md='dummy', back_md='dummy', front_html='dummy',
                back_html='dummy', tags=[], deck_name='')


def test_converting_oneliner_front_to_html(card):
    card.front_md = 'some text here'
    expected = '<p>some text here</p>'

    converter.convert_cards_to_html([card])

    assert card.front_html == expected


def test_converting_oneliner_back_to_html(card):
    card.back_md = 'some text here'
    expected = '<p>some text here</p>'

    converter.convert_cards_to_html([card])

    assert card.back_html == expected


def test_converts_front_to_html_without_newline_before_or_after_tags(card):
    card.front_md = (
        '1. Item1\n'
        '2. Item2\n'
        '3. Item3\n'
        '\n'
        '```javascript\n'
        'let a = 12;\n'
        'let b = a;\n'
        '```\n'
        '\n'
        '[google](https://google.com)\n'
    )
    expected = ('<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>'
                '<pre><code class="language-javascript">let a = 12;\nlet b = a;</code></pre>'
                '<p><a href="https://google.com">google</a></p>')

    converter.convert_cards_to_html([card])

    assert card.front_html == expected


def test_converts_back_to_html_without_newline_before_or_after_tags(card):
    card.back_md = (
        '1. Item1\n'
        '2. Item2\n'
        '3. Item3\n'
        '\n'
        '```javascript\n'
        'let a = 12;\n'
        'let b = a;\n'
        '```\n'
        '\n'
        '[google](https://google.com)\n'
    )
    expected = ('<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>'
                '<pre><code class="language-javascript">let a = 12;\nlet b = a;</code></pre>'
                '<p><a href="https://google.com">google</a></p>')

    converter.convert_cards_to_html([card])

    assert card.back_html == expected


def test_converting_front_with_line_break_to_html(card):
    card.front_md = (
        'some text here\n'
        'and more text'
    )
    expected = '<p>some text here\nand more text</p>'

    converter.convert_cards_to_html([card])

    assert card.front_html == expected


def test_converting_back_with_line_break_to_html(card):
    card.back_md = (
        'some text here\n'
        'and more text'
    )
    expected = '<p>some text here\nand more text</p>'

    converter.convert_cards_to_html([card])

    assert card.back_html == expected


def test_converting_multiline_front_to_html(card):
    card.front_md = (
        'some text here\n'
        '\n'
        'more text'
    )
    expected = '<p>some text here</p><p>more text</p>'

    converter.convert_cards_to_html([card])

    assert card.front_html == expected


def test_converting_multiline_back_to_html(card):
    card.back_md = (
        'some text here\n'
        '\n'
        'more text'
    )
    expected = '<p>some text here</p><p>more text</p>'

    converter.convert_cards_to_html([card])

    assert card.back_html == expected


def test_converting_oneliner_front_to_md(card):
    card.front_html = '<p>some text here</p>'
    expected = 'some text here'

    converter.convert_card_to_md(card)

    assert card.front_md == expected


def test_converting_oneliner_back_to_md(card):
    card.back_html = '<p>some text here</p>'
    expected = 'some text here'

    converter.convert_card_to_md(card)

    assert card.back_md == expected


def test_converting_multiline_front_to_md(card):
    card.front_html = '<p>some text here</p><p>more text</p>'
    expected = 'some text here\n\nmore text'

    converter.convert_card_to_md(card)

    assert card.front_md == expected


def test_converting_multiline_back_to_md(card):
    card.back_html = '<p>some text here</p><p>more text</p>'
    expected = 'some text here\n\nmore text'

    converter.convert_card_to_md(card)

    assert card.back_md == expected
