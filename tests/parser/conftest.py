import pytest

from src.inka.parser import Parser


@pytest.fixture
def parser():
    return Parser('file_doesnt_exist.md')
