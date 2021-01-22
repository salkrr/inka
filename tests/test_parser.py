import unittest

from src.inka.card import Card
from src.inka.parser import Parser


class ParserTest(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = Parser('file_doesnt_exist.md')

    def test_get_question_sections_from_empty_string(self):
        sections = self.parser._get_question_sections('')

        self.assertEqual([], sections)

    def test_get_question_sections_from_string_without_sections(self):
        string_without_sections = (
            'First line'
            'Second line'
            '\t 123 51'
        )

        sections = self.parser._get_question_sections(string_without_sections)

        self.assertEqual([], sections)

    def test_get_question_sections_from_string_with_empty_section(self):
        string_with_empty_section = (
            '---\n'
            '---'
        )

        result = self.parser._get_question_sections(string_with_empty_section)

        self.assertEqual([], result)

    def test_get_question_sections_from_string_with_section_with_incorrect_section_start(self):
        string = (
            '---123\n'
            'Not empty\n'
            '---'
        )

        result = self.parser._get_question_sections(string)

        self.assertEqual([], result)

    def test_get_question_sections_from_string_with_section_with_incorrect_section_end(self):
        string = (
            '---\n'
            'Not empty\n'
            'a---'
        )

        result = self.parser._get_question_sections(string)

        self.assertEqual([], result)

    def test_get_question_sections_from_string_with_section_without_section_end(self):
        string = (
            '---\n'
            'Not empty\n'
            'Ok'
        )

        result = self.parser._get_question_sections(string)

        self.assertEqual([], result)

    def test_get_question_sections_from_string_with_one_section(self):
        string_with_one_section = (
            '---\n'
            'Text inside section\n'
            '---'
        )
        expected = ['Text inside section\n']

        sections = self.parser._get_question_sections(string_with_one_section)

        self.assertEqual(expected, sections)

    def test_get_question_sections_from_string_with_multiline_section_content(self):
        string_with_one_section = (
            '---\n'
            'First\n'
            'Second\n'
            'Third\n'
            '---'
        )
        expected = ['First\nSecond\nThird\n']

        sections = self.parser._get_question_sections(string_with_one_section)

        self.assertEqual(expected, sections)

    def test_get_question_sections_from_string_with_two_sections(self):
        string_with_two_sections = (
            '---\n'
            'First one\n'
            '---\n'
            '---\n'
            'Second one\n'
            '---'
        )
        expected = ['First one\n', 'Second one\n']

        sections = self.parser._get_question_sections(string_with_two_sections)

        self.assertEqual(expected, sections)

    def test_get_question_sections_from_string_with_two_sections_and_text_between_them(self):
        string_with_two_sections = (
            '---\n'
            'First one\n'
            '---\n'
            'Some text in between\n'
            '---\n'
            'Second one\n'
            '---'
        )
        expected = ['First one\n', 'Second one\n']

        sections = self.parser._get_question_sections(string_with_two_sections)

        self.assertEqual(expected, sections)

    def test_get_tags_from_section_without_tag_field(self):
        section = (
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual([], tags)

    def test_get_tags_from_section_with_empty_tag_field(self):
        section = (
            'Tags:\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual([], tags)

    def test_get_tags_from_section_with_not_empty_tag_field(self):
        section = (
            'Tags: yolo\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )
        expected = ['yolo']

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual(expected, tags)

    def test_get_tags_from_section_with_tag_field_with_multiple_tags(self):
        section = (
            'Tags: yolo abc new1\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )
        expected = ['yolo', 'abc', 'new1']

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual(expected, tags)

    def test_get_tags_from_section_with_tag_field_not_on_top(self):
        section = (
            '1. Question?\n'
            '\n'
            'Answer\n'
            '\n'
            'Tags: yolo\n'
            '\n'
            '2. Q?\n'
            '\n'
            'A\n'
        )
        expected = ['yolo']

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual(expected, tags)

    def test_get_tags_from_section_with_tag_field_inline(self):
        section = (
            'Some text; Tags: yolo abc new1\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        tags = self.parser._get_tags_from_section(section)

        self.assertEqual([], tags)

    def test_get_tags_from_section_with_multiple_tag_fields(self):
        section = (
            'Tags: yolo abc new1\n'
            '1. Question?\n'
            '\n'
            'Tags: okay bro\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_tags_from_section(section)

    def test_get_deck_name_from_section_without_deck_name_field(self):
        section = (
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_deck_name_from_section(section)

    def test_get_deck_name_from_section_with_empty_deck_name_field(self):
        section = (
            'Deck:\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_deck_name_from_section(section)

    def test_get_deck_name_from_section_with_only_whitespace_deck_name_field(self):
        section = (
            'Deck:   \n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_deck_name_from_section(section)

    def test_get_deck_name_from_section_with_not_empty_deck_name_field(self):
        section = (
            'Deck: yolo\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )
        expected = 'yolo'

        deck_name = self.parser._get_deck_name_from_section(section)

        self.assertEqual(expected, deck_name)

    def test_get_deck_name_from_section_with_deck_name_field_with_multiple_words(self):
        section = (
            'Deck: Very Long Deck Name\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )
        expected = 'Very Long Deck Name'

        deck_name = self.parser._get_deck_name_from_section(section)

        self.assertEqual(expected, deck_name)

    def test_get_deck_name_from_section_with_deck_name_field_not_on_top(self):
        section = (
            '1. Question?\n'
            '\n'
            'Answer\n'
            '\n'
            'Deck: yolo\n'
            '\n'
            '2. Q?\n'
            '\n'
            'A\n'
        )
        expected = 'yolo'

        deck_name = self.parser._get_deck_name_from_section(section)

        self.assertEqual(expected, deck_name)

    def test_get_deck_name_from_section_with_deck_name_field_inline(self):
        section = (
            'Some text; Deck: yolo\n'
            '1. Question?\n'
            '\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_deck_name_from_section(section)

    def test_get_deck_name_from_section_with_multiple_deck_name_fields(self):
        section = (
            'Deck: Abraham\n'
            '1. Question?\n'
            '\n'
            'Deck: Default\n'
            'Answer\n'
        )

        with self.assertRaises(ValueError):
            self.parser._get_deck_name_from_section(section)

    def test_get_cards_from_section_which_is_empty(self):
        section = ''

        with self.assertRaises(ValueError):
            self.parser._get_cards_from_section(section)

    def test_get_cards_from_section_with_only_deck_field(self):
        section = (
            'Deck: Abraham\n'
        )

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual([], cards)

    def test_get_cards_from_section_with_only_deck_and_tags_fields(self):
        section = (
            'Deck: Abraham\n'
            'Tags: some tags here'
        )

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual([], cards)

    def test_get_cards_from_section_with_one_card_without_tags(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> Answer'
        )
        expected = [Card(front='Some question?', back='Answer', tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_one_card_with_tags(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            'Tags: one two-three\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> Answer'
        )
        expected = [Card(front='Some question?', back='Answer', tags=['one', 'two-three'], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_one_card_without_empty_line_between_question_and_answer(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '> Answer'
        )
        expected = [Card(front='Some question?', back='Answer', tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_two_cards_without_tags(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '\n'
            '2. Q\n'
            '\n'
            '> A'
        )
        expected = [Card(front='Some question?', back='Answer', tags=[], deck_name='Abraham'),
                    Card(front='Q', back='A', tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_two_cards_without_empty_line_between_answer_and_new_question(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '2. Q\n'
            '\n'
            '> A'
        )
        expected = [Card(front='Some question?', back='Answer', tags=[], deck_name='Abraham'),
                    Card(front='Q', back='A', tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_one_card_with_multiline_question(self):
        section = (
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
        expected = [Card(front='Some question?\n\nMore info on question.\n\nAnd even more!',
                         back='Answer', tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_one_card_with_multiline_answer(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '\n'
            '> Answer\n'
            '> \n'
            '> Additional info\n'
            '> \n'
            '> And more to it'
        )
        expected = [Card(front='Some question?',
                         back='Answer\n\nAdditional info\n\nAnd more to it',
                         tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_with_one_card_with_multiline_question_and_answer(self):
        section = (
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
        )
        expected = [Card(front='Some question?\n\nMore info on question.\n\nAnd even more!',
                         back='Answer\n\nAdditional info\n\nAnd more to it',
                         tags=[], deck_name='Abraham')]

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual(expected, cards)

    def test_get_cards_from_section_card_with_incorrect_question_syntax_ignored(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '>> Some question?\n'
            '\n'
            '> Answer\n'
        )

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual([], cards)

    def test_get_cards_from_section_card_with_incorrect_answer_syntax_ignored(self):
        section = (
            'Deck: Abraham\n'
            '\n'
            '1. Some question?\n'
            '\n'
            'Answer\n'
        )

        cards = self.parser._get_cards_from_section(section)

        self.assertEqual([], cards)


if __name__ == '__main__':
    unittest.main()
