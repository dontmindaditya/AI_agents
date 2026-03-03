"""
Utility functions module for input validations and index boundary checks.

This module provides helper functions to validate that input arrays are sorted in ascending order
and to check if given indices are within the valid bounds of array lengths.
These utilities support algorithms that require pre-validated inputs and safe index handling.

Functions:
    - validate_sorted_array(arr: List[int]) -> bool
    - is_index_in_bounds(index: int, arr_length: int) -> bool
"""

from typing import List


def validate_sorted_array(arr: List[int]) -> bool:
    """
    Check if the input array is sorted in ascending order.

    This function iterates through the array to verify each element is less than or equal to
    the next element. Returns True if the entire array is sorted ascendingly, else False.

    Args:
        arr (List[int]): List of integers to check.

    Returns:
        bool: True if `arr` is sorted in non-decreasing order, False otherwise.

    Raises:
        TypeError: If `arr` is not a list of integers.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list of integers.")
    for i, item in enumerate(arr):
        if not isinstance(item, int):
            raise TypeError(f"Element at index {i} is not an integer.")

    # Early return for empty or single-element arrays (always sorted)
    if len(arr) < 2:
        return True

    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            return False
    return True


def is_index_in_bounds(index: int, arr_length: int) -> bool:
    """
    Determine whether the index is within the valid bounds for array access.

    The valid index range is from 0 to arr_length - 1 inclusive.

    Args:
        index (int): Index to check.
        arr_length (int): Length of the array.

    Returns:
        bool: True if index is within bounds [0, arr_length-1], False otherwise.

    Raises:
        TypeError: If `index` or `arr_length` is not an integer.
        ValueError: If `arr_length` is negative.
    """
    if not isinstance(index, int):
        raise TypeError("Index must be an integer.")
    if not isinstance(arr_length, int):
        raise TypeError("Array length must be an integer.")
    if arr_length < 0:
        raise ValueError("Array length cannot be negative.")

    return 0 <= index < arr_length
