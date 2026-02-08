"""Unit tests for lib/utils.py."""

import unittest
from lib import utils


class TestDateFormatConversion(unittest.TestCase):
    """Test C# to Python date format conversion."""

    def test_convert_year_format(self):
        """Test conversion of year formats."""
        result = utils.convert_csharp_date_format('yyyy')
        self.assertEqual(result, '%Y')
        
        result = utils.convert_csharp_date_format('yy')
        self.assertEqual(result, '%y')

    def test_convert_month_format(self):
        """Test conversion of month formats."""
        result = utils.convert_csharp_date_format('MMMM')
        self.assertEqual(result, '%B')
        
        result = utils.convert_csharp_date_format('MM')
        self.assertEqual(result, '%m')

    def test_convert_day_format(self):
        """Test conversion of day formats."""
        result = utils.convert_csharp_date_format('dddd')
        self.assertEqual(result, '%A')
        
        result = utils.convert_csharp_date_format('dd')
        self.assertEqual(result, '%d')

    def test_convert_time_format(self):
        """Test conversion of time formats."""
        result = utils.convert_csharp_date_format('HH:mm:ss')
        self.assertIn('%H', result)
        self.assertIn('%M', result)
        self.assertIn('%S', result)

    def test_convert_complex_format(self):
        """Test conversion of complex date formats."""
        result = utils.convert_csharp_date_format('yyyy-MM-dd HH:mm:ss')
        self.assertIn('%Y', result)
        self.assertIn('%m', result)
        self.assertIn('%d', result)
        self.assertIn('%H', result)
        self.assertIn('%M', result)
        self.assertIn('%S', result)

    def test_convert_literal_text(self):
        """Test conversion with literal text in quotes."""
        result = utils.convert_csharp_date_format("yyyy 'at' HH:mm")
        self.assertIn('%Y', result)
        self.assertIn('at', result)
        self.assertIn('%H', result)

    def test_convert_escaped_characters(self):
        """Test conversion with escaped characters."""
        result = utils.convert_csharp_date_format(r'yyyy\-MM\-dd')
        self.assertIn('%Y', result)
        self.assertIn('-', result)
        self.assertIn('%m', result)


class TestSalesforceIDConversion(unittest.TestCase):
    """Test Salesforce ID conversion."""

    def test_convert_15_to_18_char_id(self):
        """Test converting 15-character ID to 18-character ID."""
        id_15 = "001D000000IqhSL"
        result = utils.convert_salesforce_15_to_18(id_15)
        
        self.assertEqual(len(result), 18)
        self.assertTrue(result.startswith(id_15))

    def test_return_18_char_id_unchanged(self):
        """Test that 18-character IDs are returned unchanged."""
        id_18 = "001D000000IqhSLIAZ"
        result = utils.convert_salesforce_15_to_18(id_18)
        
        self.assertEqual(result, id_18)

    def test_raise_error_for_empty_id(self):
        """Test that empty ID raises ValueError."""
        with self.assertRaises(ValueError):
            utils.convert_salesforce_15_to_18("")

    def test_raise_error_for_none_id(self):
        """Test that None ID raises ValueError."""
        with self.assertRaises(ValueError):
            utils.convert_salesforce_15_to_18(None)

    def test_raise_error_for_non_string_id(self):
        """Test that non-string ID raises TypeError."""
        with self.assertRaises(TypeError):
            utils.convert_salesforce_15_to_18(12345)

    def test_raise_error_for_invalid_length(self):
        """Test that invalid length ID raises ValueError."""
        with self.assertRaises(ValueError):
            utils.convert_salesforce_15_to_18("001D000")

    def test_checksum_calculation(self):
        """Test that checksum is correctly calculated."""
        id_15 = "001D000000IqhSL"
        result = utils.convert_salesforce_15_to_18(id_15)
        
        # The last 3 characters should be checksum
        self.assertEqual(len(result), 18)
        checksum = result[15:]
        self.assertEqual(len(checksum), 3)


class TestHashFunctions(unittest.TestCase):
    """Test hash functions."""

    def test_md5_hash(self):
        """Test MD5 hash generation."""
        text = "hello"
        result = utils.hash_string('md5', text)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 32)  # MD5 produces 32 hex characters
        self.assertEqual(result, '5d41402abc4b2a76b9719d911017c592')

    def test_sha1_hash(self):
        """Test SHA1 hash generation."""
        text = "hello"
        result = utils.hash_string('sha1', text)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 40)  # SHA1 produces 40 hex characters
        self.assertEqual(result, 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d')

    def test_sha256_hash(self):
        """Test SHA256 hash generation."""
        text = "hello"
        result = utils.hash_string('sha256', text)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)  # SHA256 produces 64 hex characters

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        result = utils.hash_string('md5', '')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 32)

    def test_hash_unicode(self):
        """Test hashing Unicode text."""
        text = "Hello 世界"
        result = utils.hash_string('md5', text)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 32)

    def test_hash_consistency(self):
        """Test that same input produces same hash."""
        text = "test"
        hash1 = utils.hash_string('md5', text)
        hash2 = utils.hash_string('md5', text)
        
        self.assertEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()
