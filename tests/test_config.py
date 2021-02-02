import configparser
import os

import pytest

from src.inka.config import Config


@pytest.fixture
def config_path(tmp_path):
    """Temporary path to config file"""
    return tmp_path / 'test_config.ini'


@pytest.fixture
def config(config_path):
    """Instance of Config class. Path to config specified by 'config_path' fixture"""
    return Config(config_path)


@pytest.fixture
def default_config_string():
    """Contents of the default config file"""
    return (
        '[defaults]\n'
        'deck = Default\n'
        'folder = \n'
        '\n'
        '[anki]\n'
        'profile = \n'
        'note_type = Basic\n'
        'front_field = Front\n'
        'back_field = Back\n'
        '\n'
        '[anki_connect]\n'
        'port = 8765\n'
        '\n'
    )


def test_saves_correctly(tmp_path):
    filepath = tmp_path / 'test_config.ini'
    config = Config(filepath)
    config._config = configparser.ConfigParser()
    config._config['defaults'] = {
        'deck': 'Default',
        'folder': ''
    }
    expected = (
        '[defaults]\n'
        'deck = Default\n'
        'folder = \n'
        '\n'
    )

    config._save()

    with open(filepath, mode='rt', encoding='utf-8') as file:
        assert file.read() == expected


def test_reads_correctly_from_existing_config(config_path):
    with open(config_path, mode='wt', encoding='utf-8') as file:
        file.write(
            '[defaults]\n'
            'deck = Default\n'
            'folder =\n'
            '\n'
            '[anki_connect]\n'
            'port = 8765\n'
        )
    config = Config(config_path)

    expected = configparser.ConfigParser()
    expected['defaults'] = {
        'deck': 'Default',
        'folder': ''
    }
    expected['anki_connect'] = {
        'port': '8765'
    }

    assert config._config == expected


def test_create_default_config(config, config_path, default_config_string):
    os.remove(config_path)

    config._create_default()

    with open(config_path, mode='rt', encoding='utf-8') as file:
        assert file.read() == default_config_string


def test_if_config_not_found_created_default(config, config_path, default_config_string):
    with open(config_path, mode='rt', encoding='utf-8') as file:
        assert file.read() == default_config_string


def test_get_entry_value(config):
    expected = 'Default'

    entry_value = config.get_entry_value('defaults', 'deck')

    assert entry_value == expected


def test_get_entry_value_with_incorrect_section_raises_error(config):
    with pytest.raises(KeyError):
        config.get_entry_value('ankiConnect', 'port')


def test_get_entry_value_with_incorrect_key_raises_error(config):
    with pytest.raises(KeyError):
        config.get_entry_value('defaults', 'profile')


def test_updates_entry_value_in_backing_object(config):
    new_value = 'path/to/folder'
    config.update_entry_value('defaults', 'folder', new_value)

    updated_value = config._config['defaults']['folder']

    assert updated_value == new_value


def test_updates_entry_value_in_file(config, config_path):
    new_value = 'path/to/folder'
    config.update_entry_value('defaults', 'folder', new_value)
    config_parser = configparser.ConfigParser()

    config_parser.read(config_path)
    updated_value = config_parser['defaults']['folder']

    assert updated_value == new_value


def test_update_entry_value_with_incorrect_section_raises_error(config):
    with pytest.raises(KeyError):
        config.update_entry_value('ankiConnect', 'port', '12')


def test_update_entry_value_with_incorrect_key_raises_error(config):
    with pytest.raises(KeyError):
        config.update_entry_value('defaults', 'profile', 'Profile Name')
