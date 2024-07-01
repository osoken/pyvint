from io import BytesIO

import pytest

from pyvint import core


@pytest.mark.parametrize(
    ("vint", "expected"),
    (
        (b"\x82", 2),
        (b"\x40\x03", 3),
        (b"\x20\x00\x05", 5),
        (b"\x10\x00\x00\x08", 8),
        (b"\x08\x00\x00\x00\x0d", 13),
        (b"\x04\x00\x00\x00\x00\x15", 21),
        (b"\x02\x00\x00\x00\x00\x00\x22", 34),
        (b"\x01\x00\x00\x00\x00\x00\x00\x37", 55),
        (b"\x00\x80\x00\x00\x00\x00\x00\x00\x59", 89),
        (b"\x00\x11\x04\xc4\x31\x49\x08\xfb\xb7\xd9\x86\xb6", 1231434398764213200324278),
        (b"\x1a\x45\xdf\xa3", 172351395),
    ),
)
def test_decode(vint: bytes, expected: int) -> None:
    assert core.decode(vint) == expected


def test_decode_invalid_too_short() -> None:
    with pytest.raises(ValueError, match="Invalid VINT."):
        core.decode(b"\x01")


def test_decode_invalid_too_long() -> None:
    with pytest.raises(ValueError, match="Invalid VINT."):
        core.decode(b"\x80\x01")


@pytest.mark.parametrize(
    ("vint", "expected", "remainder"),
    (
        (b"\x82", 2, b""),
        (b"\x40\x03", 3, b""),
        (b"\x20\x00\x05", 5, b""),
        (b"\x10\x00\x00\x08", 8, b""),
        (b"\x08\x00\x00\x00\x0d", 13, b""),
        (b"\x04\x00\x00\x00\x00\x15", 21, b""),
        (b"\x02\x00\x00\x00\x00\x00\x22", 34, b""),
        (b"\x01\x00\x00\x00\x00\x00\x00\x37", 55, b""),
        (b"\x00\x80\x00\x00\x00\x00\x00\x00\x59", 89, b""),
        (b"\x00\x11\x04\xc4\x31\x49\x08\xfb\xb7\xd9\x86\xb6\x00\x12", 1231434398764213200324278, b"\x00\x12"),
        (b"\x1a\x45\xdf\xa3\x9f\x39\x86\x81\x01\x39", 172351395, b"\x9f\x39\x86\x81\x01\x39"),
    ),
)
def test_decode_stream(vint: bytes, expected: int, remainder: bytes) -> None:
    stream = BytesIO(vint)
    actual = core.decode_stream(stream=stream)
    assert actual == expected
    assert stream.read() == remainder


def test_decode_stream_invalid_too_short() -> None:
    with pytest.raises(ValueError, match="Invalid VINT."):
        core.decode_stream(BytesIO(b"\x01"))
