# szn_pyfastrpc/utils.py

def zigzag_encode(n: int) -> int:
    """
    Encode an integer using ZigZag encoding.
    ZigZag encoding maps signed integers to unsigned integers so that numbers
    with a small absolute value (e.g., -1) have a small varint encoded value.
    """
    return (n << 1) ^ (n >> 31)

def zigzag_decode(n: int) -> int:
    """
    Decode a ZigZag-encoded integer.
    """
    return (n >> 1) ^ -(n & 1)

def int_to_bytes(n: int, length: int) -> bytes:
    """
    Convert an integer to little-endian bytes of the specified length.
    """
    return n.to_bytes(length, byteorder='little')

def bytes_to_int(b: bytes) -> int:
    """
    Convert little-endian bytes to an integer.
    """
    return int.from_bytes(b, byteorder='little')

def read_varint(data: bytes) -> (int, bytes):
    """
    Read a variable-length integer from the data.
    Returns the integer and the remaining bytes.
    (Simplified: assumes the varint fits in one byte for small values.)
    """
    if not data:
        raise ValueError("No data to read")
    value = data[0]
    return value, data[1:]
