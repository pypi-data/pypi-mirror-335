# python -m unittest discover tests

import unittest
from lofty.module1 import *

class TestMathFunctions(unittest.TestCase):
    def test_age(self):
        self.assertEqual(Hazel.getage(self), 46.07529089664613)
    
    def test_employment(self):
        self.assertEqual(Hazel.getemploymentstatus(self), True)

if __name__ == '__main__':
    unittest.main()
