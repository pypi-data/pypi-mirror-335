import unittest
from mathutils.geometry import distance, cercle_surface

class TestGeometry(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(distance(1, 2, 2, 4), 5.0)
        self.assertEqual(distance(0, 0, 3, 4), 5.0)
        
    def test_cercle_surface(self):
        self.assertEqual(cercle_surface(10), 3.14159 * 22)    
        self.assertEqual(cercle_surface(10), 3.14159 * 100)
        
if __name__== '__main__':
    unittest.main()        