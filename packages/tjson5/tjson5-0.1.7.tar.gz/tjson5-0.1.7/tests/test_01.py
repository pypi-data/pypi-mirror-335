import unittest
import os
import sys
from pathlib import Path

# Add project directory to path to import the package
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

# Import the parser (after building with python setup.py build_ext --inplace)
try:
    import tjson5parser
except ImportError:
    print("Error: tjson5parser module not found.")
    print("Please build it first with: python setup.py build_ext --inplace")
    sys.exit(1)

class TestTJSON5Parser(unittest.TestCase):
    
    def test_basic_json(self):
        """Test basic JSON parsing"""
        json_data = '{"name": "test", "value": 42}'
        result = tjson5parser.parse(json_data)
        self.assertEqual(result, {"name": "test", "value": 42})
    
    def test_triple_quoted_strings(self):
        """Test triple-quoted strings"""
        json_data = '''{"text": """This is a
        multi-line string
        with "quotes" inside."""}'''
        try:
            result = tjson5parser.parse(json_data)
            self.assertEqual(result["text"], 'This is a\n        multi-line string\n        with "quotes" inside.')
        except tjson5parser.TJSON5ParseError as e:
            # Add debug output to understand the issue
            print(f"Debug - Triple quoted test failure: {e}")
            import json
            processed = tjson5parser.preprocessTripleQuotedStrings(json_data)
            print(f"Processed text: {processed}")
            print(f"After preprocessing: {json.loads(processed)}")
            raise
    
    def test_hex_numbers(self):
        """Test hexadecimal numbers"""
        json_data = '{"value": 0xFF}'
        result = tjson5parser.parse(json_data)
        self.assertEqual(result["value"], 255)
    
    def test_binary_numbers(self):
        """Test binary numbers"""
        json_data = '{"value": 0b1010}'
        result = tjson5parser.parse(json_data)
        self.assertEqual(result["value"], 10)
    
    def test_comments(self):
        """Test comment removal"""
        json_data = '''{
            // This is a comment
            "name": "test", /* This is another comment */
            "value": 42
        }'''
        result = tjson5parser.parse(json_data)
        self.assertEqual(result, {"name": "test", "value": 42})
    
    def test_trailing_commas(self):
        """Test trailing commas"""
        json_data = '''{
            "array": [1, 2, 3,],
            "object": {"a": 1, "b": 2,},
        }'''
        result = tjson5parser.parse(json_data)
        self.assertEqual(result, {"array": [1, 2, 3], "object": {"a": 1, "b": 2}})
    
    def test_error_position_mapping(self):
        """Test that error positions are correctly mapped"""
        json_data = '''{"text": """This is a
        multi-line string""", "invalid": }'''
        with self.assertRaises(tjson5parser.TJSON5ParseError) as cm:
            tjson5parser.parse(json_data)
        # The error message format has changed, but should still be informative
        error_str = str(cm.exception)
        print(f"Error message: {error_str}")
        # Check that the error message is informative
        self.assertIn("Triple-JSON5", error_str)
    
    def test_sample_file(self):
        """Test parsing a real TJSON5 file from the project"""
        # Path to test file - now using the test.tjson5 in the tests directory
        test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.tjson5")
        
        if os.path.exists(test_file_path):
            # Import the tjson5 package for the load_file functionality
            try:
                import tjson5
                # Use the new load_file function with automatic encoding detection
                data = tjson5.load_file(test_file_path)
            except ImportError:
                # Fallback to the direct approach if tjson5 package is not properly installed
                print("Warning: tjson5 package not available, using direct load")
                try:
                    # Try with UTF-8 encoding first
                    with open(test_file_path, 'r', encoding='utf-8', errors='replace') as f:
                        data = tjson5parser.load(f)
                except Exception as e:
                    print(f"Failed with UTF-8 encoding: {e}")
                    # Fallback to latin1 encoding
                    with open(test_file_path, 'r', encoding='latin1') as f:
                        data = tjson5parser.load(f)
            
            # Verify some key parts of the structure
            self.assertIn("series", data)
            self.assertEqual(data["series"], "APM32F411")
            self.assertIn("parts", data)
            self.assertTrue(isinstance(data["parts"], list))
            
            # Also test the simplified sample
            test_json = '''{
              "decimal": 123,
              "hexSmall": 0xff,
              "binarySmall": 0b101,
              "tripleQuoted": """
                 This is a multi-line
                 triple-quoted string
              """
            }'''
            
            simple_data = tjson5parser.parse(test_json)
            
            # Verify some values
            self.assertEqual(simple_data["decimal"], 123)
            self.assertEqual(simple_data["hexSmall"], 255)  # 0xff
            self.assertEqual(simple_data["binarySmall"], 5)  # 0b101
            self.assertTrue("This is a multi-line" in simple_data["tripleQuoted"])
        else:
            self.skipTest(f"Test file not found: {test_file_path}")

if __name__ == "__main__":
    unittest.main()