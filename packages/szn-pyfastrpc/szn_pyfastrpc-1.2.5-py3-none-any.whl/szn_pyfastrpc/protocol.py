# szn_pyfastrpc/protocol.py

"""
FastRPC Protocol Implementation

This module implements encoding and decoding for FastRPC protocol types,
supporting multiple revisions including:
  - FastRPC protocol 3.0 extension (zigzag encoding, 64-bit timestamps)
  - FastRPC protocol 2.x extension (Integer8, string, binary, struct, array)
  - FastRPC protocol 1.0 specification (basic scalar types and non-data types)

Refer to the documentation for details on the binary formats.
"""

import struct
from .utils import zigzag_encode, zigzag_decode, int_to_bytes, bytes_to_int

class FastRPCInteger:
    def __init__(self, value: int):
        self.value = value

    def encode(self) -> bytes:
        """
        Encode the integer using ZigZag encoding.
        Depending on the size, the integer is encoded in 1–4 octets.
        """
        encoded = zigzag_encode(self.value)
        # Determine number of bytes needed
        if encoded < 0x80:
            length = 1
        elif encoded < 0x8000:
            length = 2
        elif encoded < 0x800000:
            length = 3
        else:
            length = 4
        data = int_to_bytes(encoded, length)
        # Prepend type info: For simplicity, we use type 0x01 for integer (protocol 1.0 style)
        type_byte = (0x01 << 3) | (length - 1)
        return bytes([type_byte]) + data

    @staticmethod
    def decode(data: bytes) -> ('FastRPCInteger', bytes):
        """
        Decode an integer from FastRPC encoded bytes.
        Returns a FastRPCInteger instance and any remaining bytes.
        """
        if len(data) < 1:
            raise ValueError("Insufficient data to decode integer")
        type_byte = data[0]
        length = (type_byte & 0x07) + 1
        if len(data) < 1 + length:
            raise ValueError("Insufficient data for integer value")
        int_bytes = data[1:1+length]
        encoded = bytes_to_int(int_bytes)
        value = zigzag_decode(encoded)
        return FastRPCInteger(value), data[1+length:]

class FastRPCString:
    def __init__(self, value: str):
        self.value = value

    def encode(self) -> bytes:
        """
        Encode the string into FastRPC format.
        The string is UTF-8 encoded with a length prefix.
        """
        encoded_str = self.value.encode('utf-8')
        length = len(encoded_str)
        if length > 255:
            raise ValueError("String too long")
        # Type info for string: using 0x04 (shifted left by 3 bits)
        type_byte = 0x04 << 3
        return bytes([type_byte, length]) + encoded_str

    @staticmethod
    def decode(data: bytes) -> ('FastRPCString', bytes):
        """
        Decode a FastRPC encoded string.
        """
        if len(data) < 2:
            raise ValueError("Insufficient data for string")
        type_byte = data[0]
        length = data[1]
        if len(data) < 2 + length:
            raise ValueError("Insufficient data for string content")
        string_value = data[2:2+length].decode('utf-8')
        return FastRPCString(string_value), data[2+length:]

class FastRPCDateTime:
    def __init__(self, zone: int, unix_timestamp: int, weekday: int,
                 sec: int, minute: int, hour: int, day: int, month: int, year: int):
        self.zone = zone
        self.unix_timestamp = unix_timestamp
        self.weekday = weekday
        self.sec = sec
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year

    def encode(self) -> bytes:
        """
        Encode the DateTime field according to the FastRPC protocol.
        For protocol 3.0, the data part is 14 octets (after one type octet).
        """
        type_byte = (0x05 << 3)
        # Pack zone (1 byte) and unix timestamp (8 bytes, 64-bit little-endian)
        dt_bytes = struct.pack('<Bq', self.zone, self.unix_timestamp)
        # For simplicity, pack additional fields (weekday, sec, minute, hour) into 4 bytes.
        additional = (self.weekday & 0x07) | ((self.sec & 0x3F) << 3) | ((self.minute & 0x3F) << 9) | ((self.hour & 0x1F) << 15)
        additional_bytes = int_to_bytes(additional, 4)
        return bytes([type_byte]) + dt_bytes + additional_bytes

    @staticmethod
    def decode(data: bytes) -> ('FastRPCDateTime', bytes):
        """
        Decode a DateTime field from FastRPC encoded bytes.
        """
        if len(data) < 1 + 1 + 8 + 4:
            raise ValueError("Insufficient data for DateTime")
        type_byte = data[0]
        zone = data[1]
        unix_timestamp = struct.unpack('<q', data[2:10])[0]
        additional = bytes_to_int(data[10:14])
        weekday = additional & 0x07
        sec = (additional >> 3) & 0x3F
        minute = (additional >> 9) & 0x3F
        hour = (additional >> 15) & 0x1F
        # For brevity, day, month, and year are omitted in this simple example.
        return FastRPCDateTime(zone, unix_timestamp, weekday, sec, minute, hour, 0, 0, 0), data[14:]

# Note: Additional classes for Binary, Struct, and Array can be implemented similarly.
