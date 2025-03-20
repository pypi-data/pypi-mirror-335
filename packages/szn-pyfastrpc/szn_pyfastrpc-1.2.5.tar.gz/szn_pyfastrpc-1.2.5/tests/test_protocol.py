# tests/test_protocol.py

import unittest
from szn_pyfastrpc.protocol import FastRPCInteger, FastRPCString

class TestProtocol(unittest.TestCase):
    def test_integer_encoding(self):
        num = 42
        rpc_int = FastRPCInteger(num)
        encoded = rpc_int.encode()
        decoded, remaining = FastRPCInteger.decode(encoded)
        self.assertEqual(decoded.value, num)
        self.assertEqual(remaining, b'')

    def test_string_encoding(self):
        text = "Test"
        rpc_str = FastRPCString(text)
        encoded = rpc_str.encode()
        decoded, remaining = FastRPCString.decode(encoded)
        self.assertEqual(decoded.value, text)
        self.assertEqual(remaining, b'')

if __name__ == '__main__':
    unittest.main()
