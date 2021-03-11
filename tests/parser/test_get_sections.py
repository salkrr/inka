def test_empty_string(fake_parser):
    sections = fake_parser.get_sections('')

    assert sections == []


def test_string_without_sections(fake_parser):
    string_without_sections = (
        'First line'
        'Second line'
        '\t 123 51'
    )

    sections = fake_parser.get_sections(string_without_sections)

    assert sections == []


def test_string_with_empty_section(fake_parser):
    string_with_empty_section = (
        '---\n'
        '---'
    )

    sections = fake_parser.get_sections(string_with_empty_section)

    assert sections == []


def test_string_with_incorrect_section_start(fake_parser):
    string = (
        '---123\n'
        'Not empty\n'
        '---'
    )

    sections = fake_parser.get_sections(string)

    assert sections == []


def test_string_with_section_with_incorrect_section_end(fake_parser):
    string = (
        '---\n'
        'Not empty\n'
        'a---'
    )

    sections = fake_parser.get_sections(string)

    assert sections == []


def test_string_with_section_without_section_end(fake_parser):
    string = (
        '---\n'
        'Not empty\n'
        'Ok'
    )

    sections = fake_parser.get_sections(string)

    assert sections == []


def test_string_with_one_section(fake_parser):
    string_with_one_section = (
        '---\n'
        'Text inside section\n'
        '---'
    )
    expected = ['Text inside section\n']

    sections = fake_parser.get_sections(string_with_one_section)

    assert sections == expected


def test_string_with_multiline_section_content(fake_parser):
    string_with_one_section = (
        '---\n'
        'First\n'
        'Second\n'
        'Third\n'
        '---'
    )
    expected = ['First\nSecond\nThird\n']

    sections = fake_parser.get_sections(string_with_one_section)

    assert sections == expected


def test_string_with_two_sections(fake_parser):
    string_with_two_sections = (
        '---\n'
        'First one\n'
        '---\n'
        '---\n'
        'Second one\n'
        '---'
    )
    expected = ['First one\n', 'Second one\n']

    sections = fake_parser.get_sections(string_with_two_sections)

    assert sections == expected


def test_string_with_two_sections_and_text_between_them(fake_parser):
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

    sections = fake_parser.get_sections(string_with_two_sections)

    assert sections == expected
