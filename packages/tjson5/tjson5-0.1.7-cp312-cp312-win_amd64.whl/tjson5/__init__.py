"""
tjson5 - Triple-JSON5 parser for Python
=======================================

A high-performance parser for the Triple-JSON5 format.
Triple-JSON5 extends JSON5 with Python-style triple-quoted strings
and additional number formats.

Usage:
------
import tjson5

# Parse a TJSON5 string
data = tjson5.parse('{"key": "multi-line value"}')

# Load from a file
with open('config.tjson5', 'r') as f:
    config = tjson5.load(f)

# Load from a file with encoding fallback
data = tjson5.load_file('config.tjson5')

# Dump to a file (standard JSON format)
with open('output.json', 'w') as f:
    tjson5.dump(data, f, indent=2)
"""

import os
from tjson5parser import parse, load, loads, dump, dumps, TJSON5ParseError, preprocessTripleQuotedStrings, preprocessHexBinary

# Define the version
__version__ = "0.1.7"

def load_file(filename, encodings=None):
    """
    Load a TJSON5 file with automatic encoding detection.
    
    Args:
        filename: Path to the TJSON5 file
        encodings: List of encodings to try, defaults to ['utf-8', 'latin1']
    
    Returns:
        Parsed content as Python objects
        
    Raises:
        TJSON5ParseError: If the file cannot be parsed
        FileNotFoundError: If the file does not exist
    """
    if encodings is None:
        encodings = ['utf-8', 'latin1']
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    last_error = None
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding, errors='replace' if encoding == 'utf-8' else None) as f:
                return load(f)
        except Exception as e:
            last_error = e
    
    # If we get here, all encodings failed
    raise TJSON5ParseError(f"Failed to parse file with any encoding: {last_error}")