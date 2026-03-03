"""
Example code with various issues and optimization opportunities.
This file is used for testing the Debug Optimization Agent.
"""


def inefficient_search(data, target):
    """Search for target in data (inefficient implementation)."""
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == target:
                return i
    return -1


def string_concatenation_loop(items):
    """Concatenate strings inefficiently."""
    result = ""
    for item in items:
        result += str(item) + ", "
    return result


def mutable_default_argument(item, my_list=[]):
    """Dangerous mutable default argument."""
    my_list.append(item)
    return my_list


def deep_nesting(data):
    """Deeply nested conditional logic."""
    for item in data:
        if item > 0:
            if item % 2 == 0:
                if item < 100:
                    if item > 10:
                        print(f"Found: {item}")


def bare_except_example():
    """Using bare except clause."""
    try:
        x = 1 / 0
    except:
        pass


def long_parameter_list(a, b, c, d, e, f, g, h):
    """Function with too many parameters."""
    return a + b + c + d + e + f + g + h


class GodClass:
    """Class with too many methods."""
    
    def method1(self):
        pass
    
    def method2(self):
        pass
    
    def method3(self):
        pass
    
    def method4(self):
        pass
    
    def method5(self):
        pass
    
    def method6(self):
        pass
    
    def method7(self):
        pass
    
    def method8(self):
        pass
    
    def method9(self):
        pass
    
    def method10(self):
        pass
    
    def method11(self):
        pass
    
    def method12(self):
        pass
    
    def method13(self):
        pass
    
    def method14(self):
        pass
    
    def method15(self):
        pass
    
    def method16(self):
        pass


def list_membership_test(items, search_list):
    """Inefficient list membership testing."""
    results = []
    for item in items:
        if item in search_list:  # O(n) for each check
            results.append(item)
    return results


def repeated_computation(n):
    """Repeated expensive computation."""
    result = 0
    for i in range(n):
        result += len(str(i)) + len(str(i)) + len(str(i))
    return result


# Magic numbers
def calculate_area(radius):
    return 3.14159 * radius * radius


# Missing type hints
def process_data(data):
    return [x * 2 for x in data if x > 0]


# Unused variable
def unused_variable_example():
    x = 42
    y = 100
    return y


if __name__ == "__main__":
    # Test code
    data = list(range(1000))
    result = inefficient_search(data, 500)
    print(f"Result: {result}")