import pytest

from msfpatterns import find_offset, generate_pattern


def test_generate_pattern_length() -> None:
    """Ensure generated pattern has correct length."""
    length = 64
    pattern = generate_pattern(length)
    assert len(pattern) == length


def test_generate_pattern_content() -> None:
    """Ensure the pattern is generated as expected."""
    pattern = generate_pattern(64)
    assert pattern == "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0A"


@pytest.mark.parametrize(
    ("query", "expected_offsets"),
    [
        (
            "0x6241",
            [30, 33, 36, 39, 42, 45, 48, 51, 54, 57],
        ),
        ("0x41306241", [30]),
        ("0x6241316241306241", [30]),
        (
            "Ab",
            [30, 33, 36, 39, 42, 45, 48, 51, 54, 57],
        ),
        ("Ab0A", [30]),
        ("Ab0Ab1Ab", [30]),
        ("XXXX", []),
    ],
)
def test_find_offset(query: str, expected_offsets: list[int]) -> None:
    assert find_offset(query, 256) == expected_offsets


@pytest.mark.parametrize(
    ("query", "expected_message"),
    [
        (
            "A",
            "Input must be a 2-character, 4-character, or 8-character string or hexadecimal equivalent.",
        ),
        (
            "ABC",
            "Input must be a 2-character, 4-character, or 8-character string or hexadecimal equivalent.",
        ),
        (
            "ABCDEFGHI",
            "Input must be a 2-character, 4-character, or 8-character string or hexadecimal equivalent.",
        ),
        (
            "0x4142A",
            r"Hex value must be exactly 4, 8, or 16 hex digits \(2, 4, or 8 bytes\).",
        ),
        ("0xGGGG", "Invalid hexadecimal input: 0xGGGG."),
    ],
)
def test_find_offset_invalid_input(query: str, expected_message: str) -> None:
    """Ensure invalid input types raise ValueError with exact error messages."""
    with pytest.raises(ValueError, match=expected_message):
        find_offset(query, 256)
