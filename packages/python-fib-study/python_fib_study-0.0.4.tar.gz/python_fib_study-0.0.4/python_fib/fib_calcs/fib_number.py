
def fib_recurring(number: int) -> int:
    if number < 0:
        raise ValueError("Fibonacci has to be equal or above zero")
    elif number <= 1:
        return number
    else:
        return fib_recurring(number - 1) + fib_recurring(number - 2)
