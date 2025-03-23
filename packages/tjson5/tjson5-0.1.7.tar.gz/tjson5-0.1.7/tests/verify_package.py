#!/usr/bin/env python3
"""
Verify the TJSON5 package is working correctly
"""
import sys
import os
from pathlib import Path

# Add project directory to path to import the package
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

def main():
    """Test all package functionality"""
    print("Verifying TJSON5 package functionality")
    print("===============================")
    
    try:
        import tjson5
        print(f"Imported tjson5 package successfully (version {tjson5.__version__})")
    except ImportError as e:
        print(f"Error importing tjson5: {e}")
        return 1
    
    # Test basic parsing
    try:
        print("\nTest 1: Basic parsing...")
        data = tjson5.parse('{"key": "value", "number": 42}')
        assert data["key"] == "value" and data["number"] == 42
        print("Basic parsing works")
    except Exception as e:
        print(f"Error in basic parsing: {e}")
        return 1
    
    # Test triple-quoted strings
    try:
        print("\nTest 2: Triple-quoted strings...")
        data = tjson5.parse('{"multiline": """line1\nline2"""}')
        assert data["multiline"] == "line1\nline2"
        print("Triple-quoted strings work")
    except Exception as e:
        print(f"Error in triple-quoted strings: {e}")
        return 1
    
    # Test hex numbers
    try:
        print("\nTest 3: Hex numbers...")
        data = tjson5.parse('{"hex": 0xff}')
        assert data["hex"] == 255
        print("Hex numbers work")
    except Exception as e:
        print(f"Error in hex numbers: {e}")
        return 1
    
    # Test binary numbers
    try:
        print("\nTest 4: Binary numbers...")
        data = tjson5.parse('{"binary": 0b1010}')
        assert data["binary"] == 10
        print("Binary numbers work")
    except Exception as e:
        print(f"Error in binary numbers: {e}")
        return 1
    
    # Test loading from a file
    try:
        print("\nTest 5: Loading from a file...")
        test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.tjson5")
        with open(test_file, 'r', encoding='utf-8') as f:
            data = tjson5.load(f)
        assert "series" in data
        assert "parts" in data
        print("Loading from a file works")
    except Exception as e:
        print(f"Error loading from a file: {e}")
        return 1
    
    print("\nAll tests passed! The tjson5 package is working correctly.")
    print("\nReady to publish to PyPI!")
    print("Run the appropriate build script:")
    print("  - On Windows: build.bat")
    print("  - On Linux: ./build_pypi.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())