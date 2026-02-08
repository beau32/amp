"""Unit tests for main amp.py module."""

import unittest
import os
import tempfile
from amp import (
    extract_ampscript_blocks,
    transpile_js_to_py,
    compile_from_file
)


class TestAmpScriptExtraction(unittest.TestCase):
    """Test AmpScript extraction from embedded content."""

    def test_extract_pure_ampscript(self):
        """Test extraction from pure AmpScript content."""
        content = "%%[ VAR @a SET @a = 1 ]%%"
        result, is_embedded = extract_ampscript_blocks(content)
        
        self.assertEqual(result.strip(), "VAR @a SET @a = 1")
        self.assertFalse(is_embedded)

    def test_extract_embedded_ampscript(self):
        """Test extraction from JavaScript-embedded AmpScript."""
        content = """
        <script>
        try {
        %%[ VAR @a SET @a = 1 ]%%
        } catch(e) {}
        </script>
        """
        result, is_embedded = extract_ampscript_blocks(content)
        
        self.assertIn("VAR @a", result)
        self.assertTrue(is_embedded)

    def test_extract_multiple_blocks(self):
        """Test extraction of multiple AmpScript blocks."""
        content = """
        %%[ VAR @a ]%%
        Some text
        %%[ SET @a = 1 ]%%
        """
        result, is_embedded = extract_ampscript_blocks(content)
        
        self.assertIn("VAR @a", result)
        self.assertIn("SET @a = 1", result)
        self.assertTrue(is_embedded)

    def test_unclosed_block(self):
        """Test handling of unclosed AmpScript blocks."""
        content = "%%[ VAR @a"
        result, is_embedded = extract_ampscript_blocks(content)
        
        # Should return empty or handle gracefully
        self.assertIsInstance(result, str)

    def test_empty_content(self):
        """Test extraction from empty content."""
        content = ""
        result, is_embedded = extract_ampscript_blocks(content)
        
        self.assertEqual(result, "")
        self.assertFalse(is_embedded)


class TestJavaScriptTranspilation(unittest.TestCase):
    """Test JavaScript to Python transpilation."""

    def test_transpile_try_catch(self):
        """Test transpilation of try-catch blocks."""
        js_code = "try { } catch() { }"
        py_code = transpile_js_to_py(js_code)
        
        self.assertIn("try:", py_code)
        self.assertIn("except Exception:", py_code)

    def test_transpile_try_catch_with_exception(self):
        """Test transpilation of try-catch with exception variable."""
        js_code = "try { } catch(e) { }"
        py_code = transpile_js_to_py(js_code)
        
        self.assertIn("try:", py_code)
        self.assertIn("except Exception:", py_code)

    def test_remove_script_tags(self):
        """Test removal of script tags."""
        js_code = "<script runat='server'>code</script>"
        py_code = transpile_js_to_py(js_code)
        
        self.assertNotIn("<script", py_code)
        self.assertNotIn("</script>", py_code)

    def test_transpile_nested_structure(self):
        """Test transpilation of nested structures."""
        js_code = """
        <script runat='server' type="text/javascript">
        try{
        }catch(){
        }
        </script>
        """
        py_code = transpile_js_to_py(js_code)
        
        self.assertIn("try:", py_code)
        self.assertIn("except Exception:", py_code)
        self.assertNotIn("<script", py_code)


class TestCompilation(unittest.TestCase):
    """Test file compilation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_pure_ampscript_to_python(self):
        """Test compiling pure AmpScript to Python."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.ampscript")
        with open(test_file, 'w') as f:
            f.write("%%[ VAR @a SET @a = 1 ]%%")
        
        # This should succeed
        result = compile_from_file(test_file, "py")
        self.assertTrue(result)

    def test_compile_missing_file(self):
        """Test compilation with missing file."""
        result = compile_from_file("nonexistent.ampscript", "py")
        self.assertFalse(result)

    def test_compile_unsupported_language(self):
        """Test compilation with unsupported target language."""
        test_file = os.path.join(self.temp_dir, "test.ampscript")
        with open(test_file, 'w') as f:
            f.write("%%[ VAR @a ]%%")
        
        result = compile_from_file(test_file, "ruby")
        self.assertFalse(result)

    def test_compile_embedded_ampscript(self):
        """Test compiling embedded AmpScript in JavaScript."""
        test_file = os.path.join(self.temp_dir, "test_js.ampscript")
        with open(test_file, 'w') as f:
            f.write("""
            <script runat='server'>
            try {
            %%[ VAR @a SET @a = 1 ]%%
            } catch(e) {}
            </script>
            """)
        
        result = compile_from_file(test_file, "py")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
