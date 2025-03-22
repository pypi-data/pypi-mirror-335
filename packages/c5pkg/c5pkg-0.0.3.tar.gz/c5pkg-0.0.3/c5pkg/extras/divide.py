def divide(a, b):
    """
    Divide two numbers and handle division by zero.

    Parameters:
    a (float): The numerator.
    b (float): The denominator.

    Returns:
    float: The result of the division, or None if division by zero occurs.
    """
    try:
        return a / b
    except ZeroDivisionError:
        print("Error: Division by zero is not allowed.")
        return None