import filecmp
import os
import shutil

import pytest


def test_file_exists_returns_true(anki_media, image_anki):
    expected = True
    file_name = os.path.basename(image_anki)

    assert anki_media.exists(file_name) == expected


def test_file_does_not_exist_returns_false(anki_media, image):
    expected = False
    file_name = os.path.basename(image)

    assert anki_media.exists(file_name) == expected


def test_copying_non_existing_file_raises_error(anki_media):
    with pytest.raises(FileNotFoundError):
        anki_media.copy_file_from('path/does/not/exist.md')


def test_copying_file_when_no_file_with_same_name_in_anki_media(anki_media, image, path_to_anki_image):
    expected = True

    anki_media.copy_file_from(image)

    assert filecmp.cmp(image, path_to_anki_image) == expected


def test_copying_file_when_exists_different_file_with_same_name_raises_error(anki_media, image, path_to_anki_image):
    with open(path_to_anki_image, 'wt') as f:
        f.write('some text')

    with pytest.raises(FileExistsError):
        anki_media.copy_file_from(image)


def test_copying_file_when_exists_same_file_with_same_name(anki_media, image):
    anki_file_path = f'{anki_media._anki_media_path}/{image}'
    shutil.copyfile(image, anki_file_path)

    anki_media.copy_file_from(image)

    assert filecmp.cmp(image, anki_file_path)


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

    with pytest.raises(FileExistsError):
        anki_media.create_file(file_name, file_content)

    os.remove(anki_file_path)
