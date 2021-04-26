import os
from unittest.mock import MagicMock

import pytest
from PIL import Image as Img

from inka.models.anki_api import AnkiApi
from inka.models.anki_media import AnkiMedia
from inka.models.config import Config
from inka.models.parser import Parser


@pytest.fixture
def anki_media() -> AnkiMedia:
    """Instance of AnkiMedia class with profile 'test'."""
    anki_media = AnkiMedia(anki_profile="test_profile")

    try:
        os.makedirs(anki_media._anki_media_path)
    except FileExistsError:
        return anki_media

    return anki_media


@pytest.fixture
def anki_media_mock(mocker) -> MagicMock:
    """Mock of AnkiMedia instance"""
    return mocker.MagicMock(spec=AnkiMedia)


@pytest.fixture
def fake_parser() -> Parser:
    """Parser class with dummy filename, default_deck. It uses 'test' profile."""
    return Parser("file_doesnt_exist.md", "")


@pytest.fixture
def anki_api_mock(mocker) -> MagicMock:
    """Mock of AnkiApi instance"""
    return mocker.MagicMock(spec=AnkiApi)


@pytest.fixture
def image() -> str:
    """Path to temp image in working directory"""
    path = "image_for_testing.png"
    Img.new("RGBA", size=(50, 50), color=(155, 0, 0)).save(path, format="png")

    yield path

    os.remove(path)


@pytest.fixture
def another_image() -> str:
    """Path to temp image in working directory"""
    path = "another_image_for_testing.png"
    Img.new("RGBA", size=(50, 50), color=(155, 0, 123)).save(path, format="png")

    yield path

    os.remove(path)


@pytest.fixture
def path_to_anki_image(anki_media, image):
    """Path to non-existing image (with the same name as 'image' fixture returns) in anki media folder"""
    path_to_anki_image = f"{anki_media._anki_media_path}/{image}"

    yield path_to_anki_image

    # Remove image if it was created
    try:
        os.remove(path_to_anki_image)
    except OSError:
        pass


@pytest.fixture
def path_to_another_anki_image(anki_media, another_image):
    """Path to non-existing image (with the same name as 'another_image' fixture returns) in anki media folder"""
    path = f"{anki_media._anki_media_path}/{another_image}"

    yield path

    # Remove image if it was created
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture
def image_anki(anki_media, path_to_anki_image) -> str:
    """Temporary image in anki media folder with the same name as 'image' fixture returns
    but different content.
    """
    Img.new("RGBA", size=(20, 150), color=(100, 13, 35)).save(
        path_to_anki_image, format="png"
    )
    return path_to_anki_image


@pytest.fixture
def config_path(tmp_path):
    """Temporary path to config file"""
    return tmp_path / "test_config.ini"


@pytest.fixture
def config(config_path):
    """Instance of Config class. Path to config specified by 'config_path' fixture"""
    return Config(config_path)
