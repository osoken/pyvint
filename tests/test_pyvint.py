import re

import pyvint


def test_pyvint_exports_version() -> None:
    assert re.match(r"\d+\.\d+\.\d+", pyvint.__version__)


def test_pyvint_exports_decode() -> None:
    assert pyvint.decode == pyvint.core.decode


def test_pyvint_exports_decode_stream() -> None:
    assert pyvint.decode_stream == pyvint.core.decode_stream
