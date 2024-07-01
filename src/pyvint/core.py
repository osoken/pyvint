import math
from io import BytesIO
from typing import Optional, Tuple


def _calc_vint_width(vint: bytes) -> int:
    r"""
    >>> _calc_vint_width(b'\x82')
    0
    >>> _calc_vint_width(b'\x40\x02')
    1
    >>> _calc_vint_width(b'\x20\x00\x02')
    2
    >>> _calc_vint_width(b'\x10\x00\x00\x02')
    3
    >>> _calc_vint_width(b'\x00\x04')
    13
    """
    vint_width = 0
    for idx in range(len(vint)):
        flg = vint[idx]
        if flg == 0:
            vint_width += 8
        else:
            vint_width += 7 - math.floor(math.log2(flg))
            break
    return vint_width


def decode(vint: bytes) -> int:
    r"""
    Decode a Variable-Size Integer (VINT).

    Args:
        vint (bytes): The bytes representing the VINT.

    Returns:
        The decoded integer.

    Examples:
        >>> decode(b'\x82')
        2
        >>> decode(b'\x10\x00\x00\x02')
        2
        >>> decode(b'\xff')
        127
        >>> decode(b'\x01')
        Traceback (most recent call last):
         ...
        ValueError: Invalid VINT.
    """
    vint_width = _calc_vint_width(vint)
    if len(vint) != vint_width + 1:
        raise ValueError("Invalid VINT.")
    return int.from_bytes(vint, byteorder="big") - (0x01 << (7 * vint_width + 7))


def _calc_vint_width_and_return_last_bytes_from_stream(stream: BytesIO) -> Tuple[int, bytes]:
    r"""
    >>> _calc_vint_width_and_return_last_bytes_from_stream(BytesIO(b'\x82'))
    (0, b'\x82')
    >>> _calc_vint_width_and_return_last_bytes_from_stream(BytesIO(b'\x40\x02'))
    (1, b'@')
    >>> _calc_vint_width_and_return_last_bytes_from_stream(BytesIO(b'\x20\x00\x02'))
    (2, b' ')
    >>> _calc_vint_width_and_return_last_bytes_from_stream(BytesIO(b'\x10\x00\x00\x02'))
    (3, b'\x10')
    >>> _calc_vint_width_and_return_last_bytes_from_stream(BytesIO(b'\x00\x04'))
    (13, b'\x04')
    """
    vint_width = 0
    byte = stream.read(1)
    while byte:
        flg = byte[0]
        if flg == 0:
            vint_width += 8
        else:
            vint_width += 7 - math.floor(math.log2(flg))
            break
        byte = stream.read(1)
    return vint_width, byte


def decode_stream(stream: BytesIO) -> int:
    r"""
    Decode a Variable-Size Integer (VINT) from a stream.

    Args:
        stream (IOBase[bytes]): The stream to read the VINT from.

    Returns:
        The decoded integer.

    Examples:
        >>> from io import BytesIO
        >>> stream = BytesIO(b'\x82')
        >>> decode_stream(stream)
        2
        >>> stream = BytesIO(b'\x40\x02\x00')
        >>> decode_stream(stream)
        2
        >>> stream.read()
        b'\x00'
    """
    vint_width, head_byte = _calc_vint_width_and_return_last_bytes_from_stream(stream)
    head_byte = (head_byte[0] & ((0x01 << (7 - (vint_width % 8))) - 1)).to_bytes(1, byteorder="big")
    vint = head_byte + stream.read(vint_width - vint_width // 8)
    if len(vint) != vint_width + 1 - vint_width // 8:
        raise ValueError("Invalid VINT.")
    return int.from_bytes(vint, byteorder="big")


def encode(value: int, octet_length: Optional[int] = None) -> bytes:
    r"""
    Encode an integer to a Variable-Size Integer (VINT).
    You can specify the octet length of the VINT. If you don't specify it, the function will calculate it automatically.
    This function doesn't support negative integers, which causes a ValueError to be raised.
    You will get a ValueError if the octet length is less than the calculated one.

    Args:
        value (int): The integer to encode.
        octet_length (Optional[int]): The octet length of the VINT. Defaults to None.

    Returns:
        The bytes representing the VINT.

    Examples:
        >>> encode(2)
        b'\x82'
        >>> encode(89)
        b'\xd9'
        >>> encode(0)
        b'\x80'
        >>> encode(0, 2)
        b'@\x00'
        >>> encode(172351395)
        b'\x1aE\xdf\xa3'
        >>> encode(2, 2)
        b'@\x02'
    """
    if value < 0:
        raise ValueError("The value must be non-negative.")
    b128_length = math.floor(math.log(value, 128)) + 1 if value > 0 else 1
    if octet_length is None:
        octet_length_ = b128_length
    else:
        if octet_length < b128_length:
            raise ValueError("Invalid octet length.")
        octet_length_ = octet_length
    buf = bytearray(value.to_bytes(octet_length_, byteorder="big"))
    buf[(octet_length_ - 1) // 8] |= 0x80 >> ((octet_length_ + 7) % 8)
    return bytes(buf)
