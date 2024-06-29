from io import BytesIO

import pytest

from pyvint import core


@pytest.mark.parametrize(
    ("vint", "expected"),
    (
        (b"\x82", 2),
        (b"\x40\x02", 2),
        (b"\x20\x00\x02", 2),
        (b"\x10\x00\x00\x02", 2),
        (b"\x00\x11\x04\xc4\x31\x49\x08\xfb\xb7\xd9\x86\xb6", 1231434398764213200324278),
        (b"\x1a\x45\xdf\xa3", 172351395),
    ),
)
def test_decode(vint: bytes, expected: int) -> None:
    assert core.decode(vint) == expected


@pytest.mark.parametrize(
    ("vint", "expected", "remainder"),
    (
        (b"\x82", 2, b""),
        (b"\x40\x02\x00", 2, b"\x00"),
        (b"\x20\x00\x02\x00", 2, b"\x00"),
    ),
)
def test_decode_stream(vint: bytes, expected: int, remainder: bytes) -> None:
    stream = BytesIO(vint)
    actual = core.decode_stream(stream=stream)
    assert actual == expected
    assert stream.read() == remainder
