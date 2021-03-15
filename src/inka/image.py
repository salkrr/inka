import os
import re
from pathlib import Path
from typing import Union


class Image:

    def __init__(self, markdown_link: str):
        self._initial_md_link = markdown_link
        self._current_md_link = markdown_link

    @property
    def initial_md_link(self) -> str:
        """Initial markdown link to the image"""
        return self._initial_md_link

    @property
    def current_md_link(self) -> str:
        """Current markdown link to the image"""
        return self._current_md_link

    @current_md_link.setter
    def current_md_link(self, new_link: str) -> None:
        self._current_md_link = new_link

    @property
    def path(self) -> str:
        """Path to image from markdown image link"""
        return re.search(r'(?<=\().+?(?=\))', self._current_md_link).group()

    @path.setter
    def path(self, new_path: Union[str, Path]) -> None:
        self.current_md_link = re.sub(r'(?<=\().+(?=\))', new_path, self._current_md_link)

    @property
    def abs_path(self) -> str:
        """Absolute path to the image"""
        return os.path.realpath(self.path)

    @property
    def file_name(self) -> str:
        """File name of the image"""
        return os.path.basename(self.path)

    def rename(self, new_file_name: str) -> None:
        """
        Rename the original image file and update its markdown links in file

        Args:
            new_file_name: new name of the file (with extension)
        """
        # TODO: update links in file
        folder = os.path.dirname(self.path)
        new_path = f'{folder}/{new_file_name}'
        os.rename(self.path, new_path)
        self.current_md_link = re.sub(r'(?<=\().+(?=\))', new_path, self._current_md_link)
