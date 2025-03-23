# TJSON5 Parser

A high-performance Python parser for Triple-JSON5 (TJSON5) files implemented in Cython.

## Features

- Parses TJSON5 files into Python objects
- Supports all standard JSON5 features:
  - Comments (single and multi-line)
  - Trailing commas in objects and arrays
  - Unquoted object keys
- Triple-JSON5 extensions:
  - Triple-quoted strings (`"""`) for multi-line text without escaping
  - Hexadecimal number literals (`0xFF`)
  - Binary number literals (`0b1010`)
- Automatic encoding detection and fallback
- Helpful error messages with context
- No external dependencies (pure Python/Cython implementation)

## Installation

```bash
# Install from source
git clone https://github.com/kristofmulier/triple-json5.git
cd triple-json5/python_tjson5
pip install -e .
```

## Usage

```python
import tjson5

# Parse a TJSON5 string
data = tjson5.parse("""
{
    // This is a comment
    name: "TJSON5 Example",
    description: """
        This is a multi-line
        description using triple quotes
    """,
    values: [1, 2, 0xFF, 0b1010,], // Trailing comma is allowed
}
""")

print(data["name"])  # "TJSON5 Example"
print(data["values"])  # [1, 2, 255, 10]

# Read from a file with automatic encoding detection
config = tjson5.load_file("config.tjson5")

# Or traditional way
with open("config.tjson5", "r", encoding="utf-8") as f:
    config = tjson5.load(f)

# Write to JSON (standard JSON format)
with open("output.json", "w") as f:
    tjson5.dump(data, f, indent=2)
```

## Building the Extension

```bash
# Install development dependencies
pip install cython

# Build the extension in place
python setup.py build_ext --inplace

# Run tests
python test_tjson5.py
```

## How it Works

The parser uses a multi-stage process without any external dependencies:

1. Preprocesses triple-quoted strings, converting them to standard JSON strings
2. Converts hex and binary numbers to decimal
3. Removes comments (both single-line and multi-line)
4. Handles unquoted keys by adding proper quotes
5. Removes trailing commas in objects and arrays
6. Uses multiple fallback strategies for robust parsing
7. Passes the processed JSON to Python's built-in JSON parser

All error positions are mapped back to the original source for accurate error reporting with helpful context.

## Performance

The Cython implementation provides near-native performance, making it suitable for parsing large TJSON5 files quickly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.