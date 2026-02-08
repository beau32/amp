"""Unit tests for ampinterpreter.py."""

import unittest
import io
from contextlib import redirect_stdout
from src import ampinterpreter


class TestAmpInterpreter(unittest.TestCase):
    """Test AmpScript interpreter functionality."""

    def setUp(self):
        """Set up interpreter for each test."""
        self.interpreter = ampinterpreter.AmpInterpreter({})

    def test_eval_integer(self):
        """Test evaluation of integer literals."""
        expr = ('INT', 42)
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 42)

    def test_eval_string(self):
        """Test evaluation of string literals."""
        expr = ('STR', 'hello')
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 'hello')

    def test_eval_addition(self):
        """Test evaluation of addition."""
        expr = ('BINOP', '+', ('INT', 2), ('INT', 3))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 5)

    def test_eval_subtraction(self):
        """Test evaluation of subtraction."""
        expr = ('BINOP', '-', ('INT', 5), ('INT', 3))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 2)

    def test_eval_multiplication(self):
        """Test evaluation of multiplication."""
        expr = ('BINOP', '*', ('INT', 3), ('INT', 4))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 12)

    def test_eval_division(self):
        """Test evaluation of division."""
        expr = ('BINOP', '/', ('INT', 10), ('INT', 2))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 5.0)

    def test_eval_grouped_expression(self):
        """Test evaluation of grouped expressions."""
        expr = ('GROUP', ('INT', 42))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 42)

    def test_eval_unary_minus(self):
        """Test evaluation of unary minus."""
        expr = ('UNARY', '-', ('INT', 5))
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, -5)

    def test_assign_variable(self):
        """Test variable assignment."""
        self.interpreter.vars['a'] = None
        self.interpreter.assign('a', ('INT', 10))
        
        self.assertEqual(self.interpreter.vars['a'], 10)

    def test_eval_variable(self):
        """Test evaluation of variables."""
        self.interpreter.vars['a'] = 42
        expr = ('@', 'a')
        result = self.interpreter.eval(expr)
        
        self.assertEqual(result, 42)

    def test_eval_undefined_variable(self):
        """Test evaluation of undefined variable raises error."""
        expr = ('@', 'undefined')
        
        with self.assertRaises(RuntimeError):
            self.interpreter.eval(expr)

    def test_relational_expression_less_than(self):
        """Test relational expression evaluation (less than)."""
        self.interpreter.vars['a'] = 5
        self.interpreter.vars['b'] = 10
        
        expr = ('RELOP', '<', ('@', 'a'), ('@', 'b'))
        result = self.interpreter.releval(expr)
        
        self.assertTrue(result)

    def test_relational_expression_greater_than(self):
        """Test relational expression evaluation (greater than)."""
        self.interpreter.vars['a'] = 10
        self.interpreter.vars['b'] = 5
        
        expr = ('RELOP', '>', ('@', 'a'), ('@', 'b'))
        result = self.interpreter.releval(expr)
        
        self.assertTrue(result)

    def test_relational_expression_equal(self):
        """Test relational expression evaluation (equal)."""
        self.interpreter.vars['a'] = 5
        self.interpreter.vars['b'] = 5
        
        expr = ('RELOP', '==', ('@', 'a'), ('@', 'b'))
        result = self.interpreter.releval(expr)
        
        self.assertTrue(result)

    def test_flatten_list(self):
        """Test flattening nested lists."""
        nested = (('a', '@'), ('b', '@'), 'c')
        result = self.interpreter.flatten_list(nested)
        
        self.assertIn('a', result)
        self.assertIn('@', result)
        self.assertIn('b', result)

    def test_var_str_int(self):
        """Test converting integer value to string."""
        result = self.interpreter.var_str(('INT', 42))
        
        self.assertEqual(result, "42")

    def test_var_str_string(self):
        """Test converting string value to string."""
        result = self.interpreter.var_str(('STR', 'hello'))
        
        self.assertEqual(result, "'hello'")

    def test_var_str_variable(self):
        """Test converting variable value to string."""
        self.interpreter.vars['a'] = 'value'
        result = self.interpreter.var_str(('@', 'a'))
        
        self.assertEqual(result, "value")

    def test_add_statements(self):
        """Test adding statements to program."""
        prog_statement = ('VAR', ('@', 'a'))
        self.interpreter.add_statements(prog_statement)
        
        self.assertIn(0, self.interpreter.prog)
        self.assertEqual(self.interpreter.prog[0], prog_statement)

    def test_new_program(self):
        """Test clearing the program."""
        self.interpreter.prog = {0: ('VAR', ('@', 'a'))}
        self.interpreter.new()
        
        self.assertEqual(len(self.interpreter.prog), 0)


if __name__ == '__main__':
    unittest.main()
