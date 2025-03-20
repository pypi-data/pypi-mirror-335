# szn_pyfastrpc/main.py

"""
Main module for szn-pyfastrpc.

Provides a command-line interface to test serialization and parsing of FastRPC messages.
"""

import sys
from .serializer import serialize, deserialize
from .parser import parse_message

def main():
    """
    Entry point for command-line execution.
    Demonstrates serialization and parsing with sample data.
    """
    if len(sys.argv) < 2:
        print("Usage: szn-pyfastrpc <command> [args]")
        print("Commands: serialize, deserialize")
        sys.exit(1)

    command = sys.argv[1]
    if command == "serialize":
        sample = "Hello, FastRPC!"
        print("Serializing string:", sample)
        encoded = serialize(sample)
        print("Encoded bytes:", encoded)
    elif command == "deserialize":
        # For demonstration, use a hardcoded encoded string.
        encoded = b'\x20\x10Hello, FastRPC!'
        print("Decoding bytes:", encoded)
        obj = deserialize(encoded)
        print("Decoded object:", obj)
    else:
        print("Unknown command.")
        sys.exit(1)

if __name__ == "__main__":
    main()
