import os

import pytest
from PIL import Image as Img

from src.inka.image import Image
from src.inka.parser import Parser


@pytest.fixture
def parser():
    return Parser('file_doesnt_exist.md')


@pytest.fixture
def image():
    """Temporary image in working directory"""
    filename = 'image_for_testing.png'
    markdown_link = f'![]({filename})'
    Img.new('RGBA', size=(50, 50), color=(155, 0, 0)).save(filename, format='png')

    image = Image(markdown_link)
    yield image

    os.remove(image.abs_path)


@pytest.fixture
def path_to_anki_image(parser, image):
    """Path to image (with the same name as 'image' fixture returns) in anki media folder"""
    path_to_anki_image = f'{parser._anki_media_path}/{image.file_name}'

    yield path_to_anki_image

    # Remove image if it was created
    try:
        os.remove(path_to_anki_image)
    except OSError:
        pass


@pytest.fixture
def image_anki(path_to_anki_image):
    """Temporary image in anki media folder with the same name as 'image' fixture returns"""
    markdown_link = f'![]({path_to_anki_image})'
    Img.new('RGBA', size=(50, 50), color=(100, 0, 0)).save(path_to_anki_image, format='png')

    return Image(markdown_link)
