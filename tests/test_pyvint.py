import re

import pyvint


def test_pyvint_exports_version() -> None:
    assert re.match(r"\d+\.\d+\.\d+", pyvint.__version__)


def test_pyvint_exports_decode() -> None:
    assert pyvint.decode == pyvint.core.decode


def test_pyvint_exports_decode_stream() -> None:
    assert pyvint.decode_stream == pyvint.core.decode_stream


def test_pyvint_exports_encode() -> None:
    assert pyvint.encode == pyvint.core.encode


def test_pyvint_exports_read_vint() -> None:
    assert pyvint.read_vint == pyvint.core.read_vint
