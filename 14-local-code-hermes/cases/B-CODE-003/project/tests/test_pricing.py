import runpy
import unittest
from pathlib import Path

MODULE = runpy.run_path(Path(__file__).parents[1] / "src" / "pricing.py")
apply_discount = MODULE["apply_discount"]


class PricingTests(unittest.TestCase):
    def test_zero_discount_keeps_total(self) -> None:
        self.assertEqual(apply_discount(1000, 0), 1000)

    def test_quarter_discount(self) -> None:
        self.assertEqual(apply_discount(1000, 25), 750)

    def test_full_discount_is_zero(self) -> None:
        self.assertEqual(apply_discount(1000, 100), 0)


if __name__ == "__main__":
    unittest.main()
