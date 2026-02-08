# =============================================================================
# amp.py
#
# Copyright (C) 2023 B. Wang
# All rights reserved.
# Licensed under the BSD open source license agreement
#
# AmpScript compiler and interpreter for JavaScript and Python targets.
# =============================================================================
"""AmpScript compiler and interpreter main module."""

import logging
import argparse
import sys

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from src import ampinterpreter, ampyacc, ampcompiler

# Constants
APP_VERSION = "0.0.5"
LOG_FILE = "parse.log"
HISTORY_FILE = ".history.txt"
PROMPT_TEXT = "amp > "

# Supported target languages
SUPPORTED_LANGUAGES = {"py", "js"}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    filemode="w"
)
logger = logging.getLogger(__name__)


def detect_javascript(content):
    """
    Detect if content contains JavaScript code.

    Args:
        content: File content to analyze

    Returns:
        True if JavaScript patterns are detected, False otherwise
    """
    import re
    
    # Check for common JavaScript patterns
    js_patterns = [
        r'<script[^>]*>',           # Script tags
        r'\bvar\s+\w+',             # var declarations
        r'\blet\s+\w+',             # let declarations
        r'\bconst\s+\w+',           # const declarations
        r'\bfunction\s+\w+\s*\(',  # function declarations
        r'\btry\s*{',               # try blocks
        r'\bcatch\s*\(',            # catch blocks
        r'console\.\w+\(',          # console calls
    ]
    
    for pattern in js_patterns:
        if re.search(pattern, content):
            return True
    
    return False


def extract_ampscript_blocks(content):
    """
    Extract AmpScript blocks from JavaScript/HTML content.

    AmpScript can be embedded in JavaScript using %%[ and ]%% delimiters.
    This function extracts all AmpScript blocks and returns them.

    Args:
        content: File content that may contain embedded AmpScript

    Returns:
        Tuple of (extracted_ampscript, is_embedded)
        extracted_ampscript: Concatenated AmpScript code
        is_embedded: True if AmpScript was found embedded in other code
    """
    start_delim = '%%['
    end_delim = ']%%'

    ampscript_blocks = []
    is_embedded = False

    # Find all AmpScript blocks
    content_copy = content
    while start_delim in content_copy:
        start_idx = content_copy.find(start_delim)
        end_idx = content_copy.find(end_delim, start_idx)

        if end_idx == -1:
            logger.error("Unclosed AmpScript block: found %%[ but no ]%%")
            break

        # Extract block content (between delimiters)
        block_start = start_idx + len(start_delim)
        block_content = content_copy[block_start:end_idx]
        ampscript_blocks.append(block_content)

        # Mark as embedded if there's content before/after the AmpScript
        if start_idx > 0 or end_idx + len(end_delim) < len(content_copy):
            is_embedded = True

        # Continue searching after this block
        content_copy = content_copy[end_idx + len(end_delim):]

    if ampscript_blocks:
        # Return list of blocks for separate processing
        return ampscript_blocks, is_embedded
    else:
        # No embedded blocks found, return original content
        return content, False


