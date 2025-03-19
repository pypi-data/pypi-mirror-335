from unittest import main, TestCase

from python_fib.fib_calcs.fib_number import fib_recurring


class RecurringFibNumberTest(TestCase):
    def test_zero(self):
        self.assertEqual(0, fib_recurring(0))

    def test_negative(self):
        self.assertEqual(None, fib_recurring(-1))

    def test_one(self):
        self.assertEqual(1, fib_recurring(1))

    def test_two(self):
        self.assertEqual(1, fib_recurring(2))

    def test_twenty(self):
        self.assertEqual(6765, fib_recurring(20))

if __name__ == "__main__":
    main()
