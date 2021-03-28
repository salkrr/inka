import configparser
import os
from pathlib import Path
from typing import Union, List


class Config:
    """Class for working with the configuration file."""

    _default_deck = 'Default'
    _default_folder = ''
    _default_profile = ''
    _default_note_type = 'Basic'
    _default_front_field = 'Front'
    _default_back_field = 'Back'
    _default_port = '8765'
    _default_highlight_style = 'monokai'

    def __init__(self, config_path: Union[str, Path]):
        self._config = configparser.ConfigParser()
        self._config_path = config_path

        if not os.path.exists(self._config_path):
            self._create_default()
        else:
            self._read()

    def reset(self):
        """Reset config file to default state"""
        self._config = configparser.ConfigParser()
        self._create_default()

    def _create_default(self):
        """Create default configuration file"""
        config_dict = {
            'defaults': {
                'profile': self._default_profile,
                'deck': self._default_deck,
                'folder': self._default_folder,
            },
            'anki': {
                'note_type': self._default_note_type,
                'front_field': self._default_front_field,
                'back_field': self._default_back_field
            },
            'anki_connect': {
                'port': self._default_port
            },
            'highlight': {
                'style': self._default_highlight_style,
            },
        }

        self._config.read_dict(config_dict)
        self._save()

    def _read(self):
        """Get config from file system"""
        self._config.read(self._config_path)

    def _save(self):
        """Save config state in file system"""
        with open(self._config_path, mode='wt', encoding='utf-8') as file:
            self._config.write(file)

    def get_option_value(self, section: str, key: str) -> str:
        """Get value of the config entry"""
        return self._config[section][key]

    def update_option_value(self, section: str, key: str, new_value: str):
        """Update value of the config entry"""
        if key not in self._config[section]:
            raise KeyError

        self._config[section][key] = new_value
        self._save()

    def get_formatted_options(self) -> List[str]:
        """Get list of formatted key-value entries from the config"""
        formatted_entries = []
        for section in self._config.sections():
            for key, value in self._config[section].items():
                formatted_entries.append(f'{section}.{key} = {value}')

        return formatted_entries

    def __repr__(self):
        return f"{type(self).__name__}(config_path={repr(self._config_path)})"
