import math
import unittest

from pygeometry2d import XY

class TestXY(unittest.TestCase):
    def test_length(self):
        point = XY(3.0, 4.0)
        self.assertEqual(point.length, 5.0)

    def test_angle(self):
        point = XY(1.0, 1.0)
        self.assertAlmostEqual(point.angle, math.pi / 4)

    def test_mid(self):
        point1 = XY(1.0, 2.0)
        point2 = XY(3.0, 4.0)
        mid_point = XY.mid(point1, point2)
        self.assertEqual(mid_point, XY(2.0, 3.0))

    def test_offset(self):
        point = XY(1.0, 2.0)
        offset_point = point.offset(1.0, 1.0)
        self.assertEqual(offset_point, XY(2.0, 3.0))

    def test_distance(self):
        point1 = XY(1.0, 2.0)
        point2 = XY(4.0, 6.0)
        self.assertEqual(point1.distance(point2), 5.0)

    def test_normalize(self):
        point = XY(3.0, 4.0)
        normalized = point.normalize()
        self.assertAlmostEqual(normalized.length, 1.0)

    def test_dot_product(self):
        point1 = XY(1.0, 2.0)
        point2 = XY(3.0, 4.0)
        self.assertEqual(point1.dot_product(point2), 11.0)

    def test_perpendicular(self):
        point = XY(1.0, 2.0)
        perpendicular_point = point.perpendicular()
        self.assertEqual(perpendicular_point, XY(-2.0, 1.0))

    def test_rotate(self):
        point = XY(1.0, 0.0)
        rotated_point = point.rotate(math.pi / 2)
        self.assertAlmostEqual(rotated_point.x, 0.0)
        self.assertAlmostEqual(rotated_point.y, 1.0)