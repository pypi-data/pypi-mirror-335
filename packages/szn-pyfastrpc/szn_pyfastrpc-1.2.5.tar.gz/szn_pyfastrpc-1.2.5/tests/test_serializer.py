# tests/test_serializer.py

import unittest
from szn_pyfastrpc.serializer import serialize, deserialize

class TestSerializer(unittest.TestCase):
    def test_serialize_integer(self):
        num = 100
        encoded = serialize(num)
        decoded = deserialize(encoded)
        self.assertEqual(decoded, num)

    def test_serialize_string(self):
        text = "Hello World"
        encoded = serialize(text)
        decoded = deserialize(encoded)
        self.assertEqual(decoded, text)

if __name__ == '__main__':
    unittest.main()
