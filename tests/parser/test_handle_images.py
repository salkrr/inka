import pytest


def test_no_images(parser):
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

    result = parser._handle_images(section)

    assert result == expected


def test_updates_links_for_one_image(parser, image):
    section = (
        'Deck: Abraham\n'
        f'{image.original_md_link}'
        '\n'
        '1. Some question?\n'
        ''
        '\n'
        '> Answer\n'
        f'> {image.original_md_link}'
    )
    expected = (
        'Deck: Abraham\n'
        f'{image.updated_md_link}'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        f'> {image.updated_md_link}'
    )

    result = parser._handle_images(section)

    assert result == expected


def test_updates_links_for_two_images(parser, image, another_image):
    section = (
        'Deck: Abraham\n'
        f'{image.original_md_link}'
        '\n'
        '1. Some question?\n'
        ''
        '\n'
        '> Answer\n'
        f'> {another_image.original_md_link}'
    )
    expected = (
        'Deck: Abraham\n'
        f'{image.updated_md_link}'
        '\n'
        '1. Some question?\n'
        '\n'
        '> Answer\n'
        f'> {another_image.updated_md_link}'
    )

    result = parser._handle_images(section)

    assert result == expected


def test_non_existing_image(parser, image):
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
        parser._handle_images(section)
