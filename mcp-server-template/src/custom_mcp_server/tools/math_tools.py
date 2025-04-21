from custom_mcp_server.tools_registry import tool

@tool
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide two numbers (raises error if dividing by zero)"""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m ** 2)