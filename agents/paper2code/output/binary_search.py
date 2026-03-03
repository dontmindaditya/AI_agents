"""
Module: binary_search.py
Path: src/algorithms/binary_search.py

This module provides a robust, iterative implementation of the binary search algorithm
for searching a target value within a sorted list of integers.

The binary_search function returns the index of the target value if found;
otherwise, it returns -1.

No external dependencies are required.

Example:
    >>> binary_search([1, 3, 5, 7, 9], 5)
    2
    >>> binary_search([1, 3, 5, 7, 9], 2)
    -1
"""

from typing import List


def binary_search(arr: List[int], target: int) -> int:
    """
    Perform an iterative binary search to find the target in a sorted list of integers.

    Args:
        arr (List[int]): A list of integers sorted in ascending order.
        target (int): The integer value to search for in `arr`.

    Returns:
        int: The index of the `target` in `arr` if found; otherwise, -1.

    Raises:
        TypeError: If `arr` is not a list of integers or `target` is not an integer.
        ValueError: If `arr` is empty or not sorted in ascending order.

    Notes:
        - The function assumes that `arr` is sorted in ascending order.
        - If multiple occurrences of `target` exist, the function returns the index of any one occurrence.

    Time Complexity:
        O(log n), where n is the number of elements in `arr`.

    Space Complexity:
        O(1), iterative implementation.
    """
    # Input validation
    if not isinstance(arr, list):
        raise TypeError("The 'arr' argument must be of type List[int].")
    if not all(isinstance(x, int) for x in arr):
        raise TypeError("All elements in 'arr' must be integers.")
    if not isinstance(target, int):
        raise TypeError("The 'target' argument must be an integer.")
    if len(arr) == 0:
        raise ValueError("Input array 'arr' must not be empty.")
    if any(arr[i] > arr[i + 1] for i in range(len(arr) - 1)):
        raise ValueError("Input array 'arr' must be sorted in ascending order.")

    low: int = 0
    high: int = len(arr) - 1

    while low <= high:
        # Use floor division to avoid float indices
        mid: int = low + (high - low) // 2
        mid_value = arr[mid]

        if mid_value == target:
            return mid
        elif mid_value < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


if __name__ == "__main__":
    # Basic usage examples
    test_arrays = [
        ([1, 2, 3, 4, 5], 3),
        ([10, 20, 30, 40, 50], 35),
        ([1], 1),
        ([2, 4, 6, 8, 10], 10),
        ([2, 4, 6, 8, 10], 1),
    ]

    for arr, tgt in test_arrays:
        try:
            result = binary_search(arr, tgt)
            print(f"binary_search({arr}, {tgt}) = {result}")
        except Exception as e:
            print(f"Error: {e}")
