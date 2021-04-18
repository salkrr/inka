import os

import pytest

from inka.models import img_handler
from inka.models.notes.basic_note import BasicNote


def test_fetch_image_links_if_cards_do_not_have_images():
    card1 = BasicNote(front_md="Some text", back_md="Another text", tags=[], deck_name="deck")
    card2 = BasicNote(front_md="More\n\nText", back_md="Answer text", tags=[], deck_name="deck")

    links = img_handler._fetch_image_links([card1, card2])

    assert {} == links


def test_fetch_image_links_if_cards_have_images():
    image1 = "![](path/to/img1.png)"
    image2 = "![](img2.png)"
    card1 = BasicNote(front_md="Some text", back_md=f"Another text\n\n{image1}", tags=[], deck_name="deck")
    card2 = BasicNote(front_md=f"More\n\n{image2}", back_md="Answer text", tags=[], deck_name="deck")
    expected = {
        image1: [card1],
        image2: [card2]
    }

    links = img_handler._fetch_image_links([card1, card2])

    assert expected == links


def test_fetch_image_links_if_cards_have_same_image():
    image = "![](path/to/img1.png)"
    card1 = BasicNote(front_md="Some text", back_md=f"Another text\n\n{image}", tags=[], deck_name="deck")
    card2 = BasicNote(front_md=f"More\n\n{image}", back_md="Answer text", tags=[], deck_name="deck")
    expected = {
        image: [card1, card2]
    }

    links = img_handler._fetch_image_links([card1, card2])

    assert expected == links


def test_update_image_links_when_no_image_links():
    card1 = BasicNote(front_md="Some text", back_md="Another text", tags=[], deck_name="deck")
    card2 = BasicNote(front_md="More\n\nText", back_md="Answer text", tags=[], deck_name="deck")
    cards = [card1, card2]

    img_handler._update_image_links_in_notes({})

    for card in cards:
        assert card.raw_front_md == card.updated_front_md
        assert card.raw_back_md == card.updated_back_md


def test_update_image_links_when_card_has_image_link():
    image = "![](path/to/img1.png)"
    card = BasicNote(front_md=f"Some {image} text", back_md=f"Another text\n\n{image}", tags=[], deck_name="deck")
    image_links = {
        image: [card]
    }
    expected_front = "Some ![](img1.png) text"
    expected_back = "Another text\n\n![](img1.png)"

    img_handler._update_image_links_in_notes(image_links)

    assert expected_front == card.updated_front_md
    assert expected_back == card.updated_back_md


def test_update_image_links_when_card_has_different_image_links():
    image1 = "![](path/to/img1.png)"
    image2 = "![](images/image2.png)"
    card = BasicNote(front_md=f"{image2}\n\nSome {image1} text",
                     back_md=f"Another text\n\n{image1}\n{image2}",
                     tags=[], deck_name="deck")
    image_links = {
        image1: [card],
        image2: [card]
    }
    expected_front = "![](image2.png)\n\nSome ![](img1.png) text"
    expected_back = "Another text\n\n![](img1.png)\n![](image2.png)"

    img_handler._update_image_links_in_notes(image_links)

    assert expected_front == card.updated_front_md
    assert expected_back == card.updated_back_md


def test_update_image_links_in_several_cards_with_same_images():
    image1 = "![](path/to/img1.png)"
    image2 = "![](images/image2.png)"
    card1 = BasicNote(front_md=f"{image2}\n\nSome {image1} text",
                      back_md=f"Another text\n\n{image1}\n{image2}",
                      tags=[], deck_name="deck")
    card2 = BasicNote(front_md=f"{image2}Some text {image1}",
                      back_md=f"{image1} {image2}\n\nAnother text\n\n",
                      tags=[], deck_name="deck")
    image_links = {
        image1: [card1, card2],
        image2: [card2, card1]
    }
    expected_front1 = "![](image2.png)\n\nSome ![](img1.png) text"
    expected_back1 = "Another text\n\n![](img1.png)\n![](image2.png)"
    expected_front2 = "![](image2.png)Some text ![](img1.png)"
    expected_back2 = "![](img1.png) ![](image2.png)\n\nAnother text\n\n"

    img_handler._update_image_links_in_notes(image_links)

    assert expected_front1 == card1.updated_front_md
    assert expected_back1 == card1.updated_back_md
    assert expected_front2 == card2.updated_front_md
    assert expected_back2 == card2.updated_back_md


# Copy images
def test_copy_images_to_with_one_image_link(anki_media, image, path_to_anki_image):
    img_handler._copy_images_to(anki_media, [f"![some image]({image})"])

    assert os.path.exists(path_to_anki_image)


def test_copy_images_to_with_multiple_image_links(anki_media,
                                                  image,
                                                  path_to_anki_image,
                                                  another_image,
                                                  path_to_another_anki_image):
    img_handler._copy_images_to(anki_media, [f"![some image]({image})", f"![some image]({another_image})"])

    assert os.path.exists(path_to_anki_image)
    assert os.path.exists(path_to_another_anki_image)


def test_copy_images_to_with_non_existing_image_raises_error(anki_media):
    with pytest.raises(FileNotFoundError):
        img_handler._copy_images_to(anki_media, ['![](/path/to/non-existing.png)'])


def test_copy_images_to_when_exists_different_image_with_same_name_raises_error(anki_media, image, image_anki):
    with pytest.raises(FileExistsError):
        img_handler._copy_images_to(anki_media, [f"![some image]({image})"])


def test_handle_images_if_no_images_then_fields_remain_same(anki_media):
    card = BasicNote("Some text", "Another text", tags=[], deck_name="deck")

    img_handler.handle_images_in([card], anki_media)

    assert card.updated_front_md == card.raw_front_md


def test_handle_images_when_cards_have_images(anki_media, image, another_image):
    image_link1 = f"![some image]({image})"
    image_link2 = f"![another img]({another_image})"
    card1 = BasicNote(f"Some text {image_link1}", f"{image_link2} Another text", tags=[], deck_name="deck")
    card2 = BasicNote("Question here", f"And answer here {image_link2}", tags=[], deck_name="deck")
    expected_front1 = f"Some text ![some image]({os.path.basename(image)})"
    expected_front2 = "Question here"
    expected_back1 = f"![another img]({os.path.basename(another_image)}) Another text"
    expected_back2 = f"And answer here ![another img]({os.path.basename(another_image)})"

    img_handler.handle_images_in([card1, card2], anki_media)

    assert expected_front1 == card1.raw_front_md
    assert expected_front2 == card2.raw_front_md
    assert expected_back1 == card1.raw_back_md
    assert expected_back2 == card2.raw_back_md


def test_handle_images_copies_images_to_anki_media(anki_media, image, path_to_anki_image):
    card = BasicNote("Some text", f"Another text ![img]({image})", tags=[], deck_name="deck")

    img_handler.handle_images_in([card], anki_media)

    os.path.exists(path_to_anki_image)
