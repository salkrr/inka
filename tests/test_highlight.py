import pytest
import requests
from requests import HTTPError

from inka.models import highlighter
from inka.models.highlighter import BASE_URL
from inka.models.notes.note import Note


@pytest.fixture
def default_styles() -> str:
    return """.card {
  font-family: arial;
  font-size: 20px;
  color: black;
  background-color: white;
}
"""


def test_update_style_in_note_type_when_style_is_empty_string_raises_error(
    anki_api_mock,
):
    with pytest.raises(ValueError):
        highlighter._update_style_in(
            note_type=Note, style_name="", anki_api=anki_api_mock
        )


def test_update_style_in_note_type_uses_anki_api_to_get_current_style(
    anki_api_mock, default_styles, mocker
):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    mocker.patch("requests.get", return_value=mocker.MagicMock())

    highlighter._update_style_in(
        note_type=Note, style_name="monokai", anki_api=anki_api_mock
    )

    assert anki_api_mock.fetch_note_type_styling.call_count == 1


def test_update_style_in_note_type_uses_requests_to_download_style(
    anki_api_mock, mocker, default_styles
):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    style_name = "monokai"
    mocked_get = mocker.patch("requests.get", return_value=mocker.MagicMock())
    url = f"{BASE_URL}/styles/{style_name}.min.css"

    highlighter._update_style_in(
        note_type=Note, style_name=style_name, anki_api=anki_api_mock
    )

    mocked_get.assert_called_once_with(url)


def test_update_style_in_note_type_skips_when_same_style_already_exists(
    anki_api_mock, mocker, default_styles
):
    mocker.patch("requests.get", return_value=mocker.MagicMock())
    style_name = "monokai"
    start = f"/*STYLE:{style_name} VERSION:{highlighter.HLJS_VERSION}*/"
    styles = f"{default_styles}\n{start}\nsomething here\n/*END*/"
    anki_api_mock.fetch_note_type_styling.return_value = styles

    highlighter._update_style_in(
        note_type=Note, style_name=style_name, anki_api=anki_api_mock
    )

    assert anki_api_mock.update_note_type_styling.call_count == 0


def test_update_style_in_note_type_when_incorrect_style_requested_raises_error(
    anki_api_mock, default_styles
):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles

    with pytest.raises(HTTPError):
        highlighter._update_style_in(
            note_type=Note, style_name="i_dont_exist", anki_api=anki_api_mock
        )


def test_update_style_in_note_type_when_no_highlight_style_generates_new_with_one(
    anki_api_mock, mocker, default_styles
):
    note_type = Note
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    some_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = some_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlighter.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{some_style}\n/*END*/"

    highlighter._update_style_in(
        note_type=note_type, style_name="monokai", anki_api=anki_api_mock
    )

    anki_api_mock.update_note_type_styling.assert_called_once_with(note_type, expected)


def test_update_style_in_note_type_when_exists_different_highlight_style_replaces_it(
    anki_api_mock, mocker, default_styles
):
    anki_api_mock.fetch_note_type_styling.return_value = (
        f"{default_styles}\n/*STYLE:default VERSION:{highlighter.HLJS_VERSION}*/\n"
        f"some default style here\n"
        f"/*END*/"
    )
    style_name = "monokai"
    note_type = Note
    some_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = some_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlighter.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{some_style}\n/*END*/"

    highlighter._update_style_in(
        note_type=note_type, style_name=style_name, anki_api=anki_api_mock
    )

    anki_api_mock.update_note_type_styling.assert_called_once_with(note_type, expected)


def test_handle_highlighjs_script_when_no_script_in_anki_media_downloads_one(
    anki_api_mock, anki_media_mock, mocker
):
    anki_media_mock.exists.return_value = False
    response_mock = mocker.MagicMock(spec=requests.Response)
    file_content = "let a = 12;"
    response_mock.text = file_content
    mocked_get = mocker.patch("requests.get", return_value=response_mock)
    expected_url = f"{highlighter.BASE_URL}/highlight.min.js"

    highlighter._handle_highlighjs_files_for(Note, anki_media_mock, anki_api_mock)

    mocked_get.assert_called_once_with(expected_url)
    anki_media_mock.create_file.assert_called_once_with("_hl.pack.js", file_content)


