import os
import re
from typing import List, Dict, Optional

from .anki_media import AnkiMedia
from .card import Card


def handle_images_in(cards: List[Card], anki_media: AnkiMedia) -> None:
    """
    Copy images used in Cards fields to Anki Media folder and change source in their
    links to be just filename (for Anki to find them).

    Args:
        cards: Cards in which image links will be searched for and then updated
        anki_media: AnkiMedia object that will be used to copy images
    """
    # Find all unique image links in the cards
    image_links = _fetch_image_links(cards)

    # Copy images to Anki Media folder
    _copy_images_to(anki_media, list(image_links.keys()))

    # Update image links in cards
    _update_image_links_in_cards(image_links)


def _fetch_image_links(cards: List[Card]) -> Dict[str, List[Card]]:
    """Get dictionary of image links with cards in which they are used.

    Args:
        cards: Cards in which image links will be searched
    Returns:
        Dictionary with image links as keys and a list of cards in which they are used as values
    """
    image_links = dict()
    image_regex = re.compile(r'!\[.*?]\(.*?\)')
    for card in cards:
        found_links_front = set(re.findall(image_regex, card.front_md))
        found_links_back = set(re.findall(image_regex, card.back_md))
        all_found_links = found_links_front.union(found_links_back)

        for link in all_found_links:
            if not image_links.get(link):
                image_links[link] = [card]
                continue
            image_links[link].append(card)

    return image_links


def _update_image_links_in_cards(image_links: Dict[str, List[Card]]) -> None:
    """Update image links in Cards. Updated text is stored in updated_front_md and updated_back_md of the Card.

    Args:
        image_links: dictionary with image links as keys and a list of cards in which they are used as values
    """
    image_path_regex = re.compile(r'(?<=\().+?(?=\))')
    for link, cards in image_links.items():
        image_filename = _get_filename_from(link)
        new_link = re.sub(image_path_regex, image_filename, link)

        for card in cards:
            card.updated_front_md = card.updated_front_md.replace(link, new_link)
            card.updated_back_md = card.updated_back_md.replace(link, new_link)


def _copy_images_to(anki_media: AnkiMedia, image_links: List[str]) -> None:
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
        try:
            anki_media.copy_file_from(abs_path)
        except FileNotFoundError:
            raise FileNotFoundError(f'Cannot find image "{link}" on the path "{abs_path}"')


def _get_path_from(image_link: str) -> Optional[str]:
    """Get path used in markdown's image link.

    Args:
        image_link: markdown image link
    Returns:
        String with path used in markdown's image link
    """
    return re.search(r'(?<=\().+?(?=\))', image_link).group()


def _get_abs_path_from(image_link: str) -> Optional[str]:
    """Get absolute path to image from markdown's image link

    Args:
        image_link: markdown image link
    Returns:
        String with the absolute path to image
    """
    return os.path.realpath(
        _get_path_from(image_link)
    )


def _get_filename_from(image_link: str) -> Optional[str]:
    """Get image filename from markdown's image link
    Args:
        image_link: markdown image link
    Returns:
        String with the name of the image
    """
    return os.path.basename(
        _get_path_from(image_link)
    )
