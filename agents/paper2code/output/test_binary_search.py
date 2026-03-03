import pytest
from src.algorithms.binary_search import binary_search

def test_binary_search_basic_found():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 5) == 2
    # Since duplicates are allowed, check any valid index for target 3
    arr_with_duplicates = [1, 3, 3, 3, 5]
    result = binary_search(arr_with_duplicates, 3)
    assert result in [1, 2, 3]

def test_binary_search_basic_not_found():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 2) == -1
    assert binary_search(arr, 10) == -1
    assert binary_search(arr, 0) == -1

def test_binary_search_target_smaller_than_smallest():
    arr = [10, 20, 30, 40]
    assert binary_search(arr, 5) == -1

def test_binary_search_target_larger_than_largest():
    arr = [10, 20, 30, 40]
    assert binary_search(arr, 50) == -1

def test_binary_search_target_at_index_zero():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 1) == 0

def test_binary_search_target_at_last_index():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 9) == len(arr) - 1

def test_binary_search_empty_array_raises_value_error():
    with pytest.raises(ValueError):
        binary_search([], 1)

def test_binary_search_arr_not_list_raises_type_error():
    with pytest.raises(TypeError):
        binary_search("not a list", 1)
    with pytest.raises(TypeError):
        binary_search(123, 1)
    with pytest.raises(TypeError):
        binary_search(None, 1)

def test_binary_search_arr_contains_non_integer_raises_type_error():
    with pytest.raises(TypeError):
        binary_search([1, 2, "three", 4], 3)
    with pytest.raises(TypeError):
        binary_search([1, 2, 3.5, 4], 3)
    with pytest.raises(TypeError):
        binary_search([1, 2, None, 4], 3)

def test_binary_search_target_not_integer_raises_type_error():
    arr = [1, 2, 3, 4]
    with pytest.raises(TypeError):
        binary_search(arr, "3")
    with pytest.raises(TypeError):
        binary_search(arr, 3.5)
    with pytest.raises(TypeError):
        binary_search(arr, None)

def test_binary_search_single_element_array_found():
    arr = [10]
    assert binary_search(arr, 10) == 0

def test_binary_search_single_element_array_not_found():
    arr = [10]
    assert binary_search(arr, 5) == -1

def test_binary_search_large_array():
    arr = list(range(0, 1000000, 2))  # Even numbers from 0 to 999998
    target = 654321
    # target is an odd number and not in list, expect -1
    assert binary_search(arr, target) == -1
    target = 654320
    # target is in list, index should be target // 2
    assert binary_search(arr, target) == target // 2

def test_binary_search_duplicates_returns_valid_index():
    arr = [1, 2, 2, 2, 3, 4]
    result = binary_search(arr, 2)
    assert result in [1, 2, 3]