def test_handle_highlighjs_script_when_script_exists_in_anki_media_does_not_download_one(
    anki_api_mock, anki_media_mock, mocker
):
    anki_media_mock.exists.return_value = True
    response_mock = mocker.MagicMock(spec=requests.Response)
    mocked_get = mocker.patch("requests.get", return_value=response_mock)

    highlighter._handle_highlighjs_files_for(Note, anki_media_mock, anki_api_mock)

    mocked_get.assert_not_called()
    anki_media_mock.assert_not_called()


def test_handle_highlighjs_script_adds_scripts_to_front_and_back_of_note_type(
    anki_api_mock, anki_media_mock
):
    note_type = Note
    anki_media_mock.exists.return_value = True
    anki_api_mock.fetch_note_type_templates.return_value = {
        "Card 1": {
            "Front": "{{Front}}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
        }
    }
    script_elements = (
        f'<script src="_hl.pack.js"></script>\n{highlighter.AUTOSTART_SCRIPT}'
    )
    expected = {
        "Card 1": {
            "Front": "{{Front}}" + f"\n{script_elements}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
            + f"\n{script_elements}",
        }
    }

    highlighter._handle_highlighjs_files_for(note_type, anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_templates.assert_called_once_with(
        note_type, expected
    )


def test_handle_highlighjs_script_when_front_of_note_type_has_scripts_does_not_add_more_to_it(
    anki_api_mock, anki_media_mock
):
    note_type = Note
    anki_media_mock.exists.return_value = True
    script_elements = (
        f'<script src="_hl.pack.js"></script>\n{highlighter.AUTOSTART_SCRIPT}'
    )
    front_value = "{{Front}}" + f"\n{script_elements}"
    anki_api_mock.fetch_note_type_templates.return_value = {
        "Card 1": {
            "Front": front_value,
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
        }
    }
    expected = {
        "Card 1": {
            "Front": front_value,
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
            + f"\n{script_elements}",
        }
    }

    highlighter._handle_highlighjs_files_for(note_type, anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_templates.assert_called_once_with(
        note_type, expected
    )


def test_handle_highlighjs_script_when_back_of_note_type_has_scripts_does_not_add_more_to_it(
    anki_api_mock, anki_media_mock
):
    note_type = Note
    anki_media_mock.exists.return_value = True
    script_elements = (
        f'<script src="_hl.pack.js"></script>\n{highlighter.AUTOSTART_SCRIPT}'
    )
    back_value = "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}" + f"\n{script_elements}"
    anki_api_mock.fetch_note_type_templates.return_value = {
        "Card 1": {"Front": "{{Front}}", "Back": back_value}
    }
    expected = {
        "Card 1": {"Front": "{{Front}}" + f"\n{script_elements}", "Back": back_value}
    }

    highlighter._handle_highlighjs_files_for(note_type, anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_templates.assert_called_once_with(
        note_type, expected
    )


def test_handle_highlighjs_script_if_fields_have_not_change_no_update_request_sent(
    anki_api_mock, anki_media_mock
):
    anki_media_mock.exists.return_value = True
    script_elements = (
        f'<script src="_hl.pack.js"></script>\n{highlighter.AUTOSTART_SCRIPT}'
    )
    anki_api_mock.fetch_note_type_templates.return_value = {
        "Card 1": {
            "Front": "{{Front}}" + f"\n{script_elements}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
            + f"\n{script_elements}",
        }
    }

    highlighter._handle_highlighjs_files_for(Note, anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_templates.assert_not_called()


def test_handle_highlighjs_script_adds_scripts_to_multiple_templates(
    anki_api_mock, anki_media_mock
):
    note_type = Note
    anki_media_mock.exists.return_value = True
    anki_api_mock.fetch_note_type_templates.return_value = {
        "Card 1": {
            "Front": "{{Front}}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
        },
        "Different": {"Front": "{{Front}} {{Front}}", "Back": "{{Back}}"},
    }
    script_elements = (
        f'<script src="_hl.pack.js"></script>\n{highlighter.AUTOSTART_SCRIPT}'
    )
    expected = {
        "Card 1": {
            "Front": "{{Front}}" + f"\n{script_elements}",
            "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
            + f"\n{script_elements}",
        },
        "Different": {
            "Front": "{{Front}} {{Front}}" + f"\n{script_elements}",
            "Back": "{{Back}}" + f"\n{script_elements}",
        },
    }

    highlighter._handle_highlighjs_files_for(note_type, anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_templates.assert_called_once_with(
        note_type, expected
    )
