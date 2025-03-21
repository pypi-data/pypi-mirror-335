# classyDict

`classyDict` is a Python package that provides a dictionary with dot notation access, including support for nested dictionaries.

## Features
- Access dictionary keys using dot notation.
- Supports nested dictionaries with dot notation.

## Installation

To install `classyDict`, you can use pip:

```bash
pip install classyDict
```

## Usage

Here's a simple example of how to use `classyDict`:

```python
from classyDict import ClassyDict

# Create a ClassyDict instance
my_dict = ClassyDict({'key1': 'value1', 'key2': {'nestedKey': 'nestedValue'}})

# Access values using dot notation
print(my_dict.key1)  # Output: value1
print(my_dict.key2.nestedKey)  # Output: nestedValue
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Hassan Rasool - [hassanrasool1057@gmail.com](mailto:hassanrasool1057@gmail.com)

## Acknowledgments

- Inspired by the need for a more intuitive way to access dictionary keys in Python. 