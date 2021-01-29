import os
import shutil
from unittest.mock import Mock

import pytest

from src.inka.image import Image


def test_copy_new_image(parser, image, path_to_anki_image):
    parser._copy_image_to_anki_media(image)

    assert os.path.exists(path_to_anki_image)


def test_copy_non_existing_image_raises_error(parser):
    image = Image('![](/path/to/non-existing.png)')

    with pytest.raises(OSError):
        parser._copy_image_to_anki_media(image)


def test_path_to_image_is_changed(parser, image):
    expected = image.file_name

    parser._copy_image_to_anki_media(image)

    assert image.path == expected


def test_if_exists_same_image_in_anki_media_our_is_not_copied(parser, image, path_to_anki_image):
    shutil.copyfile(image.abs_path, path_to_anki_image)
    image.rename = Mock()

    parser._copy_image_to_anki_media(image)

    image.rename.assert_not_called()


def test_exists_different_image_with_same_name_in_anki_media(parser, image, image_anki):
    image.rename = Mock()

    parser._copy_image_to_anki_media(image)

    image.rename.assert_called()
