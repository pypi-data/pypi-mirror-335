from setuptools import setup, Extension
import os
import sys

# Read the README.md file for the long description
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
    long_description = f.read()

# Check if we're building from the C file directly
USE_CYTHON = False
ext = '.c'

if '--use-cython' in sys.argv:
    USE_CYTHON = True
    sys.argv.remove('--use-cython')
    ext = '.pyx'

# Change this to the pre-generated C file path instead of the pyx file
ext_modules = [Extension("tjson5parser", ["tjson5parser" + ext], language="c")]

# Conditionally use Cython if available and requested
if USE_CYTHON:
    try:
        from Cython.Build import cythonize
        ext_modules = cythonize(ext_modules, language_level=3)
    except ImportError:
        # If Cython is not available, we'll just use the pre-generated C file
        if ext == '.pyx':
            print("Cython not available, using pre-generated C file")
            ext_modules = [Extension("tjson5parser", ["tjson5parser.c"], language="c")]

setup(
    name="tjson5",
    version="0.1.1",
    description="Triple-JSON5 parser for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kristof Mulier",
    author_email="kristof.mulier@example.com",
    url="https://github.com/kristofmulier/triple-json5",
    ext_modules=ext_modules,
    python_requires=">=3.7",
    setup_requires=["setuptools>=18.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)