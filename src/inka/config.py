import configparser
import os
from pathlib import Path
from typing import Union


class Config:
    _default_deck = 'Default'
    _default_folder = ''
    _default_profile = ''
    _default_note_type = 'Basic'
    _default_front_field = 'Front'
    _default_back_field = 'Back'
    _default_port = '8765'

    def __init__(self, config_path: Union[str, Path]):
        self._config = configparser.ConfigParser()
        self._config_path = config_path

        if not os.path.exists(self._config_path):
            self._create_default()
        else:
            self._read()

    def _create_default(self):
        """Create default configuration file"""
        self._config['defaults'] = {
            'deck': self._default_deck,
            'folder': self._default_folder
        }
        self._config['anki'] = {
            'profile': self._default_profile,
            'note_type': self._default_note_type,
            'front_field': self._default_front_field,
            'back_field': self._default_back_field
        }
        self._config['anki_connect'] = {
            'port': self._default_port
        }

        self._save()

    def _read(self):
        """Get config from file system"""
        self._config.read(self._config_path)

    def _save(self):
        """Save config state in file system"""
        with open(self._config_path, mode='wt', encoding='utf-8') as file:
            self._config.write(file)

    def get_entry_value(self, section: str, key: str) -> str:
        """Get value of the config entry"""
        return self._config[section][key]
