# pyvint

A pure Python library for encoding and decoding Variable-Sized Integer (VINT) values.
VINT is used in EBML (Extensible Binary Meta Language) to encode integers with a variable number of bytes.
Detailed information about VINT can be found in the [Extensible Binary Meta Language RFC 8794](https://datatracker.ietf.org/doc/rfc8794/)

## Installation

The library is available on PyPI and can be installed using pip:

```bash
pip install pyvint
```

## Usage

### Encoding (Integer to VINT)

```python
import pyvint

vint = pyvint.encode(2)  # just passing an integer returns the minimum length VINT
print(vint)  # b'\x82'
vint2 = pyvint.encode(2, 2)  # passing an integer and the octet length returns a VINT with the specified octet length
print(vint2)  # b'\x40\x02'
```

### Decoding (VINT to Integer)

```python
import pyvint

value = pyvint.decode(b'\x82')
print(value)  # 2
value2 = pyvint.decode(b'\x40\x02')
print(value2)  # 2
```

`pyvint` also provides decoding of VINTs from a stream of bytes. This is useful when reading VINTs from a file or a network stream.
The `decode_stream` function returns the integer value of the VINT and advances the buffer to the next byte after the VINT.

```python
from io import BytesIO
import pyvint

data = b'\x82\x40\x02'
buffer = BytesIO(data)
value = pyvint.decode_stream(data)
print(value)  # 2
print(buffer.read())  # b'\x40\x02'
```
