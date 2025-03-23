import unittest

from pygeometry2d import XY, Rectangle

class TestRectangle(unittest.TestCase):
    def test_center(self):
        rect = Rectangle(XY(0.0, 0.0), XY(2.0, 2.0))
        self.assertEqual(rect.center, XY(1.0, 1.0))

    def test_discretize(self):
        rect = Rectangle(XY(0.0, 0.0), XY(2.0, 2.0))
        sub_rects = rect.discretize(2, 2)
        self.assertEqual(len(sub_rects), 4)
        self.assertEqual(sub_rects[0].min_corner, XY(0.0, 1.0))
        self.assertEqual(sub_rects[0].max_corner, XY(1.0, 2.0))
        self.assertEqual(sub_rects[2].min_corner, XY(0.0, 0.0))
        self.assertEqual(sub_rects[2].max_corner, XY(1.0, 1.0))