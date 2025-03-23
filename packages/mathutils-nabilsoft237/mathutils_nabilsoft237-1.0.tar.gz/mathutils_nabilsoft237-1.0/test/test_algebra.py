import unittest 
from mathutils.algebra import resourdre_equation, determinant

class TestAlgebra(unittest.TestCase):
    def test_resourdre_equation(self):
        self.assertEqual(resourdre_equation(1, 2, 1), -1.0)
        
    def test_determinant(self):
        self.assertEqual(determinant([[1, 2], [3, 4]]), -2.0)
        self.assertEqual(determinant([[1, 0], [0, 1]]), 1.0)
        
if __name__== '__main__':
    unittest.main()         
            
            