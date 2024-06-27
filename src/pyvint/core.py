import math


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
        flg = vint[idx] & 0xFF
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
