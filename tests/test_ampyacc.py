"""Unit tests for ampyacc.py parser."""

import unittest
from src import ampyacc


class TestAmpParser(unittest.TestCase):
    """Test AmpScript parser functionality."""

    def test_parse_variable_declaration(self):
        """Test parsing variable declarations."""
        code = "%%[ VAR @a, @b ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'VAR')

    def test_parse_assignment(self):
        """Test parsing variable assignments."""
        code = "%%[ SET @a = 1 ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'SET')
        self.assertEqual(result[1], 'a')

    def test_parse_if_statement(self):
        """Test parsing IF statements."""
        code = "%%[ IF @a < @b THEN VAR @c ENDIF ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'IF')

    def test_parse_if_else_statement(self):
        """Test parsing IF-ELSE statements."""
        code = "%%[ IF @a < @b THEN VAR @c ELSE VAR @d ENDIF ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'IFELSE')

    def test_parse_for_loop(self):
        """Test parsing FOR loops."""
        code = "%%[ FOR @i = 1 TO 10 DO VAR @a NEXT @i ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'FOR')
        self.assertEqual(result[1], 'i')

    def test_parse_for_downto_loop(self):
        """Test parsing FOR DOWNTO loops."""
        code = "%%[ FOR @i = 10 DOWNTO 1 DO VAR @a NEXT @i ]%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'FOR')
        self.assertEqual(result[3], 'DOWNTO')

    def test_parse_function_call(self):
        """Test parsing function calls."""
        code = '%%[ VAR @result SET @result = Output("Hello") ]%%'
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)

    def test_parse_arithmetic_expression(self):
        """Test parsing arithmetic expressions."""
        code = "%%=@a + @b=%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'BINOP')

    def test_parse_relational_expression(self):
        """Test parsing relational expressions."""
        code = "%%=@a < @b=%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'RELOP')

    def test_parse_complex_condition(self):
        """Test parsing complex conditions with AND/OR."""
        code = "%%=@a < @b AND @c > @d=%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)
        # Should contain BINOP for AND operation

    def test_parse_grouped_expression(self):
        """Test parsing grouped expressions with parentheses."""
        code = "%%=(@a + @b) * @c=%%"
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)

    def test_parse_full_program(self):
        """Test parsing a complete AmpScript program."""
        code = """
        %%[
        VAR @a, @b
        SET @a = 1
        SET @b = 2
        IF @a < @b THEN
            Output('Less')
        ENDIF
        ]%%
        """
        result = ampyacc.parse(code)
        
        self.assertIsNotNone(result)

    def test_parse_syntax_error(self):
        """Test handling of syntax errors."""
        code = "%%[ SET @a = ]%%"  # Incomplete assignment
        result = ampyacc.parse(code)
        
        self.assertIsNone(result)

    def test_parse_empty_input(self):
        """Test parsing empty input."""
        code = ""
        result = ampyacc.parse(code)
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
