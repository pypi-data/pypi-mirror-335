import math
import unittest

from pygeometry2d import XY, Arc, Line

class TestArc(unittest.TestCase):
    def test_length(self):
        center = XY(0.0, 0.0)
        arc = Arc(center, 1.0, 0.0, math.pi / 2)
        self.assertAlmostEqual(arc.length, math.pi / 2)

    def test_discretize(self):
        center = XY(0.0, 0.0)
        arc = Arc(center, 1.0, 0.0, math.pi / 2)
        points = arc.discretize(4)
        self.assertEqual(len(points), 5)
        self.assertEqual(points[0], XY(1.0, 0.0))
        self.assertEqual(points[-1], XY(0.0, 1.0))

    def test_is_point_on_edge(self):
        center = XY(0.0, 0.0)
        arc = Arc(center, 1.0, 0.0, math.pi / 2)
        point_on_edge = XY(1.0, 0.0)
        point_not_on_edge = XY(2.0, 2.0)
        self.assertTrue(arc.is_point_on_edge(point_on_edge))
        self.assertFalse(arc.is_point_on_edge(point_not_on_edge))

    def test_intersection(self):
        center = XY(0.0, 0.0)
        arc = Arc(center, 1.0, 0.0, math.pi / 2)
        line = Line(XY(-1.0, 0.0), XY(1.0, 0.0))
        intersections = arc.intersection(line)
        self.assertEqual(len(intersections), 1)
        self.assertEqual(intersections[0], XY(1.0, 0.0))