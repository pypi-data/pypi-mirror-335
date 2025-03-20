"""isoddeven
=====
A Python package to check if a number is odd or even.
"""

def isodd(n: int) -> bool:
    """Return true if the number is odd.

    Check if a number is odd. It returns true if the number is odd and false if the number is even.

    Parameters
    ----------
    n : int
        The number to check.

    Returns
    -------
    bool
        True if `n` is odd, False otherwise.

    Raises
    ------
    TypeError
        If `n` is not an integer.

    Examples
    --------
    >>> isoddeven.isodd(3)
    True
    >>> isoddeven.isodd(4)
    False
    """

    try:
        return n % 2 != 0
    except TypeError:
        print("Expected an integer value.")

def iseven(n: int) -> bool:
    """Return true if the number is even.

    Check if a number is even. It returns true if the number is even and false if the number is odd.

    Parameters
    ----------
    n : int
        The number to check.

    Returns
    -------
    bool
        True if `n` is even, False otherwise.

    Raises
    ------
    TypeError
        If `n` is not an integer.

    Examples
    --------
    >>> isoddeven.iseven(2)
    True
    >>> isoddeven.iseven(5)
    False
    """

    try:
        return n % 2 == 0
    except TypeError:
        print("Expected an integer value.")

def state(n: int) -> str:
    """Check whether the number is odd or even.
    
    Return "odd" if the number is odd and "even" if the number is even.

    Parameters
    ----------
    n : int
        The number to check.

    Returns
    -------
    str
        "odd" if `n` is odd, "even" if `n` is even.

    Raises
    ------
    TypeError
        If `n` is not an integer.

    Examples
    --------
    >>> isoddeven.state(2)
    even
    >>> isoddeven.state(3)
    odd
    """

    try:
        if isodd(n):
            return "odd"
        elif iseven(n):
            return "even"
    except TypeError:
        print("Expected an integer value.")

if __name__ == "__main__":
    # This code will only execute when the module is run as a standalone script.
    print("Executing module as a standalone script")
    number = int(input("Enter a number: "))
    print(f"{number} is ", state(number))
