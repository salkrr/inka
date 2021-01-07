import os
import re


class Image:

    def __init__(self, markdown_link):
        self._original_md_link = markdown_link
        self.updated_md_link = markdown_link

    @property
    def original_md_link(self):
        return self._original_md_link

    @property
    def updated_md_link(self):
        return self._updated_md_link

    @updated_md_link.setter
    def updated_md_link(self, new_link):
        self._updated_md_link = new_link
        self._path = re.search(r'(?<=\().+?(?=\))', self._updated_md_link).group()
        self._file_name = os.path.basename(self._path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path
        self._updated_md_link = re.sub(r'(?<=\().+(?=\))', new_path, self._updated_md_link)
        self._file_name = os.path.basename(new_path)

    @property
    def file_name(self):
        return self._file_name

    @property
    def abs_path(self):
        return os.path.abspath(self._path)

    def rename(self, new_file_name):
        """
        Rename original image file

        :param str new_file_name: new name of the file (with extension)
        """
        folder = os.path.dirname(self._path)
        new_path = f'{folder}/{new_file_name}'
        os.rename(self._path, new_path)

        self._file_name = new_file_name
        self._path = new_path
        self._updated_md_link = re.sub(r'(?<=\().+(?=\))', new_path, self._updated_md_link)
