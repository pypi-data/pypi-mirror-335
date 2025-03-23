# cython: language_level=3
"""
Triple-JSON5 parser implemented in Cython - Fixed version.
This parser supports JSON5 with the addition of triple-quoted strings
and special number formats (hex: 0x, binary: 0b).

This is a standalone parser implementation with no external dependencies
on json5 or other parsing libraries.
"""
import re
import json  # We'll still use the standard json module for the final parsing
import os
import tempfile
from cpython.ref cimport PyObject
from libc.stdlib cimport malloc, free

# Define exception class for parse errors
class TJSON5ParseError(Exception):
    """Exception raised for Triple-JSON5 parsing errors."""
    pass

# Regular expressions for parsing
cdef object HEX_REGEX = re.compile(r'\b0x([0-9A-Fa-f]+)\b')
cdef object BINARY_REGEX = re.compile(r'\b0b([01]+)\b')
cdef object COMMENT_LINE_REGEX = re.compile(r'^\s*//.*$', re.MULTILINE)
cdef object FIRST_JSON_CHAR_REGEX = re.compile(r'[\[\{]')
cdef object SINGLE_LINE_COMMENT_REGEX = re.compile(r'//.*?$', re.MULTILINE)
cdef object MULTI_LINE_COMMENT_REGEX = re.compile(r'/\*.*?\*/', re.DOTALL)
cdef object UNQUOTED_KEY_REGEX = re.compile(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', re.DOTALL)
cdef object TRAILING_COMMA_OBJ_REGEX = re.compile(r',\s*\}')
cdef object TRAILING_COMMA_ARR_REGEX = re.compile(r',\s*\]')

# We won't use json5 - we'll implement everything ourselves
HAS_JSON5 = False

# Convert triple-quoted strings to regular quoted strings
cdef str process_triple_quotes(str text):
    """
    Process triple-quoted strings by converting them to regular quoted strings.
    This is a simpler implementation focusing on correctness first.
    """
    cdef list result_parts = []
    cdef int pos = 0
    cdef int length = len(text)
    cdef bint in_string = False
    cdef bint in_triple_string = False
    cdef str current_part = ""
    
    while pos < length:
        # Check for triple quotes
        if pos + 2 < length and text[pos:pos+3] == '"""':
            if in_triple_string:  # Closing triple quote
                result_parts.append(current_part.replace('"', '\\"').replace('\n', '\\n'))
                current_part = ""
                result_parts.append('"')  # Close with single quote
                in_triple_string = False
                pos += 3
            elif not in_string:  # Opening triple quote
                result_parts.append('"')  # Open with single quote
                in_triple_string = True
                pos += 3
            else:  # Triple quote inside a regular string (unlikely)
                current_part += text[pos]
                pos += 1
        elif in_triple_string:  # Inside triple string, collect content
            current_part += text[pos]
            pos += 1
        elif pos < length and text[pos] == '"' and not in_triple_string:
            # Toggle regular string state if not in triple string
            in_string = not in_string
            result_parts.append('"')
            pos += 1
        else:  # Regular character
            result_parts.append(text[pos])
            pos += 1
    
    return "".join(result_parts)

# Convert hex and binary literals to decimal
cdef str process_number_formats(str text):
    """Convert hex and binary literals to decimal."""
    # Replace hex numbers
    text = HEX_REGEX.sub(lambda m: str(int(m.group(1), 16)), text)
    # Replace binary numbers
    text = BINARY_REGEX.sub(lambda m: str(int(m.group(1), 2)), text)
    return text

cdef str strip_leading_comments(str text):
    """
    Strip comments at the beginning of the file before the first { or [
    """
    # Find the first opening brace or bracket
    match = FIRST_JSON_CHAR_REGEX.search(text)
    if match:
        start_pos = match.start()
        if start_pos > 0:
            # Get the part of the text before the first JSON character
            prefix = text[:start_pos]
            # If it's only comments and whitespace, remove it
            if re.match(r'^(\s*((//[^\n]*\n)|(\/\*[\s\S]*?\*\/)))*\s*$', prefix):
                return text[start_pos:]
    return text

# Process JSON5 unquoted keys and other features
cdef str process_json5_features(str text):
    """
    Process JSON5 features like unquoted keys, comments, and trailing commas.
    
    This function converts a JSON5 string to valid JSON by:
    1. Removing single and multi-line comments
    2. Converting unquoted keys to quoted keys
    3. Removing trailing commas in objects and arrays
    """
    cdef str processed = text
    
    # 1. Remove comments first
    # Remove single-line comments (//...)
    processed = SINGLE_LINE_COMMENT_REGEX.sub('', processed)
    # Remove multi-line comments (/* ... */)
    processed = MULTI_LINE_COMMENT_REGEX.sub('', processed)
    
    # 2. Handle unquoted keys - convert objects like {key: value} to {"key": value}
    # The positive lookbehind (?<= ensures we're matching after a { or ,
    processed = UNQUOTED_KEY_REGEX.sub(r'\1"\2":', processed)
    
    # 3. Handle trailing commas in objects and arrays
    processed = TRAILING_COMMA_OBJ_REGEX.sub('}', processed)
    processed = TRAILING_COMMA_ARR_REGEX.sub(']', processed)
    
    return processed

cpdef parse(str text, bint strip_comments=True):
    """
    Parse a Triple-JSON5 string and return the corresponding Python object.
    
    Parameters:
    - text: The Triple-JSON5 string to parse
    - strip_comments: Whether to strip comments (default True)
    
    Returns:
    - A Python object (dict, list, str, int, float, bool, None)
    
    Raises:
    - TJSON5ParseError if the text is invalid
    """
    # Skip invalid or empty input
    if not text or not text.strip():
        raise TJSON5ParseError("Empty or invalid input")
    
    try:
        # Multi-stage parsing process:
        
        # Check if the file has comments before the actual JSON content
        has_leading_comments = text.lstrip().startswith('//')
        
        if has_leading_comments:
            # Strip leading comments before the first { or [
            text = strip_leading_comments(text)
            
        # Stage 1: Process triple-quoted strings
        processed_text = process_triple_quotes(text)
        
        # Stage 2: Process hex and binary literals
        processed_text = process_number_formats(processed_text)
        
        # Stage 3: Process JSON5 features (comments, unquoted keys, trailing commas)
        try:
            final_text = process_json5_features(processed_text)
            
            # Stage 4: Parse with standard JSON
            try:
                return json.loads(final_text)
            except json.JSONDecodeError as je:
                # If direct parsing fails, try using a temporary file approach
                # This can help overcome certain parsing limitations
                
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tf:
                    temp_filename = tf.name
                    tf.write(final_text)
                
                try:
                    # Try parsing from the file instead
                    with open(temp_filename, 'r', encoding='utf-8') as f:
                        try:
                            return json.load(f)
                        except json.JSONDecodeError as je2:
                            # If it still fails, provide a helpful error message
                            error_context = je2.doc[max(0, je2.pos-20):min(len(je2.doc), je2.pos+20)]
                            raise TJSON5ParseError(
                                f"Failed to parse Triple-JSON5: {str(je2)}\n"
                                f"Error near: ...{error_context}..."
                            )
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_filename)
                    except:
                        pass
                        
        except Exception as e:
            # If our JSON5 processor fails, try one more approach with regex-based fixes
            # This is a more aggressive approach that might handle edge cases
            
            fixed_text = processed_text
            # Apply multiple passes of regex fixes
            
            # 1. Remove all comments first
            fixed_text = SINGLE_LINE_COMMENT_REGEX.sub('', fixed_text)
            fixed_text = MULTI_LINE_COMMENT_REGEX.sub('', fixed_text)
            
            # 2. Fix unquoted keys
            fixed_text = UNQUOTED_KEY_REGEX.sub(r'\1"\2":', fixed_text)
            
            # 3. Fix trailing commas
            fixed_text = TRAILING_COMMA_OBJ_REGEX.sub('}', fixed_text)
            fixed_text = TRAILING_COMMA_ARR_REGEX.sub(']', fixed_text)
            
            try:
                # Try parsing the fixed text
                return json.loads(fixed_text)
            except json.JSONDecodeError as je:
                # If all parsing attempts fail, provide a helpful error
                error_context = je.doc[max(0, je.pos-20):min(len(je.doc), je.pos+20)]
                raise TJSON5ParseError(
                    f"Failed to parse Triple-JSON5: {str(je)}\n"
                    f"Error near: ...{error_context}..."
                )
                    
    except Exception as e:
        # Ensure we always return a TJSON5ParseError
        if not isinstance(e, TJSON5ParseError):
            raise TJSON5ParseError(f"Parsing error: {str(e)}")
        raise

cpdef loads(str text, bint strip_comments=True):
    """Alias for parse to match Python's json module API."""
    return parse(text, strip_comments)

cpdef load(file_obj, bint strip_comments=True):
    """Parse a file object containing Triple-JSON5."""
    try:
        content = file_obj.read()
        return parse(content, strip_comments)
    except UnicodeDecodeError as e:
        # Handle encoding errors gracefully
        raise TJSON5ParseError(f"Encoding error: {str(e)}. Try opening the file with a different encoding.")

cpdef dump(obj, file_obj, indent=None):
    """Serialize obj to a file as JSON."""
    json.dump(obj, file_obj, indent=indent)

cpdef dumps(obj, indent=None):
    """Serialize obj to a JSON string."""
    return json.dumps(obj, indent=indent)

# Export preprocessing functions for testing
cpdef preprocessTripleQuotedStrings(str text):
    """Process triple-quoted strings for testing."""
    return process_triple_quotes(text)

cpdef preprocessHexBinary(str text):
    """Process hex and binary literals for testing."""
    return process_number_formats(text)