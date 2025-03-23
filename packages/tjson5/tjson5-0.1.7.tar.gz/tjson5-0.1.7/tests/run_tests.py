#!/usr/bin/env python3
"""
Test runner for tjson5 package
Runs all tests to verify the package functionality
"""
import sys
import os
import subprocess
import unittest
import time

def run_test(test_script, description):
    """Run a test script and return True if it passes"""
    print(f"\n{description}")
    print("=" * len(description))
    
    start_time = time.time()
    try:
        # Add PYTHONIOENCODING=utf-8 to environment to avoid encoding issues
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Run the test script with the specified environment
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True,
            env=env,
            errors='replace'  # Handle any Unicode decoding errors in output
        )
        end_time = time.time()
        
        if result.returncode == 0:
            # Use ASCII symbols for Windows compatibility
            check_mark = "√" if os.name != 'nt' else "PASS"
            print(f"{check_mark} {description} PASSED in {end_time - start_time:.2f}s")
            # Print a brief success message
            output_lines = result.stdout.splitlines()
            if output_lines:
                # Print the last few lines of successful output
                print("\nOutput Summary:")
                for line in output_lines[-min(5, len(output_lines)):]:
                    print(f"  {line}")
            return True
        else:
            # Use ASCII symbols for Windows compatibility
            x_mark = "×" if os.name != 'nt' else "FAIL"
            print(f"{x_mark} {description} FAILED in {end_time - start_time:.2f}s")
            print("\nOutput:")
            print(result.stdout)
            print("\nErrors:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error running {test_script}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("TJSON5 Package Test Runner")
    print("=========================")
    print(f"Running tests from: {os.path.abspath('.')}")
    
    # Get current directory (should be tests/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of tests to run
    tests = [
        (os.path.join(current_dir, "test_01.py"), "Unit Tests"),
        (os.path.join(current_dir, "test_02.py"), "Simple Usage Example"),
        (os.path.join(current_dir, "test_parse_large_file.py"), "Large File Parser Test"),
        (os.path.join(current_dir, "verify_package.py"), "Package Verification")
    ]
    
    # Track results
    results = []
    
    # Run each test
    for test_script, description in tests:
        results.append(run_test(test_script, description))
    
    # Print summary
    print("\nTest Summary")
    print("===========")
    for i, (test_script, description) in enumerate(tests):
        status = "PASS" if results[i] else "FAIL"
        print(f"{status} - {description} ({test_script})")
    
    # Overall result
    if all(results):
        print("\nAll tests PASSED!")
        return 0
    else:
        print(f"\n{results.count(False)} test(s) FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())