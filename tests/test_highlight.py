import pytest
import requests
from requests import HTTPError

from src.inka import highlight
from src.inka.highlight import BASE_URL


@pytest.fixture
def default_styles() -> str:
    return """.card {
  font-family: arial;
  font-size: 20px;
  color: black;
  background-color: white;
}
"""


def test_update_style_in_note_type_when_style_is_empty_string_raises_error(anki_api_mock):
    with pytest.raises(ValueError):
        highlight._update_style_in_note_type(style_name="", anki_api=anki_api_mock)


def test_update_style_in_note_type_uses_anki_api_to_get_current_style(anki_api_mock, default_styles, mocker):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    mocker.patch("requests.get", return_value=mocker.MagicMock())

    highlight._update_style_in_note_type(style_name="monokai", anki_api=anki_api_mock)

    assert anki_api_mock.fetch_note_type_styling.call_count == 1


def test_update_style_in_note_type_uses_requests_to_download_style(anki_api_mock, mocker, default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    style_name = "monokai"
    mocked_get = mocker.patch("requests.get", return_value=mocker.MagicMock())
    url = f"{BASE_URL}/styles/{style_name}.min.css"

    highlight._update_style_in_note_type(style_name=style_name, anki_api=anki_api_mock)

    mocked_get.assert_called_once_with(url)


def test_update_style_in_note_type_skips_when_same_style_already_exists(anki_api_mock, mocker, default_styles):
    mocker.patch("requests.get", return_value=mocker.MagicMock())
    style_name = "monokai"
    start = f"/*STYLE:{style_name} VERSION:{highlight.HLJS_VERSION}*/"
    styles = f"{default_styles}\n{start}\nsomething here\n/*END*/"
    anki_api_mock.fetch_note_type_styling.return_value = styles

    highlight._update_style_in_note_type(style_name=style_name, anki_api=anki_api_mock)

    assert anki_api_mock.update_note_type_styling.call_count == 0


def test_update_style_in_note_type_when_incorrect_style_requested_raises_error(anki_api_mock, default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles

    with pytest.raises(HTTPError):
        highlight._update_style_in_note_type(style_name="i_dont_exist", anki_api=anki_api_mock)


def test_update_style_in_note_type_when_no_highlight_style_generates_new_with_one(anki_api_mock, mocker,
                                                                                  default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    monokai_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}.hljs-keyword,.hljs-literal,.hljs-name,.hljs-selector-tag,.hljs-strong,.hljs-tag{color:#f92672}.hljs-code{color:#66d9ef}.hljs-class .hljs-title{color:#fff}.hljs-attribute,.hljs-link,.hljs-regexp,.hljs-symbol{color:#bf79db}.hljs-addition,.hljs-built_in,.hljs-builtin-name,.hljs-bullet,.hljs-emphasis,.hljs-section,.hljs-selector-attr,.hljs-selector-pseudo,.hljs-string,.hljs-subst,.hljs-template-tag,.hljs-template-variable,.hljs-title,.hljs-type,.hljs-variable{color:#a6e22e}.hljs-comment,.hljs-deletion,.hljs-meta,.hljs-quote{color:#75715e}.hljs-doctag,.hljs-keyword,.hljs-literal,.hljs-section,.hljs-selector-id,.hljs-selector-tag,.hljs-title,.hljs-type{font-weight:700}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = monokai_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlight.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{monokai_style}\n/*END*/"

    highlight._update_style_in_note_type(style_name="monokai", anki_api=anki_api_mock)

    anki_api_mock.update_note_type_styling.assert_called_once_with(expected)


def test_update_style_in_note_type_when_exists_different_highlight_style_replaces_it(
        anki_api_mock, mocker, default_styles
):
    anki_api_mock.fetch_note_type_styling.return_value = \
        f"{default_styles}\n/*STYLE:default VERSION:{highlight.HLJS_VERSION}*/\nsome default style here\n/*END*/"
    style_name = "monokai"
    monokai_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}.hljs-keyword,.hljs-literal,.hljs-name,.hljs-selector-tag,.hljs-strong,.hljs-tag{color:#f92672}.hljs-code{color:#66d9ef}.hljs-class .hljs-title{color:#fff}.hljs-attribute,.hljs-link,.hljs-regexp,.hljs-symbol{color:#bf79db}.hljs-addition,.hljs-built_in,.hljs-builtin-name,.hljs-bullet,.hljs-emphasis,.hljs-section,.hljs-selector-attr,.hljs-selector-pseudo,.hljs-string,.hljs-subst,.hljs-template-tag,.hljs-template-variable,.hljs-title,.hljs-type,.hljs-variable{color:#a6e22e}.hljs-comment,.hljs-deletion,.hljs-meta,.hljs-quote{color:#75715e}.hljs-doctag,.hljs-keyword,.hljs-literal,.hljs-section,.hljs-selector-id,.hljs-selector-tag,.hljs-title,.hljs-type{font-weight:700}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = monokai_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlight.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{monokai_style}\n/*END*/"

    highlight._update_style_in_note_type(style_name=style_name, anki_api=anki_api_mock)

    anki_api_mock.update_note_type_styling.assert_called_once_with(expected)


def test_handle_highlighjs_script_when_no_script_in_anki_media_downloads_one(
        anki_api_mock, anki_media_mock, mocker
):
    anki_media_mock.exists.return_value = False
    response_mock = mocker.MagicMock(spec=requests.Response)
    file_content = "let a = 12;"
    response_mock.text = file_content
    mocked_get = mocker.patch("requests.get", return_value=response_mock)
    expected_url = f"{highlight.BASE_URL}/highlight.min.js"

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    mocked_get.assert_called_once_with(expected_url)
    anki_media_mock.create_file.assert_called_once_with("_hl.pack.js", file_content)


def test_handle_highlighjs_script_when_script_exists_in_anki_media_does_not_download_one(
        anki_api_mock, anki_media_mock, mocker
):
    anki_media_mock.exists.return_value = True
    response_mock = mocker.MagicMock(spec=requests.Response)
    mocked_get = mocker.patch("requests.get", return_value=response_mock)

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    mocked_get.assert_not_called()
    anki_media_mock.assert_not_called()


# TODO: adds usage of script in the end of front and back of note type if it doesn't exist (use mock for anki_api)
def test_handle_highlighjs_script_adds_scripts_to_front_and_back_of_note_type(
        anki_api_mock, anki_media_mock
):
    anki_media_mock.exists.return_value = True
    anki_api_mock.fetch_note_type_fields.return_value = {
        "Front": "{{Front}}",
        "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
    }
    script_elements = f'<script src="_hl.pack.js"></script>\n{highlight.AUTOSTART_SCRIPT}'
    expected = {
        "Front": "{{Front}}" + f"\n{script_elements}",
        "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}" + f"\n{script_elements}"
    }

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_fields.assert_called_once_with(expected)


def test_handle_highlighjs_script_when_front_of_note_type_has_scripts_does_not_add_more_to_it(
        anki_api_mock, anki_media_mock
):
    anki_media_mock.exists.return_value = True
    script_elements = f'<script src="_hl.pack.js"></script>\n{highlight.AUTOSTART_SCRIPT}'
    front_value = "{{Front}}" + f"\n{script_elements}"
    anki_api_mock.fetch_note_type_fields.return_value = {
        "Front": front_value,
        "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}"
    }
    expected = {
        "Front": front_value,
        "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}" + f"\n{script_elements}"
    }

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_fields.assert_called_once_with(expected)


def test_handle_highlighjs_script_when_back_of_note_type_has_scripts_does_not_add_more_to_it(
        anki_api_mock, anki_media_mock
):
    anki_media_mock.exists.return_value = True
    script_elements = f'<script src="_hl.pack.js"></script>\n{highlight.AUTOSTART_SCRIPT}'
    back_value = "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}" + f"\n{script_elements}"
    anki_api_mock.fetch_note_type_fields.return_value = {
        "Front": "{{Front}}",
        "Back": back_value
    }
    expected = {
        "Front": "{{Front}}" + f"\n{script_elements}",
        "Back": back_value
    }

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_fields.assert_called_once_with(expected)


def test_handle_highlighjs_script_if_fields_have_not_change_no_update_request_sent(
        anki_api_mock, anki_media_mock
):
    anki_media_mock.exists.return_value = True
    script_elements = f'<script src="_hl.pack.js"></script>\n{highlight.AUTOSTART_SCRIPT}'
    anki_api_mock.fetch_note_type_fields.return_value = {
        "Front": "{{Front}}" + f"\n{script_elements}",
        "Back": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}" + f"\n{script_elements}"
    }

    highlight._handle_highlighjs_script(anki_media_mock, anki_api_mock)

    anki_api_mock.update_note_type_fields.assert_not_called()
