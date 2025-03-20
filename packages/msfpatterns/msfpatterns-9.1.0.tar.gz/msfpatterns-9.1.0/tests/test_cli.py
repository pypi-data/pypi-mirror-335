import pytest

from msfpatterns.cli import main


def test_cli_generate_pattern(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the CLI pattern generation command."""
    length = 16
    monkeypatch.setattr("sys.argv", ["msfpatterns", str(length)])

    main()

    captured = capsys.readouterr()
    assert len(captured.out.strip()) == length


def test_cli_find_offset_valid(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test finding an offset from a known pattern."""
    monkeypatch.setattr("sys.argv", ["msfpatterns", "256", "-q", "Ab0A"])

    main()

    captured = capsys.readouterr()
    assert captured.out == "[*] Found 1 occurrence at offset: 30\n"


def test_cli_find_offset_not_found(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test searching for a non-existent pattern."""
    monkeypatch.setattr("sys.argv", ["msfpatterns", "256", "-q", "XXXX"])

    main()

    captured = capsys.readouterr()
    assert captured.out == "[x] Value not found in the pattern.\n"
