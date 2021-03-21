import filecmp
import os

import pytest

from src.inka.anki_media import AnkiMedia


@pytest.fixture
def anki_media() -> AnkiMedia:
    """Instance of AnkiMedia class with profile 'test'."""
    return AnkiMedia(anki_profile='test')


def test_file_exists_returns_true(anki_media, image_anki):
    expected = True

    assert anki_media.exists(image_anki.file_name) == expected


def test_file_does_not_exist_returns_false(anki_media, image):
    expected = False

    assert anki_media.exists(image.file_name) == expected


def test_copying_non_existing_file_raises_error(anki_media, non_existing_image):
    with pytest.raises(FileNotFoundError):
        anki_media.copy_file_from('path/does/not/exist.md')


def test_copying_file_when_no_file_with_same_name_in_anki_media(anki_media, image, path_to_anki_image):
    expected = True

    anki_media.copy_file_from(image.abs_path)

    assert filecmp.cmp(image.abs_path, path_to_anki_image) == expected


def test_copying_file_when_exists_file_with_same_name_in_anki_media(anki_media, image, path_to_anki_image):
    with open(path_to_anki_image, 'wt') as f:
        f.write('some text')

    with pytest.raises(OSError):
        anki_media.copy_file_from(image.abs_path)


def test_creating_file_when_no_file_with_same_name_in_anki_media(anki_media):
    file_name = '_default.css'
    file_content = 'body { background-color: yellow; }'
    anki_file_path = f'{anki_media._anki_media_path}/{file_name}'

    anki_media.create_file(file_name, file_content)

    with open(anki_file_path, 'rt') as f:
        assert f.read() == file_content

    os.remove(anki_file_path)


def test_creating_file_when_exists_file_with_same_name_in_anki_media(anki_media):
    file_name = '_default.css'
    file_content = 'body { background-color: yellow; }'
    anki_file_path = f'{anki_media._anki_media_path}/{file_name}'
    with open(anki_file_path, 'wt') as f:
        f.write(file_content)

    with pytest.raises(OSError):
        anki_media.create_file(file_name, file_content)

    os.remove(anki_file_path)
