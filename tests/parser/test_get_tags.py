import pytest


def test_section_without_tag_field(fake_parser):
    section = (
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = fake_parser._get_tags(section)

    assert tags == []


def test_section_with_empty_tag_field(fake_parser):
    section = (
        'Tags:\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = fake_parser._get_tags(section)

    assert tags == []


def test_section_with_not_empty_tag_field(fake_parser):
    section = (
        'Tags: yolo\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = ['yolo']

    tags = fake_parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_with_multiple_tags(fake_parser):
    section = (
        'Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = ['yolo', 'abc', 'new1']

    tags = fake_parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_not_on_top(fake_parser):
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

    tags = fake_parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_inline(fake_parser):
    section = (
        'Some text; Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = fake_parser._get_tags(section)

    assert tags == []


def test_section_with_multiple_tag_fields(fake_parser):
    section = (
        'Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Tags: okay bro\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        fake_parser._get_tags(section)
