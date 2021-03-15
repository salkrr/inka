import pytest


def test_no_images(fake_parser):
    section = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
    )
    expected = (
        'Deck: Abraham\n'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
    )

    result = fake_parser._handle_images(section)

    assert result == expected


def test_updates_links_for_one_image(fake_parser, image):
    section = (
        'Deck: Abraham\n'
        f'{image.initial_md_link}'
        '\n'
        '1. Some question?\n'
        ''
        '\n'
        '> Answer\n'
        f'> {image.initial_md_link}'
    )
    expected = (
        'Deck: Abraham\n'
        f'{image.current_md_link}'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        f'> {image.current_md_link}'
    )

    result = fake_parser._handle_images(section)

    assert result == expected


def test_updates_links_for_two_images(fake_parser, image, another_image):
    section = (
        'Deck: Abraham\n'
        f'{image.initial_md_link}'
        '\n'
        '1. Some question?\n'
        ''
        '\n'
        '> Answer\n'
        f'> {another_image.initial_md_link}'
    )
    expected = (
        'Deck: Abraham\n'
        f'{image.current_md_link}'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        f'> {another_image.current_md_link}'
    )

    result = fake_parser._handle_images(section)

    assert result == expected


def test_non_existing_image(fake_parser, image):
    image_md = '![](/path/to/non-existing.png)'
    section = (
        'Deck: Abraham\n'
        f'{image_md}'
        '\n'
        '1. Some question?\n'
        ''
        '\n'
        '> Answer\n'
    )

    with pytest.raises(OSError):
        fake_parser._handle_images(section)
