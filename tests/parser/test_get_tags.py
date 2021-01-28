import pytest


def test_section_without_tag_field(parser):
    section = (
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = parser._get_tags(section)

    assert tags == []


def test_section_with_empty_tag_field(parser):
    section = (
        'Tags:\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = parser._get_tags(section)

    assert tags == []


def test_section_with_not_empty_tag_field(parser):
    section = (
        'Tags: yolo\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = ['yolo']

    tags = parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_with_multiple_tags(parser):
    section = (
        'Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )
    expected = ['yolo', 'abc', 'new1']

    tags = parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_not_on_top(parser):
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

    tags = parser._get_tags(section)

    assert tags == expected


def test_section_with_tag_field_inline(parser):
    section = (
        'Some text; Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Answer\n'
    )

    tags = parser._get_tags(section)

    assert tags == []


def test_section_with_multiple_tag_fields(parser):
    section = (
        'Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Tags: okay bro\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        parser._get_tags(section)
