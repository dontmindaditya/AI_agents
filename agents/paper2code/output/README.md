```markdown
# Binary Search Implementation

## Overview

This project provides a clean, efficient, and robust implementation of the **binary search** algorithm in Python. It includes supporting utility functions and custom exceptions to ensure proper input validation and error handling. The binary search function operates on sorted lists or arrays, efficiently searching for a given target value with logarithmic time complexity.

Key features:

- Implementation of binary search algorithm supporting generic comparable data types.
- Clear and concise utility modules for input validation.
- Custom exceptions for meaningful error handling.
- Comprehensive unit tests using `pytest`.
- Easy-to-understand API with thorough documentation and examples.

---

## Installation

This project requires Python 3.7 or higher. The only external dependency is `pytest` for testing.

To install dependencies, run:

```bash
pip install -r requirements.txt
```

Alternatively, install `pytest` directly via pip:

```bash
pip install pytest
```

---

## Usage

Import the binary search function from the `binary_search.py` module and call it with a sorted list and a target value to find:

```python
from binary_search import binary_search

# Example sorted list
numbers = [1, 3, 5, 7, 9, 11]

# Search for the value 7
index = binary_search(numbers, 7)

print(f'Target found at index: {index}')
# Output: Target found at index: 3
```

If the target value is not in the list, the function returns `-1`.

```python
index = binary_search(numbers, 4)
print(f'Target found at index: {index}')
# Output: Target found at index: -1
```

---

## API Documentation

### `binary_search(data: list, target: Any) -> int`

Performs a binary search on a sorted list to find the index of the target element.

- **Parameters:**
  - `data` (`list`): A sorted list of elements to search. Must be sorted in ascending order.
  - `target` (`Any`): The element to locate in the list. Must be comparable with the list elements.

- **Returns:**
  - `int`: The index of the target element if found; otherwise, `-1`.

- **Raises:**
  - `InvalidInputError`: If input `data` is not a list or is unsorted.
  - `TypeError`: If elements cannot be compared to the target.

---

## Examples

### Example 1: Searching for an integer in a sorted list

```python
from binary_search import binary_search

# Sorted list of integers
numbers = [2, 4, 6, 8, 10, 12, 14]

target = 10
index = binary_search(numbers, target)

print(f'Found {target} at index {index}')
# Expected output: Found 10 at index 4
```

### Example 2: Searching for a string in a sorted list of strings

```python
from binary_search import binary_search

# Sorted list of strings
words = ["apple", "banana", "cherry", "date", "fig", "grape"]

target_word = "date"
index = binary_search(words, target_word)

print(f'Found "{target_word}" at index {index}')
# Expected output: Found "date" at index 3
```

---

## Performance

- **Time Complexity:** O(log n), where n is the number of elements in the input list. Binary search halves the search space on each iteration.
- **Space Complexity:** O(1), uses constant extra space.
- **Notes:** Input list must be sorted in ascending order to guarantee correct behavior. If the list is not sorted, result is undefined and may raise errors.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch with a descriptive name (`feature/your-feature-name` or `bugfix/issue-description`).
3. Write clear, maintainable code with appropriate type hints and documentation.
4. Add tests if applicable.
5. Submit a pull request describing your changes.

Please ensure tests pass using `pytest` before submitting.

---

## License

MIT License

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

*This README.md provides a comprehensive guide to using, understanding, and contributing to the binary search implementation project.*
```