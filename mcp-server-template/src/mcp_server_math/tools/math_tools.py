def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide two numbers (raises error if dividing by zero)"""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

def dummy_tool() -> str:
    """A dummy tool that returns a static string for testing purposes."""
    return "This is a dummy tool response."
