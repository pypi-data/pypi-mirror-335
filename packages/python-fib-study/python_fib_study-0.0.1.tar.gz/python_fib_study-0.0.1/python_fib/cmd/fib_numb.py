import argparse

from python_fib.fib_calcs.fib_number import fib_recurring


def fib_numb() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate Fibonacci numbers",
    )
    parser.add_argument(
        "--number",
        action="store",
        type=int,
        required=True,
        help="Fibonacci number to be calculated",
    )
    args = parser.parse_args()
    print(f"You Fibonacci number is {fib_recurring(args.number)}")
