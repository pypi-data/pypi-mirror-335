#!/usr/bin/env python3
"""
Test parsing a large TJSON5 file
This tests the parser's ability to handle complex, real-world TJSON5 files
"""
import sys
import os
import time
from pathlib import Path

# Add project directory to path to import the package
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

def main():
    print("Testing parsing of large TJSON5 file")
    print("====================================")
    
    # Import the tjson5 package
    try:
        import tjson5
        print(f"Using tjson5 version {tjson5.__version__}")
    except ImportError as e:
        print(f"Error importing tjson5: {e}")
        return 1
    
    # Path to the test file
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.tjson5")
    
    if not os.path.exists(test_file):
        print(f"Error: Test file not found at {test_file}")
        return 1
    
    # Get file size
    file_size = os.path.getsize(test_file) / 1024  # KB
    print(f"Found test file: {test_file} ({file_size:.1f} KB)")
    
    # Parse the file directly using the new load_file function
    print("\nParsing file...")
    start_time = time.time()
    try:
        data = tjson5.load_file(test_file)
        end_time = time.time()
        parse_time = end_time - start_time
        print(f"Successfully parsed file in {parse_time:.2f} seconds")
        
        # Print some basic info about the parsed content
        if isinstance(data, dict):
            print(f"\nFile structure summary:")
            print(f"- Top-level keys: {len(data.keys())}")
            print(f"- Top-level keys: {', '.join(list(data.keys())[:5])}...")
            
            # Check for some expected keys
            if "series" in data:
                print(f"- Series: {data['series']}")
            if "parts" in data and isinstance(data["parts"], list):
                print(f"- Parts: {len(data['parts'])} items")
        else:
            print(f"Note: Parsed data is not a dictionary but a {type(data).__name__}")
            
        return 0
    except Exception as e:
        end_time = time.time()
        parse_time = end_time - start_time
        print(f"× Error parsing file after {parse_time:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())