import pytest

from src.inka import converter
from src.inka.card import Card


@pytest.fixture
def card():
    """Card object with dummy data"""
    return Card(front_md='dummy', back_md='dummy', front_html='dummy',
                back_html='dummy', tags=[], deck_name='')


test_strings = {
    'some text here': '<p>some text here</p>',
    ('1. Item1\n'
     '2. Item2\n'
     '3. Item3\n'
     '\n'
     '```javascript\n'
     'let a = 12;\n'
     'let b = a;\n'
     '```\n'
     '\n'
     '[google](https://google.com)\n'): ('<ol><li>Item1</li><li>Item2</li><li>Item3</li></ol>'
                                         '<pre><code class="language-javascript">let a = 12;\nlet b = a;</code></pre>'
                                         '<p><a href="https://google.com">google</a></p>'),
    ('some text here\n'
     'and more text'): '<p>some text here\nand more text</p>',
    ('some text here\n'
     '\n'
     'more text'): '<p>some text here</p><p>more text</p>',
}


@pytest.mark.parametrize('test_input, expected', test_strings.items())
def test_convert_cards_to_html_front_of_card(card, test_input, expected):
    card.updated_front_md = test_input

    converter.convert_cards_to_html([card])

    assert card.front_html == expected


@pytest.mark.parametrize('test_input, expected', test_strings.items())
def test_convert_cards_to_html_back_of_card(card, test_input, expected):
    card.updated_back_md = test_input

    converter.convert_cards_to_html([card])

    assert card.back_html == expected


@pytest.mark.skip('WIP')
@pytest.mark.parametrize('expected, test_input', test_strings.items())
def test_convert_card_to_md_front_of_card(card, test_input, expected):
    card.front_html = test_input

    converter.convert_card_to_md(card)

    assert card.front_md == expected


@pytest.mark.skip('WIP')
@pytest.mark.parametrize('expected, test_input', test_strings.items())
def test_convert_card_to_md_back_of_card(card, test_input, expected):
    card.back_html = test_input

    converter.convert_card_to_md(card)

    assert card.back_md == expected