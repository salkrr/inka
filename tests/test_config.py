import configparser
import os

import pytest

from inka.models.config import Config


@pytest.fixture
def default_config_string():
    """Contents of the default config file"""
    return (
        "[defaults]\n"
        "profile = \n"
        "deck = Default\n"
        "folder = \n"
        "\n"
        "[anki]\n"
        "basic_type = Basic\n"
        "front_field = Front\n"
        "back_field = Back\n"
        "cloze_type = Cloze\n"
        "cloze_field = Text\n"
        "\n"
        "[anki_connect]\n"
        "port = 8765\n"
        "\n"
        "[highlight]\n"
        "style = monokai\n"
        "\n"
    )


def test_saves_correctly(tmp_path):
    filepath = tmp_path / "test_config.ini"
    config = Config(filepath)
    config._config = configparser.ConfigParser()
    config._config["defaults"] = {"deck": "Default", "folder": ""}
    expected = "[defaults]\n" "deck = Default\n" "folder = \n" "\n"

    config._save()

    with open(filepath, mode="rt", encoding="utf-8") as file:
        assert file.read() == expected


def test_reads_correctly_from_existing_config(config_path):
    with open(config_path, mode="wt", encoding="utf-8") as file:
        file.write(
            "[defaults]\n"
            "deck = Default\n"
            "folder =\n"
            "\n"
            "[anki_connect]\n"
            "port = 8765\n"
        )
    config = Config(config_path)

    expected = configparser.ConfigParser()
    expected["defaults"] = {"deck": "Default", "folder": ""}
    expected["anki_connect"] = {"port": "8765"}

    assert config._config == expected


def test_create_default_config(config, config_path, default_config_string):
    os.remove(config_path)

    config._create_default()

    with open(config_path, mode="rt", encoding="utf-8") as file:
        assert file.read() == default_config_string


def test_if_config_not_found_created_default(
    config, config_path, default_config_string
):
    with open(config_path, mode="rt", encoding="utf-8") as file:
        assert file.read() == default_config_string


def test_get_entry_value(config):
    expected = "Default"

    entry_value = config.get_option_value("defaults", "deck")

    assert entry_value == expected


def test_get_entry_value_with_incorrect_section_raises_error(config):
    with pytest.raises(KeyError):
        config.get_option_value("ankiConnect", "port")


def test_get_entry_value_with_incorrect_key_raises_error(config):
    with pytest.raises(KeyError):
        config.get_option_value("anki_connect", "profile")


def test_updates_entry_value_in_backing_object(config):
    new_value = "path/to/folder"
    config.update_option_value("defaults", "folder", new_value)

    updated_value = config._config["defaults"]["folder"]

    assert updated_value == new_value


def test_updates_entry_value_in_file(config, config_path):
    new_value = "path/to/folder"
    config.update_option_value("defaults", "folder", new_value)
    config_parser = configparser.ConfigParser()

    config_parser.read(config_path)
    updated_value = config_parser["defaults"]["folder"]

    assert updated_value == new_value


def test_update_option_value_with_incorrect_section_raises_error(config):
    with pytest.raises(KeyError):
        config.update_option_value("ankiConnect", "port", "12")


def test_update_option_value_with_incorrect_key_raises_error(config):
    with pytest.raises(KeyError):
        config.update_option_value("defaults", "port", "Profile Name")


def test_repr_method(config, config_path):
    expected = f"Config(config_path={repr(config_path)})"

    assert repr(config) == expected


def test_reset(config, config_path, default_config_string):
    config.update_option_value("defaults", "profile", "new profile")

    config.reset()

    with open(config_path, mode="rt", encoding="utf-8") as f:
        assert f.read() == default_config_string


def test_new_options_removed_by_reset(config, config_path, default_config_string):
    config._config = configparser.ConfigParser()
    new_config = {
        "defaults": {
            "profile": config._default_profile,
            "deck": config._default_deck,
            "folder": config._default_folder,
            "new_option": 123456,
        },
        "anki": {
            "note_type": config._default_basic_type,
            "front_field": config._default_front_field,
            "back_field": config._default_back_field,
        },
        "anki_connect": {"port": config._default_port},
    }
    config._config.read_dict(new_config)
    config._save()

    config.reset()

    with open(config_path, mode="rt", encoding="utf-8") as f:
        assert f.read() == default_config_string
