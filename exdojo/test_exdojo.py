import unittest

from exdojo import factorial


class TestFactorial(unittest.TestCase):

    def test_factorial_0(self):
        self.assertEqual(factorial(0), 1)

    def test_factorial_1(self):
        self.assertEqual(factorial(1), 1)

    def test_factorial_2(self):
        self.assertEqual(factorial(2), 2)

    def test_factorial_3(self):
        self.assertEqual(factorial(3), 6)

    def test_factorial_4(self):
        self.assertEqual(factorial(4), 24)
