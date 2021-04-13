import pytest

test_cases = {

    ('1. Question?\n'
     '\n'
     'Answer\n'): [],

    ('Tags:\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): [],

    ('Tags: yolo\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): ['yolo'],

    ('Tags: yolo abc new1\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): ['yolo', 'abc', 'new1'],

    ('1. Question?\n'
     '\n'
     'Answer\n'
     '\n'
     'Tags: yolo\n'
     '\n'
     '2. Q?\n'
     '\n'
     'A\n'): ['yolo'],

    ('Some text; Tags: yolo abc new1\n'
     '1. Question?\n'
     '\n'
     'Answer\n'): [],
}


@pytest.mark.parametrize('section, expected', test_cases.items())
def test_get_tags(fake_parser, section, expected):
    tags = fake_parser._get_tags(section)

    assert tags == expected


def test_get_tags_when_section_with_multiple_tag_fields_raises_error(fake_parser):
    section = (
        'Tags: yolo abc new1\n'
        '1. Question?\n'
        '\n'
        'Tags: okay bro\n'
        'Answer\n'
    )

    with pytest.raises(ValueError):
        fake_parser._get_tags(section)
