"""Unit tests for ampcompiler.py."""

import unittest
import io
from contextlib import redirect_stdout
from src import ampyacc, ampcompiler


class TestAmpCompilerToPy(unittest.TestCase):
    """Test AmpScript to Python compiler."""

    def compile_and_capture(self, code):
        """Helper to compile code and capture output."""
        prog = ampyacc.parse(code)
        if not prog:
            return None
        
        compiler = ampcompiler.AmpCompilerToPy(prog)
        output = io.StringIO()
        
        with redirect_stdout(output):
            compiler.compile()
        
        return output.getvalue()

    def test_compile_variable_declaration(self):
        """Test compiling variable declarations."""
        code = "%%[ VAR @a ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("a = None", result)

    def test_compile_multiple_variables(self):
        """Test compiling multiple variable declarations."""
        code = "%%[ VAR @a, @b, @c ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("a = None", result)
        self.assertIn("b = None", result)
        self.assertIn("c = None", result)

    def test_compile_assignment(self):
        """Test compiling assignments."""
        code = "%%[ SET @a = 1 ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("a = 1", result)

    def test_compile_string_assignment(self):
        """Test compiling string assignments."""
        code = '%%[ SET @a = "Hello" ]%%'
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("a = 'Hello'", result)

    def test_compile_if_statement(self):
        """Test compiling IF statements."""
        code = "%%[ IF @a < @b THEN VAR @c ENDIF ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("if", result)
        self.assertIn("a < b", result)

    def test_compile_if_else_statement(self):
        """Test compiling IF-ELSE statements."""
        code = "%%[ IF @a < @b THEN VAR @c ELSE VAR @d ENDIF ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("if", result)
        self.assertIn("else", result)

    def test_compile_for_loop(self):
        """Test compiling FOR loops."""
        code = "%%[ FOR @i = 0 TO 10 DO VAR @a NEXT @i ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("i = 0", result)
        self.assertIn("while", result)
        self.assertIn("i += 1", result)

    def test_compile_function_call(self):
        """Test compiling function calls."""
        code = '%%[ VAR @result SET @result = Output("Hello") ]%%'
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("getattr(ampfunctions,'Output')", result)


class TestAmpCompilerToJs(unittest.TestCase):
    """Test AmpScript to JavaScript compiler."""

    def compile_and_capture(self, code):
        """Helper to compile code and capture output."""
        prog = ampyacc.parse(code)
        if not prog:
            return None
        
        compiler = ampcompiler.AmpCompilerToJs(prog)
        output = io.StringIO()
        
        with redirect_stdout(output):
            compiler.compile()
        
        return output.getvalue()

    def test_compile_variable_declaration_js(self):
        """Test compiling variable declarations to JavaScript."""
        code = "%%[ VAR @a ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("var a", result)

    def test_compile_assignment_js(self):
        """Test compiling assignments to JavaScript."""
        code = "%%[ SET @a = 1 ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("a = 1", result)

    def test_compile_if_statement_js(self):
        """Test compiling IF statements to JavaScript."""
        code = "%%[ IF @a < @b THEN VAR @c ENDIF ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("if (", result)
        self.assertIn("a < b", result)
        self.assertIn("{", result)
        self.assertIn("}", result)

    def test_compile_for_loop_js(self):
        """Test compiling FOR loops to JavaScript."""
        code = "%%[ FOR @i = 0 TO 10 DO VAR @a NEXT @i ]%%"
        result = self.compile_and_capture(code)
        
        self.assertIsNotNone(result)
        self.assertIn("i = 0", result)
        self.assertIn("while (", result)
        self.assertIn("i += 1", result)


class TestCompilerHelpers(unittest.TestCase):
    """Test compiler helper methods."""

    def test_flatten_list(self):
        """Test list flattening functionality."""
        compiler = ampcompiler.AmpCompiler(None)
        nested = (('a', '@'), ('b', '@'), 'c')
        result = compiler.flatten_list(nested)
        
        self.assertIsInstance(result, list)
        self.assertIn('a', result)
        self.assertIn('b', result)
        self.assertIn('c', result)

    def test_convert_value_int(self):
        """Test converting integer values."""
        prog = ampyacc.parse("%%=1=%%")
        compiler = ampcompiler.AmpCompilerToPy(prog)
        result = compiler.convert_value_to_string(('INT', 42))
        
        self.assertEqual(result, "42")

    def test_convert_value_string(self):
        """Test converting string values."""
        prog = ampyacc.parse("%%=1=%%")
        compiler = ampcompiler.AmpCompilerToPy(prog)
        result = compiler.convert_value_to_string(('STR', 'hello'))
        
        self.assertEqual(result, "'hello'")

    def test_convert_value_variable(self):
        """Test converting variable references."""
        prog = ampyacc.parse("%%=1=%%")
        compiler = ampcompiler.AmpCompilerToPy(prog)
        result = compiler.convert_value_to_string(('@', 'myvar'))
        
        self.assertEqual(result, "myvar")


if __name__ == '__main__':
    unittest.main()
