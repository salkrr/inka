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
        highlight.update_style_in_note_type(style_name="", anki_api=anki_api_mock)


def test_update_style_in_note_type_uses_anki_api_to_get_current_style(anki_api_mock, default_styles, mocker):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    mocker.patch("requests.get", return_value=mocker.MagicMock())

    highlight.update_style_in_note_type(style_name="monokai", anki_api=anki_api_mock)

    assert anki_api_mock.fetch_note_type_styling.call_count == 1


def test_update_style_in_note_type_uses_requests_to_download_style(anki_api_mock, mocker, default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    style_name = "monokai"
    mocked_get = mocker.patch("requests.get", return_value=mocker.MagicMock())
    url = f"{BASE_URL}/styles/{style_name}.min.css"

    highlight.update_style_in_note_type(style_name=style_name, anki_api=anki_api_mock)

    mocked_get.assert_called_once_with(url)


def test_update_style_in_note_type_skips_when_same_style_already_exists(anki_api_mock, mocker, default_styles):
    mocker.patch("requests.get", return_value=mocker.MagicMock())
    style_name = "monokai"
    start = f"/*STYLE:{style_name} VERSION:{highlight.HLJS_VERSION}*/"
    styles = f"{default_styles}\n{start}\nsomething here\n/*END*/"
    anki_api_mock.fetch_note_type_styling.return_value = styles

    highlight.update_style_in_note_type(style_name=style_name, anki_api=anki_api_mock)

    assert anki_api_mock.update_note_type_styling.call_count == 0


def test_update_style_in_note_type_when_incorrect_style_requested_raises_error(anki_api_mock, mocker, default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles

    with pytest.raises(HTTPError):
        highlight.update_style_in_note_type(style_name="i_dont_exist", anki_api=anki_api_mock)


def test_update_style_in_note_type_when_no_highlight_style_generates_new_with_one(anki_api_mock, mocker,
                                                                                  default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = default_styles
    monokai_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}.hljs-keyword,.hljs-literal,.hljs-name,.hljs-selector-tag,.hljs-strong,.hljs-tag{color:#f92672}.hljs-code{color:#66d9ef}.hljs-class .hljs-title{color:#fff}.hljs-attribute,.hljs-link,.hljs-regexp,.hljs-symbol{color:#bf79db}.hljs-addition,.hljs-built_in,.hljs-builtin-name,.hljs-bullet,.hljs-emphasis,.hljs-section,.hljs-selector-attr,.hljs-selector-pseudo,.hljs-string,.hljs-subst,.hljs-template-tag,.hljs-template-variable,.hljs-title,.hljs-type,.hljs-variable{color:#a6e22e}.hljs-comment,.hljs-deletion,.hljs-meta,.hljs-quote{color:#75715e}.hljs-doctag,.hljs-keyword,.hljs-literal,.hljs-section,.hljs-selector-id,.hljs-selector-tag,.hljs-title,.hljs-type{font-weight:700}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = monokai_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlight.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{monokai_style}\n/*END*/"

    highlight.update_style_in_note_type(style_name="monokai", anki_api=anki_api_mock)

    anki_api_mock.update_note_type_styling.assert_called_once_with(expected)


def test_update_style_in_note_type_when_exists_different_highlight_style_replaces_it(anki_api_mock, mocker,
                                                                                     default_styles):
    anki_api_mock.fetch_note_type_styling.return_value = \
        f"{default_styles}\n/*STYLE:default VERSION:{highlight.HLJS_VERSION}*/\nsome default style here\n/*END*/"
    monokai_style = ".hljs{display:block;overflow-x:auto;padding:.5em;background:#272822;color:#ddd}.hljs-keyword,.hljs-literal,.hljs-name,.hljs-selector-tag,.hljs-strong,.hljs-tag{color:#f92672}.hljs-code{color:#66d9ef}.hljs-class .hljs-title{color:#fff}.hljs-attribute,.hljs-link,.hljs-regexp,.hljs-symbol{color:#bf79db}.hljs-addition,.hljs-built_in,.hljs-builtin-name,.hljs-bullet,.hljs-emphasis,.hljs-section,.hljs-selector-attr,.hljs-selector-pseudo,.hljs-string,.hljs-subst,.hljs-template-tag,.hljs-template-variable,.hljs-title,.hljs-type,.hljs-variable{color:#a6e22e}.hljs-comment,.hljs-deletion,.hljs-meta,.hljs-quote{color:#75715e}.hljs-doctag,.hljs-keyword,.hljs-literal,.hljs-section,.hljs-selector-id,.hljs-selector-tag,.hljs-title,.hljs-type{font-weight:700}"
    response_mock = mocker.MagicMock(spec=requests.Response)
    response_mock.text = monokai_style
    mocker.patch("requests.get", return_value=response_mock)
    start = f"/*STYLE:monokai VERSION:{highlight.HLJS_VERSION}*/"
    expected = f"{default_styles}\n{start}\n{monokai_style}\n/*END*/"

    highlight.update_style_in_note_type(style_name="monokai", anki_api=anki_api_mock)

    anki_api_mock.update_note_type_styling.assert_called_once_with(expected)
