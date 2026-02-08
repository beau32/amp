"""Unit tests for AmpScript function library."""

import unittest
from src import ampfunctions


class TestAmpFunctions(unittest.TestCase):
    """Test cases for AmpScript functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.func = ampfunctions.func()

    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        self.assertTrue(self.func.IsPhoneNumber('123-456-7890'))
        self.assertTrue(self.func.IsPhoneNumber('+1(123)456-7890'))

        # Invalid phone numbers
        self.assertFalse(self.func.IsPhoneNumber('123'))
        self.assertFalse(self.func.IsPhoneNumber('invalid'))

    def test_email_validation(self):
        """Test email address validation."""
        # Valid emails
        self.assertTrue(self.func.IsEmailAddress('test@example.com'))
        self.assertTrue(self.func.IsEmailAddress('user.name+tag@example.co.uk'))

        # Invalid emails
        self.assertFalse(self.func.IsEmailAddress('invalid'))
        self.assertFalse(self.func.IsEmailAddress('@example.com'))

    def test_string_operations(self):
        """Test string manipulation functions."""
        self.assertEqual(self.func.Length('hello'), 5)
        self.assertEqual(self.func.Uppercase('hello'), 'HELLO')
        self.assertEqual(self.func.Lowercase('HELLO'), 'hello')
        self.assertEqual(self.func.Trim('  hello  '), 'hello')

    def test_math_operations(self):
        """Test math functions."""
        self.assertEqual(self.func.Add(2, 3), 5)
        self.assertEqual(self.func.Subtract(5, 2), 3)
        self.assertEqual(self.func.Multiply(3, 4), 12)
        self.assertEqual(self.func.Divide(10, 2), 5.0)
        self.assertEqual(self.func.Mod(10, 3), 1)

    def test_hash_functions(self):
        """Test hash functions."""
        text = 'test'
        md5_hash = self.func.MD5(text)
        self.assertIsNotNone(md5_hash)
        self.assertEqual(len(md5_hash), 32)  # MD5 produces 32 hex chars

        sha1_hash = self.func.SHA1(text)
        self.assertIsNotNone(sha1_hash)
        self.assertEqual(len(sha1_hash), 40)  # SHA1 produces 40 hex chars

    def test_base64_encoding(self):
        """Test base64 encoding and decoding."""
        text = 'hello world'
        encoded = self.func.Base64Encode(text)
        self.assertIsNotNone(encoded)
        decoded = self.func.Base64Decode(encoded)
        self.assertEqual(decoded, text)


if __name__ == '__main__':
    unittest.main()