def transpile_js_to_py(js_code):
    """
    Transpile JavaScript code to Python.

    Handles various JavaScript constructs including:
    - Script tags
    - Variable declarations (var, let, const)
    - Try-catch blocks
    - Function declarations
    - Control structures (if, for, while)
    - Braces and semicolons

    Args:
        js_code: JavaScript code string

    Returns:
        Python equivalent code
    """
    import re
    
    # Start with ampfunctions import since JS code will use it
    py_code = "from src import ampfunctions\n"
    py_code += js_code

    # Remove HTML script tags
    py_code = re.sub(r"<script[^>]*>", '', py_code, flags=re.IGNORECASE)
    py_code = re.sub(r"</script>", '', py_code, flags=re.IGNORECASE)
    
    # Don't remove other HTML tags - they might interfere with < operator in for loops!
    # py_code = re.sub(r'<[^>]+>', '', py_code)

    # Remove JavaScript comments (// and /* */)
    py_code = re.sub(r'//.*?$', '', py_code, flags=re.MULTILINE)
    py_code = re.sub(r'/\*[\s\S]*?\*/', '', py_code)

    # Replace try-catch blocks
    # try { ... } catch (e) { ... } → try: ... except Exception as e: ...
    py_code = re.sub(r'\btry\s*\{', 'try:', py_code)
    py_code = re.sub(r'\}\s*catch\s*\(([^)]*)\)\s*\{', r'except Exception as \1:', py_code)
    
    # IMPORTANT: Replace for loops BEFORE if statements to avoid breaking nested if logic
    def replace_for_loop(match):
        init = match.group(1).strip()
        condition = match.group(2).strip()
        increment = match.group(3).strip()
        
        # Convert increment to Python
        if '++' in increment:
            var = increment.replace('++', '').strip()
            py_increment = f'{var} += 1'
        elif '--' in increment:
            var = increment.replace('--', '').strip()
            py_increment = f'{var} -= 1'
        elif '+=' in increment or '-=' in increment:
            py_increment = increment
        else:
            py_increment = increment
        
        # Insert increment as a special marker that will be moved to end of loop
        # Also mark the loop so we can find its closing brace
        return f'{init}\nwhile {condition}:\n##LOOP_END_INCREMENT:{py_increment}##\n##FOR_LOOP_START##'
    
    py_code = re.sub(r'\bfor\s*\(([^;]+);([^;]+);([^)]+)\)\s*{', replace_for_loop, py_code)

    # Convert var/let/const declarations to Python assignments
    def split_top_level(text, delimiter=','):
        parts = []
        current = []
        depth_paren = 0
        depth_bracket = 0
        depth_brace = 0
        in_single = False
        in_double = False

        for ch in text:
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if ch == '(':
                    depth_paren += 1
                elif ch == ')':
                    depth_paren = max(depth_paren - 1, 0)
                elif ch == '[':
                    depth_bracket += 1
                elif ch == ']':
                    depth_bracket = max(depth_bracket - 1, 0)
                elif ch == '{':
                    depth_brace += 1
                elif ch == '}':
                    depth_brace = max(depth_brace - 1, 0)

            if (
                ch == delimiter
                and not in_single
                and not in_double
                and depth_paren == 0
                and depth_bracket == 0
                and depth_brace == 0
            ):
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
            else:
                current.append(ch)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)
        return parts

    def convert_object_literal(value_text):
        stripped = value_text.strip()
        if not (stripped.startswith('{') and stripped.endswith('}')):
            return value_text
        inner = stripped[1:-1].strip()
        if not inner:
            return "dict()"
        entries = split_top_level(inner, delimiter=',')
        args = []
        for entry in entries:
            if ':' not in entry:
                args.append(entry.strip())
                continue
            key, val = entry.split(':', 1)
            key = key.strip()
            val = val.strip()
            if key.replace('_', '').isalnum() and key[0].isalpha():
                args.append(f"{key}={val}")
            else:
                # Fallback to a dict literal wrapped in dict() to keep syntax valid
                return f"dict({{{key}: {val}}})"
        return "dict(" + ", ".join(args) + ")"

    def replace_js_declaration(match):
        decl_body = match.group(1).strip()
        parts = split_top_level(decl_body, delimiter=',')
        converted = []
        for part in parts:
            if '=' in part:
                name, value = part.split('=', 1)
                value = convert_object_literal(value.strip())
                converted.append(f"{name.strip()} = {value}")
            else:
                converted.append(f"{part} = None")
        return "\n".join(converted)

    py_code = re.sub(r'\b(?:var|let|const)\s+([^;]+);?', replace_js_declaration, py_code)

    # Replace while loops: while (condition) { → while condition:
    py_code = re.sub(r'\bwhile\s*\(([^)]*)\)\s*{', r'while \1:', py_code)

    # Replace if statements: if (condition) { → if condition:
    # This must come AFTER for loop replacement
    py_code = re.sub(r'\bif\s*\(([^)]*)\)\s*{', r'if \1:', py_code)
    py_code = re.sub(r'}\s*else\s*if\s*\(([^)]*)\)\s*{', r'elif \1:', py_code)
    py_code = re.sub(r'}\s*else\s*{', 'else:', py_code)

    # Replace JavaScript function calls to use ampfunctions library
    # Convert console.log/warn/error/info to Write function
    def replace_js_function_calls(code):
        # Pattern: functionName(args...)
        converted = code
        
        # console.log/warn/error/info -> ampfunctions.Write
        converted = re.sub(
            r'\bconsole\.(log|warn|error|info)\s*\(',
            r"getattr(ampfunctions,'Write')(",
            converted
        )
        
        # Direct Write() calls -> ampfunctions.Write
        converted = re.sub(
            r'\bWrite\s*\(',
            r"getattr(ampfunctions,'Write')(",
            converted
        )
        
        return converted
    
    py_code = replace_js_function_calls(py_code)

    # Convert JavaScript property access patterns FIRST, before any other transformations
    # Only convert .property where property is a simple identifier (not a number like .0, .1)
    # This converts obj.propertyName to obj["propertyName"]
    py_code = re.sub(
        r'(\w+)\.([a-zA-Z_][a-zA-Z0-9_]*)(?![\w(])',
        r'\1["\2"]',
        py_code
    )

    # Convert JavaScript .length access pattern to len()
    # Now that we converted property access, ["length"] matches what used to be .length
    py_code = re.sub(r'(\w+)\["length"\]', r'len(\1)', py_code)

    # Handle JavaScript's implicit string coercion in concatenation
    # Convert patterns like "string" + var to "string" + str(var)
    def coerce_string_concatenation(code):
        # Match "string" + expression, where expression could be a variable name or dict access
        lines = code.split('\n')
        result_lines = []
        
        for line in lines:
            # Pattern: "string" + variable_or_expr
            line = re.sub(
                r'("(?:[^"\\]|\\.)*")\s*\+\s*(?!str\()(\w+(?:\[[^\]]+\])?)',
                r'\1 + str(\2)',
                line
            )
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    py_code = coerce_string_concatenation(py_code)

    # Replace logical operators
    py_code = re.sub(r'\&\&', 'and', py_code)
    py_code = re.sub(r'\|\|', 'or', py_code)
    py_code = re.sub(r'!([^=])', r'not \1', py_code)

    # Convert JavaScript .length to Python len()
    py_code = re.sub(r'\b([A-Za-z_][A-Za-z0-9_]*)\.length\b', r'len(\1)', py_code)

    # Replace comparison operators
    py_code = re.sub(r'===', '==', py_code)
    py_code = re.sub(r'!==', '!=', py_code)

    # Find and mark the end of for-loop bodies before removing all braces
    # Look for ##FOR_LOOP_START## and find its matching closing brace
    lines = py_code.split('\n')
    brace_depth = 0
    in_for_loop = False
    for i, line in enumerate(lines):
        if '##FOR_LOOP_START##' in line:
            brace_depth = 1  # We're inside the for loop
            in_for_loop = True
            lines[i] = line.replace('##FOR_LOOP_START##', '')  # Remove the marker
        elif in_for_loop:
            # Count braces to find the matching closing brace
            brace_depth += line.count('{')
            brace_depth -= line.count('}')
            if brace_depth == 0 and '}' in line:
                # This is the closing brace of the for loop
                lines[i] = line.replace('}', '##END_FOR_LOOP##', 1)
                in_for_loop = False
    py_code = '\n'.join(lines)

    # Remove remaining curly braces (convert to Python block)
    # Skip object literals: look for patterns like = { ... }
    # Replace { } with dict() when they appear after = sign
    py_code = re.sub(r'=\s*\{([^}]+)\}(?=\s*[;$\n])', lambda m: f"= dict({m.group(1)})", py_code)
    
    # Replace remaining closing braces with dedent markers (except ones already marked)
    # This preserves block structure information for indentation
    lines = py_code.split('\n')
    for i, line in enumerate(lines):
        if '}' in line and '##END_FOR_LOOP##' not in line:
            # This is a regular closing brace - mark it for dedent
            lines[i] = line.replace('}', '##DEDENT##')
    py_code = '\n'.join(lines)
    
    # Now remove any remaining braces (opening braces and marked closing braces)
    py_code = py_code.replace('{', '')

    # Remove semicolons
    py_code = py_code.replace(';', '')

    # Clean up multiple colons
    py_code = re.sub(r':+', ':', py_code)

    # Clean up whitespace and empty lines
    lines = [line.rstrip() for line in py_code.split('\n')]
    py_code = '\n'.join(line for line in lines if line.strip())
    
    # Now add proper Python indentation
    py_code = add_proper_indentation(py_code)

    return py_code


