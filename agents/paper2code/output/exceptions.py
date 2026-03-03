"""
Exceptions module for binary search operations.

This module defines custom exception classes related to binary search,
such as invalid input errors. These exceptions help clearly communicate
specific problems encountered during binary search operations, improving
error handling and debugging.

No external dependencies.
"""


class BinarySearchError(Exception):
    """
    Base class for exceptions raised by binary search operations.

    This serves as a common ancestor for all binary search-related exceptions,
    allowing for broad exception handling where needed.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the BinarySearchError exception with a message.

        Args:
            message (str): Description of the exception.
        """
        super().__init__(message)


class InvalidInputError(BinarySearchError):
    """
    Exception raised when binary search receives invalid input.

    This can include cases such as:
    - Input array is empty
    - Input array is not sorted
    - Indices provided (low, high) are out of bounds or invalid
    """

    def __init__(
        self, message: str = "Invalid input provided to binary search."
    ) -> None:
        """
        Initialize the InvalidInputError exception with a default or custom message.

        Args:
            message (str, optional): Description of the invalid input error.
                Defaults to a generic invalid input message.
        """
        super().__init__(message)


class ElementNotFoundError(BinarySearchError):
    """
    Exception raised when the target element is not found in the search array.

    Using this exception allows distinguishing a search that completes
    without locating the target from other failures.
    """

    def __init__(self, target: int, message: str = "") -> None:
        """
        Initialize the ElementNotFoundError with the target element and an optional message.

        Args:
            target (int): The element that was not found.
            message (str, optional): Additional description of the error.
                If not provided, a default message including the target will be used.
        """
        if not message:
            message = f"Element {target} not found in the array."
        super().__init__(message)
        self.target = target
