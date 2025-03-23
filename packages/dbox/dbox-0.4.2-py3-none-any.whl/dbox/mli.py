import struct


def binary(num: float) -> str:
    """Convert a float to a binary string."""
    return "".join("{:0>8b}".format(c) for c in struct.pack("!f", num))


def test_binary():
    assert binary(1.0) == "01000000011110101110000101000111"
