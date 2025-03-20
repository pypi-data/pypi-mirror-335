# szn_pyfastrpc/serializer.py

"""
Serializer module for FastRPC.

This module provides functions to serialize Python objects into FastRPC-encoded bytes
and to deserialize FastRPC messages back into Python objects.

Supported types in this simplified implementation:
  - int       -> FastRPCInteger
  - str       -> FastRPCString
  - dict      -> Encoded as a FastRPC struct (with limited support)
  - datetime-like objects (must have attributes timestamp(), second, minute, hour, day, month, year)
"""

from .protocol import FastRPCInteger, FastRPCString, FastRPCDateTime
import struct

def serialize(obj) -> bytes:
    """
    Serialize a Python object into FastRPC encoded bytes.
    """
    if isinstance(obj, int):
        return FastRPCInteger(obj).encode()
    elif isinstance(obj, str):
        return FastRPCString(obj).encode()
    elif isinstance(obj, dict):
        # Serialize dict as a struct.
        result = b'\x0A'  # Type for struct in protocol 1.0 (for example)
        num_members = len(obj)
        result += bytes([num_members])
        for key, value in obj.items():
            key_bytes = key.encode('utf-8')
            if len(key_bytes) > 255:
                raise ValueError("Key too long")
            # Prefix each member with key length.
            result += bytes([len(key_bytes)]) + key_bytes
            # Recursively serialize the value.
            serialized_value = serialize(value)
            result += serialized_value
        return result
    elif hasattr(obj, 'timestamp'):
        # Assume a datetime-like object.
        dt = FastRPCDateTime(
            zone=0,
            unix_timestamp=int(obj.timestamp()),
            weekday=0,
            sec=obj.second,
            minute=obj.minute,
            hour=obj.hour,
            day=obj.day,
            month=obj.month,
            year=obj.year
        )
        return dt.encode()
    else:
        raise TypeError(f"Type {type(obj)} not supported for serialization.")

def deserialize(data: bytes):
    """
    Deserialize FastRPC encoded bytes into a Python object.
    This is a simplified implementation that handles a subset of types.
    """
    if not data:
        return None
    type_id = data[0] >> 3
    if type_id == 0x01:
        # Integer type.
        from .protocol import FastRPCInteger
        obj, remaining = FastRPCInteger.decode(data)
        return obj.value
    elif type_id == 0x04:
        # String type.
        from .protocol import FastRPCString
        obj, remaining = FastRPCString.decode(data)
        return obj.value
    elif type_id == 0x05:
        # DateTime type.
        from .protocol import FastRPCDateTime
        obj, remaining = FastRPCDateTime.decode(data)
        # Return a dict with datetime fields for demonstration.
        return {
            'zone': obj.zone,
            'unix_timestamp': obj.unix_timestamp,
            'weekday': obj.weekday,
            'sec': obj.sec,
            'minute': obj.minute,
            'hour': obj.hour,
        }
    elif type_id == 0x0A:
        # Struct type (dict).
        if len(data) < 2:
            raise ValueError("Invalid struct data")
        num_members = data[1]
        pos = 2
        result = {}
        for _ in range(num_members):
            name_length = data[pos]
            pos += 1
            name = data[pos:pos+name_length].decode('utf-8')
            pos += name_length
            # Deserialize value (simplified: assume each value is a one-byte header plus two data bytes).
            value = deserialize(data[pos:])
            result[name] = value
            pos += 2  # Placeholder for value length.
        return result
    else:
        raise ValueError("Unknown type")
