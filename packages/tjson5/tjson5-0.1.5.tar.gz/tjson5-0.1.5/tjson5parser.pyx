# cython: language_level=3
"""
Triple-JSON5 parser implemented in Cython.
This parser supports JSON5 with the addition of triple-quoted strings
and special number formats (hex: 0x, binary: 0b).
"""
import re
from cpython.ref cimport PyObject
from libc.stdlib cimport malloc, free

# Define exception class for parse errors
class TJSON5ParseError(Exception):
    """Exception raised for Triple-JSON5 parsing errors."""
    pass

# Regular expressions for number preprocessing
cdef object HEX_REGEX = re.compile(r'\b0x([0-9A-Fa-f]+)\b')
cdef object BINARY_REGEX = re.compile(r'\b0b([01]+)\b')

cdef class PositionMap:
    """Maps positions between processed and original text."""
    cdef dict _map
    
    def __cinit__(self):
        self._map = {}
    
    cpdef add_mapping(self, int processed_pos, int original_pos):
        self._map[processed_pos] = original_pos
    
    cpdef int map_to_original(self, int processed_pos):
        # Find closest position in the map
        cdef int last_mapping = 0
        cdef int last_original = 0
        
        for processed, original in sorted(self._map.items()):
            if processed > processed_pos:
                break
            last_mapping = processed
            last_original = original
        
        cdef int offset = processed_pos - last_mapping
        return last_original + offset

cdef object preprocess_triple_strings(str text):
    """
    Process triple-quoted strings and convert to standard JSON strings.
    Returns processed text and position mapping.
    """
    cdef str result = ""
    cdef int pos = 0
    cdef bint in_string = False
    cdef bint in_triple_string = False
    cdef PositionMap position_map = PositionMap()
    
    while pos < len(text):
        # Store position mapping
        position_map.add_mapping(len(result), pos)
        
        # Handle triple quotes
        if pos + 2 < len(text) and text[pos:pos+3] == '"""' and (not in_string or in_triple_string):
            # Toggle triple string state
            in_triple_string = not in_triple_string
            
            if in_triple_string:
                # Entering triple string
                result += '"'
                in_string = True
                pos += 3  # Skip the triple quotes
            else:
                # Exiting triple string
                result += '"'
                in_string = False
                pos += 3  # Skip the triple quotes
            continue
        
        # Handle regular string quotes if not in triple string
        if not in_triple_string and text[pos] == '"':
            in_string = not in_string
            result += '"'
            pos += 1
            continue
        
        # Handle escape sequences in regular strings
        if in_string and not in_triple_string and text[pos] == '\\':
            result += '\\'
            pos += 1
            if pos < len(text):
                result += text[pos]
                pos += 1
            continue
        
        # Handle quotes inside triple strings - escape them
        if in_triple_string and text[pos] == '"':
            result += '\\"'
            pos += 1
            continue
        
        # Handle newlines in triple strings
        if in_triple_string and (text[pos] == '\n' or text[pos] == '\r'):
            # Handle CRLF sequence
            if text[pos] == '\r' and pos + 1 < len(text) and text[pos + 1] == '\n':
                pos += 2
                result += '\\n'
            else:
                # Handle CR or LF individually
                pos += 1
                result += '\\n'
            continue
        
        # Add current character to result
        result += text[pos]
        pos += 1
    
    # Add final position mapping
    position_map.add_mapping(len(result), pos)
    
    return (result, position_map)

cdef str preprocess_numbers(str text):
    """
    Convert hex (0x) and binary (0b) numbers to decimal.
    """
    # Replace hex numbers with their decimal equivalents
    cdef str processed = HEX_REGEX.sub(
        lambda m: str(int(m.group(1), 16)), 
        text
    )
    
    # Replace binary numbers with their decimal equivalents
    processed = BINARY_REGEX.sub(
        lambda m: str(int(m.group(1), 2)), 
        processed
    )
    
    return processed