def add_proper_indentation(code):
    """
    Add proper 4-space indentation to Python code.
    
    Args:
        code: Python code string with potential indentation issues
        
    Returns:
        Properly indented Python code
    """
    import re
    
    lines = code.split('\n')
    result = []
    indent_level = 0
    indent_stack = []  # Track block types and their indent levels
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            result.append('')
            continue
        
        # Skip loop increment markers for now - will process later
        if '##LOOP_END_INCREMENT:' in stripped:
            result.append(stripped)  # Keep as-is for now
            continue
        
        # Handle dedent markers - decrease indent level
        if '##DEDENT##' in stripped or '##END_FOR_LOOP##' in stripped:
            if indent_level > 0:
                indent_level -= 1
            # Remove the marker and check if there's content left
            cleaned = stripped.replace('##DEDENT##', '').replace('##END_FOR_LOOP##', '').strip()
            if cleaned:
                result.append('    ' * indent_level + cleaned)
            # Pop from stack if we're closing a block
            if indent_stack:
                indent_stack.pop()
            continue
        
        # Handle dedent keywords that close blocks
        if stripped.startswith('except'):
            # Find matching try indent level
            while indent_stack and indent_stack[-1][0] != 'try':
                indent_stack.pop()
            if indent_stack:
                indent_level = indent_stack[-1][1]
                indent_stack.pop()
            indent_stack.append(('except', indent_level))
            result.append('    ' * indent_level + stripped)
            if stripped.endswith(':'):
                indent_level += 1
            continue
        elif stripped.startswith('finally'):
            # Finally should match the try level
            while indent_stack and indent_stack[-1][0] not in ('try', 'except'):
                indent_stack.pop()
            if indent_stack:
                indent_level = indent_stack[-1][1]
                indent_stack.pop()
            result.append('    ' * indent_level + stripped)
            if stripped.endswith(':'):
                indent_level += 1
                indent_stack.append(('finally', indent_level - 1))
            continue
        elif stripped.startswith('elif') or stripped.startswith('else:'):
            # elif/else should dedent to match the if
            if indent_level > 0:
                indent_level -= 1
            result.append('    ' * indent_level + stripped)
            if stripped.endswith(':'):
                indent_level += 1
            continue
        
        # Add the line with current indentation
        result.append('    ' * indent_level + stripped)
        
        # Track blocks and increase indent after colon
        if stripped.endswith(':'):
            if stripped.startswith('try:'):
                indent_stack.append(('try', indent_level))
            elif stripped.startswith('def ') or stripped.startswith('class '):
                indent_stack.append(('def', indent_level))
            elif stripped.startswith('if ') or stripped.startswith('for ') or stripped.startswith('while '):
                indent_stack.append(('control', indent_level))
            indent_level += 1
    
    # Post-process: Move loop increment markers to end of their blocks
    final_result = []
    i = 0
    pending_increment = None  # Store increment to add at end of block
    pending_indent = None  # Store indent level for the increment
    
    while i < len(result):
        line = result[i]
        
        if '##LOOP_END_INCREMENT:' in line:
            # Extract the increment statement and store it
            match = re.search(r'##LOOP_END_INCREMENT:(.+?)##', line)
            if match:
                pending_increment = match.group(1)
                # Get the indent of the while statement (previous non-empty line)
                prev_idx = i - 1
                while prev_idx >= 0 and not result[prev_idx].strip():
                    prev_idx -= 1
                if prev_idx >= 0:
                    while_indent = len(result[prev_idx]) - len(result[prev_idx].lstrip())
                    pending_indent = while_indent + 4  # One level deeper
            i += 1
            continue  # Skip the marker line
        
        # Check if this is the end of the for loop
        if '##END_FOR_LOOP##' in line:
            if pending_increment:
                # Insert the increment before this marker
                final_result.append('    ' * (pending_indent // 4) + pending_increment)
                pending_increment = None
                pending_indent = None
            # The ##END_FOR_LOOP## marker has already been processed by add_proper_indentation
            # Just skip it here
            i += 1
            continue
        
        # Old logic: If no ##END_FOR_LOOP## marker found, fall back to indent-based detection
        if pending_increment and line.strip():
            line_indent = len(line) - len(line.lstrip())
            # If this line is at less indent than the loop body, insert increment before it
            if line_indent < pending_indent:
                final_result.append('    ' * (pending_indent // 4) + pending_increment)
                pending_increment = None
                pending_indent = None
        
        final_result.append(line)
        i += 1
    
    # Add any remaining increment at the end
    if pending_increment:
        final_result.append('    ' * (pending_indent // 4) + pending_increment)
    
    return '\n'.join(final_result)


def compile_from_file(input_file, target_language):
    """
    Compile an AmpScript file to the target language.

    Handles both pure AmpScript files and files with embedded AmpScript
    within JavaScript code. Uses enhanced lexer but maintains separation
    to avoid grammar conflicts.

    Args:
        input_file: Path to the input AmpScript file.
        target_language: Target language ("py" or "js").

    Returns:
        True if compilation was successful, False otherwise.
    """
    try:
        with open(input_file, encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        return False
    except IOError as e:
        logger.error(f"Error reading file: {e}")
        return False

    if not data.strip():
        logger.error("Empty input file")
        return False

    # Check if file contains JavaScript by looking for patterns
    has_javascript = detect_javascript(data)
    
    # Extract AmpScript blocks
    ampscript_code, is_embedded = extract_ampscript_blocks(data)

    if has_javascript and is_embedded and target_language == "py":
        # JavaScript with embedded AmpScript - handle separately to avoid conflicts
        if isinstance(ampscript_code, str) and not ampscript_code.strip():
            # Pure JavaScript
            py_code = transpile_js_to_py(data)
            print(py_code)
            return True
        
        # ampscript_code is now a list of blocks
        ampscript_blocks = ampscript_code if isinstance(ampscript_code, list) else [ampscript_code]
        
        # Compile each AmpScript block separately
        compiled_blocks = []
        for block in ampscript_blocks:
            prog = ampyacc.parse(block)
            if not prog:
                logger.error("Parsing AmpScript block failed")
                return False
            
            compiler = ampcompiler.AmpCompilerToPy(prog)
            
            try:
                import io
                from contextlib import redirect_stdout
                
                compiled_output = io.StringIO()
                with redirect_stdout(compiled_output):
                    compiler.compile()
                
                ampscript_compiled = compiled_output.getvalue()
                
                # Indent AmpScript code
                indented_ampscript = '\n'.join('    ' + line if line.strip() else line 
                                               for line in ampscript_compiled.split('\n'))
                compiled_blocks.append(indented_ampscript)
                
            except RuntimeError as e:
                logger.error(f"Compilation error: {e}")
                return False
        
        # Extract JavaScript wrapper and replace AmpScript blocks
        wrapper = data
        start_delim = '%%['
        end_delim = ']%%'
        
        # Replace each block with a unique marker
        block_markers = []
        block_idx = 0
        while start_delim in wrapper:
            start_idx = wrapper.find(start_delim)
            end_idx = wrapper.find(end_delim, start_idx)
            if end_idx == -1:
                break
            marker = f'###AMPSCRIPT_BLOCK_{block_idx}###'
            block_markers.append(marker)
            wrapper = wrapper[:start_idx] + marker + wrapper[end_idx + len(end_delim):]
            block_idx += 1
        
        # Transpile JavaScript to Python
        py_wrapper = transpile_js_to_py(wrapper)
        
        # Replace each marker with its corresponding compiled block
        final_output = py_wrapper
        for i, marker in enumerate(block_markers):
            if i < len(compiled_blocks):
                final_output = final_output.replace(marker, '\n' + compiled_blocks[i])
        
        print(final_output)
        return True
    else:
        # Pure AmpScript - use parser directly
        # Parse the AmpScript code
        # ampscript_code might be a list or string depending on is_embedded
        if is_embedded:
            # If embedded but no JavaScript, join the blocks
            code_to_parse = '\n'.join(ampscript_code) if isinstance(ampscript_code, list) else ampscript_code
        else:
            # Not embedded, use original data
            code_to_parse = data
        
        prog = ampyacc.parse(code_to_parse)
        if not prog:
            logger.error("Parsing failed")
            return False

        # Select compiler
        if target_language == "py":
            compiler = ampcompiler.AmpCompilerToPy(prog)
        elif target_language == "js":
            compiler = ampcompiler.AmpCompilerToJs(prog)
        else:
            logger.error(f"Unsupported language: {target_language}")
            return False

        # Compile
        try:
            compiler.compile()
            return True
        except RuntimeError as e:
            logger.error(f"Compilation error: {e}")
            return False


def run_interactive_mode():
    """Run the interactive REPL mode."""
    interpreter = ampinterpreter.AmpInterpreter({})
    print(f"(o) Amp {APP_VERSION}")

    while True:
        try:
            user_input = prompt(
                PROMPT_TEXT,
                history=FileHistory(HISTORY_FILE),
                auto_suggest=AutoSuggestFromHistory()
            )
        except EOFError:
            break
        except KeyboardInterrupt:
            continue

        if not user_input.strip():
            continue

        user_input += "\n"

        prog = ampyacc.parse(user_input, debug=logger)

        if not prog:
            continue

        try:
            interpreter.add_statements(prog)
            interpreter.interpret()
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")


def main():
    """Main entry point for the AmpScript compiler."""
    # Ensure redirected output is UTF-8 instead of UTF-16 on Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="AmpScript compiler with support for Python and JavaScript targets"
    )

    parser.add_argument(
        "-l", "--language",
        type=str,
        choices=list(SUPPORTED_LANGUAGES),
        help="Target language (py for Python, js for JavaScript)"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Path to input AmpScript file"
    )

    args = parser.parse_args()

    # If both arguments are provided, run compilation mode
    if args.language and args.input:
        success = compile_from_file(args.input, args.language)
        sys.exit(0 if success else 1)
    else:
        # Run interactive mode
        try:
            run_interactive_mode()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)


if __name__ == "__main__":
    main()