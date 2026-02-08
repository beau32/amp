"""Unit tests for amplex.py lexer."""

import unittest
from src import amplex


class TestAmpLexer(unittest.TestCase):
    """Test AmpScript lexer functionality."""

    def setUp(self):
        """Set up lexer for each test."""
        self.lexer = amplex.lexer

    def test_tokenize_name(self):
        """Test tokenization of variable names."""
        self.lexer.input("myVariable")
        token = self.lexer.token()
        
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, 'myVariable')

    def test_tokenize_number(self):
        """Test tokenization of numbers."""
        self.lexer.input("12345")
        token = self.lexer.token()
        
        self.assertEqual(token.type, 'NUMBER')
        self.assertEqual(token.value, 12345)

    def test_tokenize_string(self):
        """Test tokenization of strings."""
        self.lexer.input('"Hello"')
        token = self.lexer.token()
        
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, 'Hello')

    def test_tokenize_keywords(self):
        """Test tokenization of reserved keywords."""
        keywords = ['SET', 'IF', 'FOR', 'THEN', 'VAR', 'ENDIF']
        
        for keyword in keywords:
            self.lexer.input(keyword)
            token = self.lexer.token()
            self.assertEqual(token.type, keyword)

    def test_tokenize_operators(self):
        """Test tokenization of comparison operators."""
        operators = {
            '==': 'EQ',
            '!=': 'NE',
            '>=': 'GE',
            '<=': 'LE',
            '<': 'LT',
            '>': 'GT'
        }
        
        for op_str, op_type in operators.items():
            self.lexer.input(op_str)
            token = self.lexer.token()
            self.assertEqual(token.type, op_type)

    def test_tokenize_ampscript_delimiters(self):
        """Test tokenization of AmpScript delimiters."""
        self.lexer.input('%%[')
        token = self.lexer.token()
        self.assertEqual(token.type, 'OPEN')
        
        self.lexer.input(']%%')
        token = self.lexer.token()
        self.assertEqual(token.type, 'CLOSE')

    def test_tokenize_inline_delimiters(self):
        """Test tokenization of inline AmpScript delimiters."""
        self.lexer.input('%%=')
        token = self.lexer.token()
        self.assertEqual(token.type, 'SOPEN')
        
        self.lexer.input('=%%')
        token = self.lexer.token()
        self.assertEqual(token.type, 'SCLOSE')

    def test_ignore_whitespace(self):
        """Test that whitespace is properly ignored."""
        self.lexer.input("  VAR  @a  ")
        
        token1 = self.lexer.token()
        self.assertEqual(token1.type, 'VAR')
        
        token2 = self.lexer.token()
        self.assertEqual(token2.value, '@')
        
        token3 = self.lexer.token()
        self.assertEqual(token3.type, 'NAME')

    def test_line_counting(self):
        """Test that line numbers are tracked correctly."""
        self.lexer.input("VAR\n@a\n")
        
        token1 = self.lexer.token()
        self.assertEqual(token1.lineno, 1)
        
        self.lexer.token()  # @
        token3 = self.lexer.token()
        self.assertEqual(token3.lineno, 2)

    def test_comment_ignored(self):
        """Test that comments are ignored."""
        self.lexer.input("/* comment */ VAR")
        
        token = self.lexer.token()
        # Should skip comment and get VAR
        self.assertEqual(token.type, 'VAR')


if __name__ == '__main__':
    unittest.main()
