import unittest
import math

from pygeometry2d import XY, GeomUtils, Line

class TestGeomUtils(unittest.TestCase):
    def test_angle_to_vector(self):
        angle = math.pi / 4
        vector = GeomUtils.angle_to_vector(angle)
        self.assertAlmostEqual(vector.x, math.sqrt(2) / 2)
        self.assertAlmostEqual(vector.y, math.sqrt(2) / 2)

    def test_has_same_direction(self):
        angle1 = math.pi / 4
        angle2 = math.pi / 4 + 2 * math.pi
        angle3 = math.pi / 2
        angle4 = -math.pi / 2
        angle5 = 2 * math.pi
        angle6 = 0
        self.assertTrue(GeomUtils.has_same_direction(angle1, angle2))
        self.assertFalse(GeomUtils.has_same_direction(angle1, angle3))
        self.assertTrue(GeomUtils.has_same_direction(angle3, angle4))
        self.assertTrue(GeomUtils.has_same_direction(angle5, angle6))

    def test_normalize_angle(self):
        angle = 3 * math.pi
        normalized = GeomUtils.normalize_angle(angle)
        self.assertAlmostEqual(normalized, math.pi)

    def test_angle_to_nearest_orthogonal_angle(self):
        angle1 = math.pi / 6
        nearest_ortho1 = GeomUtils.angle_to_nearest_orthogonal_angle(angle1)
        angle2 = 2*math.pi/3
        nearest_ortho2 = GeomUtils.angle_to_nearest_orthogonal_angle(angle2)

        self.assertAlmostEqual(nearest_ortho1, -math.pi / 6)
        self.assertAlmostEqual(nearest_ortho2, -math.pi / 6)

    def test_is_horizontal(self):
        angle = 0.0
        self.assertTrue(GeomUtils.is_horizontal(angle))

    def test_is_vertical(self):
        angle = math.pi / 2
        self.assertTrue(GeomUtils.is_vertical(angle))

    def test_is_ortho(self):
        angle1 = 0.0
        angle2 = math.pi / 2
        angle3 = math.pi / 4
        self.assertTrue(GeomUtils.is_ortho(angle1))
        self.assertTrue(GeomUtils.is_ortho(angle2))
        self.assertFalse(GeomUtils.is_ortho(angle3))

    def test_rad_to_deg(self):
        angle_rad = math.pi
        angle_deg = GeomUtils.rad_to_deg(angle_rad)
        self.assertEqual(angle_deg, 180.0)

    def test_deg_to_rad(self):
        angle_deg = 180.0
        angle_rad = GeomUtils.deg_to_rad(angle_deg)
        self.assertEqual(angle_rad, math.pi)

    def test_optimize_segments(self):
        segments = [Line(XY(0.0, 0.0), XY(1.0, 0.0)), Line(XY(1.0, 0.0), XY(2.0, 0.0))]
        optimized = GeomUtils.optimize_segments(segments)
        self.assertEqual(len(optimized), 1)
        self.assertEqual(optimized[0].start, XY(0.0, 0.0))
        self.assertEqual(optimized[0].end, XY(2.0, 0.0))

    def test_join(self):
        lines = [Line(XY(0.0, 0.0), XY(1.0, 0.0)), Line(XY(1.0, 0.0), XY(1.0, 1.0))]
        joined = GeomUtils.join(lines)
        self.assertEqual(len(joined), 1)
        self.assertEqual(joined[0].points, [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)])

    def test_get_min_max_point(self):
        points = [XY(0.0, 0.0), XY(1.0, 1.0), XY(2.0, 2.0)]
        bbox = GeomUtils.get_min_max_point(points)
        self.assertEqual(bbox.min, XY(0.0, 0.0))
        self.assertEqual(bbox.max, XY(2.0, 2.0))

    def test_circle_by_3_points(self):
        point1 = XY(0.0, 0.0)
        point2 = XY(1.0, 0.0)
        point3 = XY(0.0, 1.0)
        center, radius = GeomUtils.circle_by_3_points(point1, point2, point3)
        self.assertEqual(center, XY(0.5, 0.5))
        self.assertAlmostEqual(radius, math.sqrt(2) / 2)

    def test_arc_by_3_points(self):
        point1 = XY(1.0, 0.0)
        point2 = XY(0.0, 0.0)
        point3 = XY(0.0, 1.0)
        center, radius, start_angle, end_angle = GeomUtils.arc_by_3_points(point1, point2, point3)
        self.assertEqual(center, XY(0.5, 0.5))
        self.assertAlmostEqual(radius, math.sqrt(2) / 2)
        self.assertAlmostEqual(start_angle, 3 * math.pi / 4)
        self.assertAlmostEqual(end_angle, 7 * math.pi / 4)