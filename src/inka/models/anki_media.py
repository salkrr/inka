import filecmp
import os
import shutil
from pathlib import Path
from typing import Union


class AnkiMedia:
    """Class for working with files in Anki Media folder"""

    def __init__(self, anki_profile: str, anki_path: str) -> None:
        self._anki_media_path = f"{anki_path}/{anki_profile}/collection.media"

    def exists(self, file_name: str) -> bool:
        """Check if file exists in Anki Media folder

        Args:
            file_name: name of the file
        Returns:
            bool: True if file exists and False otherwise
        """
        return os.path.exists(f"{self._anki_media_path}/{file_name}")

    def copy_file_from(self, file_path: Union[Path, str]) -> None:
        """Copy file to Anki Media folder.

        Args:
            file_path: path to file that will be copied
        Raises:
            FileNotFoundError: if file_path contains incorrect path
            FileExistsError: if different file with the same name already exists in Anki Media folder
        """
        file_name = os.path.basename(file_path)
        anki_file_path = f"{self._anki_media_path}/{file_name}"
        if self.exists(file_name):
            if filecmp.cmp(file_path, anki_file_path):
                return  # Skip if same file already exists

            raise FileExistsError(
                f'different file with the same name "{file_name}" already exists in Anki Media folder.'
            )

        shutil.copyfile(file_path, anki_file_path)

    def create_file(self, file_name: str, file_content: str) -> None:
        """Create text file in Anki Media folder

        Args:
            file_name: name of the file
            file_content: content of the file
        Raises:
            FileExistsError: if file with the same name already exists in Anki Media folder
        """
        anki_file_path = f"{self._anki_media_path}/{file_name}"
        if self.exists(file_name):
            raise FileExistsError(
                f'file with the name "{file_name}" already exists in Anki Media folder.'
            )

        with open(anki_file_path, "wt", encoding="utf-8") as f:
            f.write(file_content)
