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

# Dump to a file (standard JSON format)
with open('output.json', 'w') as f:
    tjson5.dump(data, f, indent=2)
"""

# Import all functions from the C extension module
from tjson5parser import *

# Define the version
__version__ = "0.1.3"