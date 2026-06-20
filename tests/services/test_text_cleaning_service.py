from __future__ import annotations

from app.services.text_cleaning_service import TextCleaningService


def test_returns_empty_string_for_empty_input() -> None:
    service = TextCleaningService()

    assert service.clean("") == ""
    assert service.clean("   ") == ""
    assert service.clean("\n\n") == ""


def test_normalizes_windows_and_mac_line_breaks() -> None:
    service = TextCleaningService()

    text = "line1\r\nline2\rline3"

    result = service.clean(text)

    assert result == "line1\nline2\nline3"


def test_removes_control_characters() -> None:
    service = TextCleaningService()

    text = "hello\x00world\x07test\x1f"

    result = service.clean(text)

    assert result == "helloworldtest"


def test_normalizes_whitespace() -> None:
    service = TextCleaningService()

    text = "hello     world\t\tfoo\vbar"

    result = service.clean(text)

    assert result == "hello world foobar"


def test_strips_lines_and_preserves_structure() -> None:
    service = TextCleaningService()

    text = """
        line one

            line two

        line three
    """

    result = service.clean(text)

    assert result == "line one\n\nline two\n\nline three"


def test_collapses_multiple_blank_lines() -> None:
    service = TextCleaningService()

    text = "line1\n\n\n\n\nline2"

    result = service.clean(text)

    assert result == "line1\n\nline2"


def test_trims_leading_and_trailing_whitespace() -> None:
    service = TextCleaningService()

    text = "   hello world   "

    result = service.clean(text)

    assert result == "hello world"


def test_combines_all_cleaning_steps() -> None:
    service = TextCleaningService()

    text = """
        hello\x00     world\r\n\r\n\r\n

            foo\t\tbar

    """

    result = service.clean(text)

    assert result == "hello world\n\nfoo bar"