cdef str preprocess_comments(str text):
    """
    Remove JSON5 comments (// and /* */).
    """
    cdef str result = ""
    cdef int pos = 0
    cdef bint in_string = False
    cdef bint escape_next = False
    
    while pos < len(text):
        # Inside a string, maintain all characters
        if in_string:
            c = text[pos]
            result += c
            
            # Handle escape sequence
            if c == '\\' and not escape_next:
                escape_next = True
            else:
                if c == '"' and not escape_next:
                    in_string = False
                escape_next = False
            
            pos += 1
            continue
            
        # Check for start of string
        if text[pos] == '"':
            in_string = True
            result += '"'
            pos += 1
            continue
            
        # Check for single line comment //
        if pos + 1 < len(text) and text[pos:pos+2] == '//':
            # Skip to end of line
            pos += 2
            while pos < len(text) and text[pos] != '\n':
                pos += 1
            continue
        
        # Check for multi-line comment /* */
        if pos + 1 < len(text) and text[pos:pos+2] == '/*':
            pos += 2
            # Find the end of comment */
            while pos + 1 < len(text) and text[pos:pos+2] != '*/':
                pos += 1
            
            # Skip the closing */
            if pos + 1 < len(text):
                pos += 2
            continue
        
        # Regular character
        result += text[pos]
        pos += 1
    
    return result

cdef str preprocess_trailing_commas(str text):
    """
    Handle trailing commas in objects and arrays.
    """
    # Replace ,] with ]
    cdef str processed = re.sub(r',\s*\]', ']', text)
    # Replace ,} with }
    processed = re.sub(r',\s*\}', '}', processed)
    
    return processed

cpdef parse(str text, bint strip_comments=True):
    """
    Parse a Triple-JSON5 string and return a Python object.
    """
    # For JSON5 parsing, we need to use a specialized library
    # For this implementation, we'll use a workaround with pre-processing
    
    # Stage 1: Preprocess triple-quoted strings
    cdef tuple triple_result
    cdef str processed_text
    cdef PositionMap position_map
    
    triple_result = preprocess_triple_strings(text)
    processed_text = triple_result[0]
    position_map = triple_result[1]
    
    try:
        
        # Stage 2: Preprocess hex and binary numbers
        processed_text = preprocess_numbers(processed_text)
        
        # Stage 3: Remove comments if requested
        if strip_comments:
            processed_text = preprocess_comments(processed_text)
        
        # Stage 4: Handle trailing commas
        processed_text = preprocess_trailing_commas(processed_text)
        
        # Handle unquoted keys - convert objects like {key: value} to {"key": value}
        # This is a simplified approach - a full JSON5 parser would handle this more thoroughly
        import re
        processed_text = re.sub(r'(?<!["\'])\b([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', processed_text)
        
        # Debug - print the processed text if there's an issue
        # print(f"Processed text: {processed_text}")
        
        try:
            # Parse with Python's built-in JSON parser
            import json
            return json.loads(processed_text)
        except json.JSONDecodeError as e:
            # Map error position back to original text
            original_pos = position_map.map_to_original(e.pos)
            # Create a new error with the mapped position
            raise TJSON5ParseError(f"{e.msg} at position {original_pos} (processed text: '{processed_text}')")
    except Exception as e:
        # For unexpected errors, wrap them in our custom exception
        if not isinstance(e, TJSON5ParseError):
            raise TJSON5ParseError(f"Parsing error: {str(e)}")
        raise

cpdef loads(str text, bint strip_comments=True):
    """
    Alias for parse (matches Python's json.loads).
    """
    return parse(text, strip_comments)

cpdef load(file_obj, bint strip_comments=True):
    """
    Parse a Triple-JSON5 file object and return a Python object.
    """
    return parse(file_obj.read(), strip_comments)

cpdef dump(obj, file_obj, indent=None):
    """
    Serialize a Python object to a Triple-JSON5 file.
    (Currently uses standard JSON serialization)
    """
    import json
    return json.dump(obj, file_obj, indent=indent)

cpdef dumps(obj, indent=None):
    """
    Serialize a Python object to a Triple-JSON5 string.
    (Currently uses standard JSON serialization)
    """
    import json
    return json.dumps(obj, indent=indent)
    
# Expose preprocessing functions for testing
cpdef preprocessTripleQuotedStrings(str text):
    """
    Export the triple-quoted string preprocessing function for testing.
    """
    result = preprocess_triple_strings(text)
    return result[0]
    
cpdef preprocessHexBinary(str text):
    """
    Export the hex/binary preprocessing function for testing.
    """
    return preprocess_numbers(text)