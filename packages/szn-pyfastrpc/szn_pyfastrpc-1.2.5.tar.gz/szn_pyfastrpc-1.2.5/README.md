# szn-pyfastrpc

**szn-pyfastrpc** is a Python implementation of the FastRPC protocol.  
Version: **1.1.36**

This package implements several revisions of the FastRPC protocol including:

- **Protocol 3.0 extension:** Uses zigzag encoding for integers and enlarges DateTime fields to 64 bits.
- **Protocol 2.x extension:** Supports Integer8 types, strings, binary, struct, and array types.
- **Protocol 1.0 specification:** Implements basic scalar types (integer, boolean, double, string, date, binary) and structured types (struct, array) similar to XML-RPC.

The package is designed for use on PyPI and includes a function that automatically starts a FastRPC service when the package is imported.

See the source files for more details on encoding, serialization, and parsing of FastRPC messages.
