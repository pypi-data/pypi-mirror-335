import tjson5parser

# Sample TJSON5 string with the special features
sample = '''
{
    // This is a comment
    name: "TJSON5 Example",
    description: """
        This is a multi-line
        description using triple quotes
    """,
    numbers: [0xFF, 0b1010],  // Hex and binary literals
    config: {
        "enabled": true,
        "timeout": "30",
    },  // Trailing comma is allowed
}
'''

# Parse the TJSON5 string
data = tjson5parser.parse(sample)

# Print the results
print("Parsed TJSON5 data:")
print(f"Name: {data['name']}")
print(f"Description: {data['description']}")
print(f"Numbers: {data['numbers']}")
print(f"Config: {data['config']}")

# You can also use it to load TJSON5 files
# with open("config.tjson5", "r") as f:
#     config = tjson5parser.load(f)