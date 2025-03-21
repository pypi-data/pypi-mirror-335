# Vrint Package

A Python package that provides a verbose print function.

## Installation

You can install the package using pip:

```bash
pip install vrint
```

## Usage
```
"""
Test script for the simplified vrint module.
This script tests the core features of vrint:
- Basic printing functionality with global state
- Function execution with state syntax (vrint.verbose(func()))
- Decorator syntax (@with_vrint_state with both myfunc(vrint.verbose) and myfunc(vrint_state=vrint.verbose))
"""

import sys
import io
from vrint import vrint, with_vrint_state

# Helper function to capture stdout for verification
def capture_output(func, *args, **kwargs):
    original_stdout = sys.stdout
    try:
        output = io.StringIO()
        sys.stdout = output
        result = func(*args, **kwargs)
        captured = output.getvalue()
        return result, captured
    finally:
        sys.stdout = original_stdout

# Test basic functionality
def test_basic():
    print("\n=== Testing Basic Functionality ===")
    
    # Reset state
    vrint.quiet
    result, output = capture_output(lambda: vrint("This should not print"))
    print(f"With quiet state: {'PASSED' if output == '' else 'FAILED'}")
    
    vrint.verbose
    result, output = capture_output(lambda: vrint("This should print"))
    print(f"With verbose state: {'PASSED' if 'This should print' in output else 'FAILED'}")
    
    # Test per-call state override
    vrint.quiet  # Set global state to quiet
    result, output = capture_output(lambda: vrint("This should print anyway", vrint.verbose))
    print(f"Per-call override (verbose): {'PASSED' if 'This should print anyway' in output else 'FAILED'}")
    
    vrint.verbose  # Set global state to verbose
    result, output = capture_output(lambda: vrint("This should NOT print", vrint.quiet))
    print(f"Per-call override (quiet): {'PASSED' if output == '' else 'FAILED'}")

# Test functions for function execution with state
def simple_function():
    """Basic test function that uses vrint"""
    vrint("Message from simple_function")
    print("Non-vrint message from simple_function")
    return "simple_function result"

@with_vrint_state
def decorated_function():
    """Function with the vrint_state decorator"""
    vrint("Message from decorated_function")
    print("Non-vrint message from decorated_function")
    return "decorated_function result"

# Test function execution with state
def test_function_execution_with_state():
    print("\n=== Testing Function Execution With State ===")
    
    # Test with quiet state
    vrint.verbose  # Make sure global state is verbose
    
    def execute_with_quiet():
        return vrint.quiet(simple_function())
    
    result, output = capture_output(execute_with_quiet)
    print(f"vrint.quiet(func()) syntax: {'PASSED' if 'Message from simple_function' not in output else 'FAILED'}")
    print(f"Non-vrint messages still appear: {'PASSED' if 'Non-vrint message from simple_function' in output else 'FAILED'}")
    print(f"Function return value is preserved: {'PASSED' if result == 'simple_function result' else 'FAILED'}")
    
    # Test with verbose state
    vrint.quiet  # Make sure global state is quiet
    
    def execute_with_verbose():
        return vrint.verbose(simple_function())
    
    result, output = capture_output(execute_with_verbose)
    print(f"vrint.verbose(func()) syntax: {'PASSED' if 'Message from simple_function' in output else 'FAILED'}")
    
    # Test with a function that takes arguments
    def function_with_args(a, b, c=None):
        vrint(f"Args: {a}, {b}, {c}")
        return a + b
    
    # This now uses the normal syntax with arguments in the function call
    vrint.quiet  # Set global state to quiet
    
    def execute_with_args():
        return vrint.verbose(function_with_args(5, 10, c="test"))
    
    result, output = capture_output(execute_with_args)
    print(f"vrint.verbose(func(args)) syntax: {'PASSED' if 'Args: 5, 10, test' in output and result == 15 else 'FAILED'}")

# Test decorator functionality
def test_decorator():
    print("\n=== Testing Decorator Functionality ===")
    
    # Test without vrint_state
    vrint.verbose
    result, output = capture_output(decorated_function)
    print(f"Decorated function (global verbose): {'PASSED' if 'Message from decorated_function' in output else 'FAILED'}")
    
    vrint.quiet
    result, output = capture_output(decorated_function)
    print(f"Decorated function (global quiet): {'PASSED' if 'Message from decorated_function' not in output else 'FAILED'}")
    
    # Test with vrint_state as first argument
    vrint.quiet  # Set global to opposite of what we're testing
    result, output = capture_output(lambda: decorated_function(vrint.verbose))
    print(f"Decorated function with vrint.verbose as first arg: {'PASSED' if 'Message from decorated_function' in output else 'FAILED'}")
    
    vrint.verbose  # Set global to opposite of what we're testing
    result, output = capture_output(lambda: decorated_function(vrint.quiet))
    print(f"Decorated function with vrint.quiet as first arg: {'PASSED' if 'Message from decorated_function' not in output else 'FAILED'}")
    
    # Test with vrint_state as kwarg
    vrint.quiet  # Set global to opposite of what we're testing
    result, output = capture_output(lambda: decorated_function(vrint_state=vrint.verbose))
    print(f"Decorated function with explicit vrint_state=verbose: {'PASSED' if 'Message from decorated_function' in output else 'FAILED'}")
    
    vrint.verbose  # Set global to opposite of what we're testing
    result, output = capture_output(lambda: decorated_function(vrint_state=vrint.quiet))
    print(f"Decorated function with explicit vrint_state=quiet: {'PASSED' if 'Message from decorated_function' not in output else 'FAILED'}")

# Run all tests
def run_all_tests():
    print("\n===== VRINT SIMPLIFIED TEST SUITE =====")
    print(f"Initial verbose state: {'On' if vrint._verbose else 'Off'}")
    
    test_basic()
    test_function_execution_with_state()
    test_decorator()
    
    print("\n===== TEST SUITE COMPLETE =====")
    print(f"Final verbose state: {'On' if vrint._verbose else 'Off'}")

# Example usage demo
def show_example_usage():
    print("\n===== VRINT EXAMPLE USAGE =====")
    print("This section demonstrates how to use vrint in real code scenarios")
    
    # Example function
    def example_function(name):
        vrint(f"Debug: Processing {name}")
        print('if verbose mode is for this function is on, the next line should print "1"')
        vrint(1)
        print(f"Hello, {name}!")
        vrint(f"Debug: Finished processing {name}")
        return f"Processed {name}"
    
    # Example decorated function
    @with_vrint_state
    def decorated_example(name):
        vrint(f"Debug: Starting decorated function for {name}")
        print('if verbose mode is for this function is on, the next line should print "1"')
        vrint(1)
        print(f"Welcome, {name}!")
        vrint(f"Debug: Ending decorated function for {name}")
        return f"Decorated {name}"
    
    print("\n--- Example 1: Basic Usage ---")
    print("Setting global state to verbose")
    vrint.verbose
    print(f"Global verbose state: {'On' if vrint._verbose else 'Off'}")
    example_function("Alice")
    
    print("\n--- Example 2: Per-call Override ---")
    print("Global state is verbose, but this call uses quiet override")
    vrint("This debug message will print")
    vrint("This debug message will NOT print", vrint.quiet)
    
    print("\n--- Example 3: Function Execution With State ---")
    print("Call a function with quiet state regardless of global state")
    vrint.verbose  # Ensure global state is verbose
    print(f"Global verbose state: {'On' if vrint._verbose else 'Off'}")
    print("Calling with vrint.quiet(example_function(...)):")
    result = vrint.quiet(example_function("Bob"))
    print(f"Global state after call: {'On' if vrint._verbose else 'Off'}")  # Should still be On
    print(f"Function still returns a value: {result}")
    
    print("\nCall a function with verbose state regardless of global state")
    vrint.quiet  # Set global state to quiet
    print(f"Global verbose state: {'On' if vrint._verbose else 'Off'}")
    print("Calling with vrint.verbose(example_function(...)):")
    result = vrint.verbose(example_function("Charlie"))
    print(f"Global state after call: {'On' if vrint._verbose else 'Off'}")  # Should still be Off
    print(f"Function still returns a value: {result}")
    
    print("\n--- Example 4: Decorator Usage ---")
    print("Using a decorated function that accepts vrint_state")
    vrint.quiet  # Set global state to quiet
    print(f"Global verbose state: {'On' if vrint._verbose else 'Off'}")
    
    print("\nCall with vrint.verbose as first argument:")
    decorated_example(vrint.verbose, "David")
    print(f"Global state after call: {'On' if vrint._verbose else 'Off'}")  # Should still be Off
    
    print("\nCall with verbose state as named parameter:")
    decorated_example("Emma", vrint_state=vrint.verbose)
    print(f"Global state after call: {'On' if vrint._verbose else 'Off'}")  # Should still be Off
    
    print("\nCall with quiet state to suppress output:")
    vrint.verbose  # Set global to verbose
    print(f"Global verbose state: {'On' if vrint._verbose else 'Off'}")
    decorated_example(vrint.quiet, "Frank")
    print(f"Global state after call: {'On' if vrint._verbose else 'Off'}")  # Should still be On
    
    print("\n===== END OF EXAMPLES =====")

if __name__ == "__main__":
    run_all_tests()
    show_example_usage()
    vrint.verbose
    vrint("This should print")
    vrint.quiet
    vrint("This should not print")
    vrint.verbose
    vrint("This should not print", vrint.quiet)
    vrint.quiet
    vrint("This should print", vrint.verbose)

    # run example output:
    """
    ===== VRINT SIMPLIFIED TEST SUITE =====
    Initial verbose state: Off

    === Testing Basic Functionality ===
    With quiet state: PASSED
    With verbose state: PASSED
    Per-call override (verbose): PASSED
    Per-call override (quiet): PASSED

    === Testing Function Execution With State ===
    vrint.quiet(func()) syntax: PASSED
    Non-vrint messages still appear: PASSED
    Function return value is preserved: PASSED
    vrint.verbose(func()) syntax: PASSED
    vrint.verbose(func(args)) syntax: PASSED

    === Testing Decorator Functionality ===
    Decorated function (global verbose): PASSED
    Decorated function (global quiet): PASSED
    Decorated function with vrint.verbose as first arg: PASSED
    Decorated function with vrint.quiet as first arg: PASSED
    Decorated function with explicit vrint_state=verbose: PASSED
    Decorated function with explicit vrint_state=quiet: PASSED

    ===== TEST SUITE COMPLETE =====
    Final verbose state: Off

    ===== VRINT EXAMPLE USAGE =====
    This section demonstrates how to use vrint in real code scenarios

    --- Example 1: Basic Usage ---
    Setting global state to verbose
    Global verbose state: On
    Debug: Processing Alice
    if verbose mode is for this function is on, the next line should print "1"
    1
    Hello, Alice!
    Debug: Finished processing Alice

    --- Example 2: Per-call Override ---
    Global state is verbose, but this call uses quiet override
    This debug message will print

    --- Example 3: Function Execution With State ---
    Call a function with quiet state regardless of global state
    Global verbose state: On
    Calling with vrint.quiet(example_function(...)):
    if verbose mode is for this function is on, the next line should print "1"
    Hello, Bob!
    Global state after call: Off
    Function still returns a value: Processed Bob

    Call a function with verbose state regardless of global state
    Global verbose state: Off
    Calling with vrint.verbose(example_function(...)):
    Debug: Processing Charlie
    if verbose mode is for this function is on, the next line should print "1"
    1
    Hello, Charlie!
    Debug: Finished processing Charlie
    Global state after call: On
    Function still returns a value: Processed Charlie

    --- Example 4: Decorator Usage ---
    Using a decorated function that accepts vrint_state
    Global verbose state: Off

    Call with vrint.verbose as first argument:
    Debug: Starting decorated function for David
    if verbose mode is for this function is on, the next line should print "1"
    1
    Welcome, David!
    Debug: Ending decorated function for David
    Global state after call: On

    Call with verbose state as named parameter:
    Debug: Starting decorated function for Emma
    if verbose mode is for this function is on, the next line should print "1"
    1
    Welcome, Emma!
    Debug: Ending decorated function for Emma
    Global state after call: On

    Call with quiet state to suppress output:
    Global verbose state: On
    if verbose mode is for this function is on, the next line should print "1"
    Welcome, Frank!
    Global state after call: Off

    ===== END OF EXAMPLES =====
    This should print
    This should print
    ```


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

This package was created by Huayra1.



