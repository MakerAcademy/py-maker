import math

from src.liquidation_module.abacus import LinearDecrease, ExponentialDecrease, StairstepExponentialDecrease
import unittest


class AbacusTest(unittest.TestCase):
    def test_linear_decrease(self):
        abacus = LinearDecrease(20.0)
        self.assertTrue(abacus.price(100.0, 10.0) == 50.0)
        self.assertTrue(abacus.price(100.0, 20.0) == 0.0)
        self.assertTrue(abacus.price(100.0, 30.0) == 0.0)

    def test_exponential_decrease(self):
        abacus = ExponentialDecrease(0.1)
        self.assertTrue(abacus.price(100.0, 1.0) == 10.0)
        self.assertTrue(math.isclose(abacus.price(100.0, 2.0), 1.0))
        self.assertTrue(math.isclose(abacus.price(100.0, 3.0), 0.1))

    def test_stairstep_exponential_decrease(self):
        abacus = StairstepExponentialDecrease(1.0, 0.1)
        self.assertTrue(abacus.price(100.0, 1.0) == 10.0)
        self.assertTrue(math.isclose(abacus.price(100.0, 2.0), 1.0))
        self.assertTrue(math.isclose(abacus.price(100.0, 3.0), 0.1))


if __name__ == '__main__':
    print("Testing...")
    unittest.main()
    print("All tests passed.")
