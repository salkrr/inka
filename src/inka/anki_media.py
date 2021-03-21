import os
import shutil
import sys
from pathlib import Path
from typing import Union

DEFAULT_ANKI_FOLDERS = {
    'win32': r'~\AppData\Roaming\Anki2',
    'linux': '~/.local/share/Anki2',
    'darwin': '~/Library/Application Support/Anki2'
}


class AnkiMedia:
    """Class for working with files in Anki Media folder"""

    def __init__(self, anki_profile: str) -> None:
        anki_folder_path = os.path.expanduser(DEFAULT_ANKI_FOLDERS[sys.platform])
        self._anki_media_path = f'{anki_folder_path}/{anki_profile}/collection.media'

    def exists(self, file_name: str) -> bool:
        """Check if file exists in Anki Media folder

        Args:
            file_name: name of the file
        Returns:
            bool: True if file exists and False otherwise
        """
        return os.path.exists(f'{self._anki_media_path}/{file_name}')

    def copy_file_from(self, file_path: Union[Path, str]) -> None:
        """Copy file to Anki Media folder

        Args:
            file_path: path to file that will be copied
        Raises:
            FileNotFoundError: if file_path contains incorrect path
            SameFileError: if same file already exists in Anki Media folder
            OSError: if different file with the same name already exists in Anki Media folder
        """
        file_name = os.path.basename(file_path)
        if self.exists(file_name):
            raise OSError(f'File with the name "{file_name}" already exists in Anki Media folder.')

        shutil.copyfile(file_path, f'{self._anki_media_path}/{file_name}')

    def create_file(self, file_name: str, file_content: str) -> None:
        """Create text file in Anki Media folder

        Args:
            file_name: name of the file
            file_content: content of the file
        Raises:
            OSError: if a file with the same name already exists
        """
        anki_file_path = f'{self._anki_media_path}/{file_name}'
        if self.exists(file_name):
            raise OSError(f'File with the name "{file_name}" already exists in Anki Media folder.')

        with open(anki_file_path, 'wt', encoding='utf-8') as f:
            f.write(file_content)
