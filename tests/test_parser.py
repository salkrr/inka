import unittest

from inka.parser import Parser


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


if __name__ == '__main__':
    unittest.main()
