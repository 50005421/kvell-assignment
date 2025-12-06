from langchain_core.tools import tool

@tool
def add(numbers: list) -> float:
    """for addition of numbers. use this tool"""
    sum = 0
    if len(numbers) == 0:
        return sum
    for number in numbers:
        sum += number

    return sum

@tool
def subtract(a: float, b: float) -> float:
    """for subtraction of two numbers. use this tool"""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """for multiplication of two numbers. use this tool"""
    return a * b

@tool
def divide(a: float, b: float):
    """for division of two numbers. use this tool"""
    if b == 0:
        return "Error: Cannot divide by zero."
    return a / b

@tool
def string_reverse(text: str) -> str:
    """to reverse a string. use this tool"""
    return text[::-1]

@tool
def count_characters(text: str) -> int:
    """to count the number of characters in a string. use this tool"""
    return len(text)

@tool
def uppercase_lowercase(text: str, to_upper: bool = True) -> str:
    """to convert string to uppercase or lowercase. use this tool"""
    if to_upper:
        return text.upper()
    else:
        return text.lower()


CALCULATOR_TOOLS = [add, subtract, multiply, divide]
STRING_TOOLS =[ string_reverse, count_characters, uppercase_lowercase]