import os
import re
from typing import List, Dict, Optional, Iterable

from .anki_media import AnkiMedia
from .notes.note import Note


def handle_images_in(
    notes: List[Note], anki_media: AnkiMedia, copy_images: bool = True
) -> None:
    """
    Copy images used in Notes fields to Anki Media folder and change source in their
    links to be just filename (for Anki to find them).

    Args:
        notes: Notes in which image links will be searched for and then updated
        anki_media: AnkiMedia object that will be used to copy images
        copy_images: copy images to Anki media folder or not
    """
    # Find all unique image links in the notes
    image_links = _fetch_image_links(notes)

    # Copy images to Anki Media folder
    if copy_images:
        _copy_images_to(anki_media, list(image_links.keys()))

    # Update image links in notes
    _update_image_links_in_notes(image_links)


def _fetch_image_links(notes: List[Note]) -> Dict[str, List[Note]]:
    """Get dictionary of image links with Note objects in which they are used.

    Args:
        notes: Notes in which image links will be searched
    Returns:
        Dictionary with image links as keys and a list of Note objects in which they are used as values
    """
    image_links: Dict[str, List[Note]] = dict()
    image_regex = re.compile(r"!\[.*?]\(.*?\)")
    for note in notes:
        all_found_links = set()
        for field in note.get_raw_fields():
            all_found_links |= set(re.findall(image_regex, field))

        for link in all_found_links:
            if not image_links.get(link):
                image_links[link] = [note]
                continue
            image_links[link].append(note)

    return image_links


def _update_image_links_in_notes(image_links: Dict[str, List[Note]]) -> None:
    """Update image links in Notes. Updated text is stored in updated_front_md and updated_back_md of the Note.

    Args:
        image_links: dictionary with image links as keys and a list of Note objects in which they are used as values
    """
    image_path_regex = re.compile(r"(?<=\().+?(?=\))")
    for link, notes in image_links.items():
        image_filename = _get_filename_from(link)
        if not image_filename:
            continue

        new_link: str = re.sub(image_path_regex, image_filename, link)

        for note in notes:
            # We use *updated* fields for replace func cause
            # we need to preserve previous replacements if there are multiple of them
            note.update_fields_with(lambda field: str.replace(field, link, new_link))


def _copy_images_to(anki_media: AnkiMedia, image_links: Iterable[str]) -> None:
    """Copy images to Anki Media folder.

    Args:
        anki_media: AnkiMedia object that will be used to copy images
        image_links: list of markdown links to images
    Raises:
        FileNotFoundError: if path to image in markdown link is incorrect
        FileExistsError: if different file with the same name already exists in Anki Media folder
    """
    for link in image_links:
        abs_path = _get_abs_path_from(link)
        if not abs_path:
            continue

        try:
            anki_media.copy_file_from(abs_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'cannot find image "{link}" on the path "{abs_path}"'
            )


def _get_path_from(image_link: str) -> Optional[str]:
    """Get path used in markdown's image link.

    Args:
        image_link: markdown image link
    Returns:
        String with path used in markdown's image link
    """
    match = re.search(r"(?<=\().+?(?=\))", image_link)
    if not match:
        return None

    return match.group(0)


def _get_abs_path_from(image_link: str) -> Optional[str]:
    """Get absolute path to image from markdown's image link

    Args:
        image_link: markdown image link
    Returns:
        String with the absolute path to image
    """
    path = _get_path_from(image_link)
    if not path:
        return None

    return os.path.realpath(path)


def _get_filename_from(image_link: str) -> Optional[str]:
    """Get image filename from markdown's image link
    Args:
        image_link: markdown image link
    Returns:
        String with the name of the image
    """
    path = _get_path_from(image_link)
    if not path:
        return None

    return os.path.basename(path)
