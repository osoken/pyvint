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
