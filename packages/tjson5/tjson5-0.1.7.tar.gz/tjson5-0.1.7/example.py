#!/usr/bin/env python3
"""
Example script showing how to use the tjson5 module 
(with the new, more consistent import name)
"""
import sys
import tjson5  # Import the package, not the extension directly

# Sample Triple-JSON5 string
sample = '''{
    // This is a comment
    name: "TJSON5 Example",
    description: """
        This is a multi-line
        description using triple quotes
        with "embedded quotes" that work fine
    """,
    values: [1, 2, 0xFF, 0b1010,], // Trailing comma is allowed
}'''

def main():
    try:
        # Parse the sample string
        data = tjson5.parse(sample)
        
        # Print the results
        print("\nParsed TJSON5 data:")
        print("-" * 40)
        print(f"Name: {data['name']}")
        print(f"Description: {data['description']}")
        print(f"Values: {data['values']}")
        
        # Convert to standard JSON
        import json
        standard_json = json.dumps(data, indent=2)
        print("\nConverted to standard JSON:")
        print("-" * 40)
        print(standard_json)
        
        # You can also read from a file
        print("\nTo read from a file:")
        print("-" * 40)
        print("with open('config.tjson5', 'r') as f:")
        print("    config = tjson5.load(f)")
        
        # And write to a file (standard JSON format)
        print("\nTo write to a file:")
        print("-" * 40)
        print("with open('output.json', 'w') as f:")
        print("    tjson5.dump(data, f, indent=2)")
        
        # Show version
        print(f"\nTJSON5 Version: {tjson5.__version__}")
        
    except tjson5.TJSON5ParseError as e:
        print(f"Parse error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())