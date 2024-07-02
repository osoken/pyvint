import math
from io import BytesIO
from typing import Optional


def _count_leading_zeros_in_char(char_value: int) -> int:
    r"""
    >>> _count_leading_zeros_in_char(0b00000000)
    8
    >>> _count_leading_zeros_in_char(0b00000001)
    7
    >>> _count_leading_zeros_in_char(0b10000000)
    0
    >>> _count_leading_zeros_in_char(0b11111111)
    0
    >>> _count_leading_zeros_in_char(0b00100111)
    2
    """
    if char_value == 0:
        return 8
    ans = 0
    val = char_value
    if val & 0b11110000 == 0:
        ans += 4
        val <<= 4
    if val & 0b11000000 == 0:
        ans += 2
        val <<= 2
    if val & 0b10000000 == 0:
        ans += 1
    return ans


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
    octet_length = 0
    for b in vint:
        leading_zeros = _count_leading_zeros_in_char(b)
        octet_length += leading_zeros
        if leading_zeros < 8:
            break
    if len(vint) != octet_length + 1:
        raise ValueError("Invalid VINT.")
    return _decode_impl(vint)


def _decode_impl(vint: bytes) -> int:
    r"""
    >>> _decode_impl(b'\x82')
    2
    >>> _decode_impl(b'\x10\x00\x00\x02')
    2
    >>> _decode_impl(b'\xff')
    127
    """
    octet_length = len(vint)
    buf = bytearray(vint)
    buf[(octet_length - 1) // 8] &= (0x80 >> ((octet_length + 7) % 8)) - 1
    return int.from_bytes(buf, byteorder="big")


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
    return _decode_impl(read_vint(stream))


def read_vint(stream: BytesIO) -> bytes:
    r"""
    Read a Variable-Size Integer (VINT) from a stream.

    Args:
        stream (IOBase[bytes]): The stream to read the VINT from.

    Returns:
        The VINT bytes.

    Examples:
        >>> from io import BytesIO
        >>> stream = BytesIO(b'\x82')
        >>> read_vint(stream)
        b'\x82'
        >>> stream = BytesIO(b'\x40\x02\x00')
        >>> read_vint(stream)
        b'@\x02'
        >>> stream.read()
        b'\x00'
    """
    octet_length = 0
    while True:
        b = stream.read(1)
        if not b:
            raise ValueError("Invalid VINT.")
        leading_zeros = _count_leading_zeros_in_char(b[0])
        octet_length += leading_zeros
        if leading_zeros < 8:
            break
    remaining = octet_length - octet_length // 8
    remaining_bytes = stream.read(remaining)
    if len(remaining_bytes) != remaining:
        raise ValueError("Invalid VINT.")
    return b"\x00" * (octet_length // 8) + b + remaining_bytes


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
