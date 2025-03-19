from typing import Optional

def fib_recurring(number: int) -> Optional[int]:
    if number < 0:
        return None
    elif number <= 1:
        return number
    else:
        return fib_recurring(number - 1) + fib_recurring(number - 2)
