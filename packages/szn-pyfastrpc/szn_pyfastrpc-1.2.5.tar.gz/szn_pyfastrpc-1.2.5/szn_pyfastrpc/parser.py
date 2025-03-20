# szn_pyfastrpc/parser.py

"""
Parser module for FastRPC messages.

This module provides functions to parse complete FastRPC messages from a byte stream.
"""

from .serializer import deserialize

def parse_message(data: bytes):
    """
    Parse a complete FastRPC message from the given byte stream.
    Returns a tuple of (parsed_object, remaining_bytes).
    """
    # In a full implementation, we would compute the exact length of a message.
    # Here we assume that the entire stream represents a single object.
    obj = deserialize(data)
    return obj, b''

def parse_multiple_messages(data: bytes):
    """
    Parse multiple FastRPC messages from a continuous byte stream.
    Returns a list of parsed objects.
    """
    messages = []
    remaining = data
    while remaining:
        msg, remaining = parse_message(remaining)
        messages.append(msg)
    return messages
