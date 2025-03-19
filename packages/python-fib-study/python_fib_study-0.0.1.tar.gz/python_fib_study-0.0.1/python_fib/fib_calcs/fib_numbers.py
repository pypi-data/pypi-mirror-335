from .fib_number import fib_recurring

def calculate_numbers(numbers: list[int]) -> list[int]:
    return [fib_recurring(number=i) for i in numbers]