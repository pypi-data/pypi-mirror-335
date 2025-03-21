# Vrint Package

A Python package that provides a verbose print function.

## Installation

You can install the package using pip:

```bash
pip install vrint
```

## Usage

Import the `vrint` function and the `verbose` variable from the package:

```python
from vrint import vrint, verbose

verbose = False
vrint("This message will not be printed.")

verbose = True
vrint("This message will be printed.")

# You can also use the verbose flag directly in functions:
def hello_world(verbose=True):
    vrint("Hello, world!", verbose=verbose)

hello_world() # This will print
hello_world(verbose=False) # This will not print


## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

This package was created by Huayra1.



