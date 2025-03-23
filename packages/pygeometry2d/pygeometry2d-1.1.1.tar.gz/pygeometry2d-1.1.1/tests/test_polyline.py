import unittest
import math

from pygeometry2d import XY, Polyline

class TestPolyline(unittest.TestCase):
    def test_length(self):
        points = [XY(0.0, 0.0), XY(3.0, 4.0), XY(3.0, 0.0)]
        polyline = Polyline(points)
        self.assertEqual(polyline.length, 9.0)

    def test_is_closed(self):
        points = [XY(0.0, 0.0), XY(1.0, 1.0), XY(0.0, 0.0)]
        polyline = Polyline(points)
        self.assertTrue(polyline.is_closed)

    def test_signed_area(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline = Polyline(points)
        self.assertEqual(polyline.signed_area, 1.0)

    def test_area(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline = Polyline(points)
        self.assertEqual(polyline.area, 1.0)

    def test_is_clockwise(self):
        points_clockwise = [XY(0.0, 0.0), XY(0.0, 1.0), XY(1.0, 1.0), XY(1.0, 0.0)]
        points_counter_clockwise = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline_clockwise = Polyline(points_clockwise)
        polyline_counter_clockwise = Polyline(points_counter_clockwise)
        self.assertTrue(polyline_clockwise.is_clockwise)
        self.assertFalse(polyline_counter_clockwise.is_clockwise)

    def test_is_counter_clockwise(self):
        points_clockwise = [XY(0.0, 0.0), XY(0.0, 1.0), XY(1.0, 1.0), XY(1.0, 0.0)]
        points_counter_clockwise = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline_clockwise = Polyline(points_clockwise)
        polyline_counter_clockwise = Polyline(points_counter_clockwise)
        self.assertFalse(polyline_clockwise.is_counter_clockwise)
        self.assertTrue(polyline_counter_clockwise.is_counter_clockwise)

    def test_is_equivalent(self):
        points1 = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        points2 = [XY(1.0, 1.0), XY(2.0, 1.0), XY(2.0, 2.0), XY(1.0, 2.0)]
        polyline1 = Polyline(points1)
        polyline2 = Polyline(points2)
        self.assertTrue(polyline1.is_equivalent(polyline2))

    def test_is_scaled_equivalent(self):
        points1 = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        points2 = [XY(0.0, 0.0), XY(2.0, 0.0), XY(2.0, 2.0), XY(0.0, 2.0)]
        polyline1 = Polyline(points1)
        polyline2 = Polyline(points2)
        self.assertTrue(polyline1.is_scaled_equivalent(polyline2))

    def test_close(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        polyline.close()
        self.assertTrue(polyline.is_closed)

    def test_closed(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        closed_polyline = polyline.closed()
        self.assertTrue(closed_polyline.is_closed)

    def test_scaled(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        scaled_polyline = polyline.scaled(2.0)
        self.assertEqual(scaled_polyline.points[1], XY(2.0, 0.0))

    def test_to_segments(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        segments = polyline.to_segments()
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].start, XY(0.0, 0.0))
        self.assertEqual(segments[0].end, XY(1.0, 0.0))

    def test_to_points(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        self.assertEqual(polyline.to_points(), points)

    def test_is_point_in_edge(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        point_on_edge = XY(0.5, 0.0)
        point_not_on_edge = XY(0.5, 0.5)
        self.assertTrue(polyline.is_point_in_edge(point_on_edge))
        self.assertFalse(polyline.is_point_in_edge(point_not_on_edge))

    def test_is_point_inside(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline = Polyline(points)
        point_inside = XY(0.5, 0.5)
        point_outside = XY(2.0, 2.0)
        self.assertTrue(polyline.is_point_inside(point_inside))
        self.assertFalse(polyline.is_point_inside(point_outside))

    def test_join(self):
        points1 = [XY(0.0, 0.0), XY(1.0, 0.0)]
        points2 = [XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline1 = Polyline(points1)
        polyline2 = Polyline(points2)
        polyline1.join(polyline2)
        self.assertEqual(polyline1.points, [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)])

    def test_intersection(self):
        points1 = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        points2 = [XY(0.5, -0.5), XY(0.5, 1.5)]
        polyline1 = Polyline(points1)
        polyline2 = Polyline(points2)
        intersections = polyline1.intersection(polyline2)
        self.assertEqual(len(intersections), 1)
        self.assertEqual(intersections[0], XY(0.5, 0.0))

    def test_center(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0), XY(0.0, 1.0)]
        polyline = Polyline(points)
        center = polyline.center()
        self.assertEqual(center, XY(0.5, 0.5))

    def test_offset(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        offset_polyline = polyline.offset(1.0)
        self.assertEqual(len(offset_polyline.points), 3)

    def test_moved(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        moved_polyline = polyline.moved(XY(1.0, 1.0))
        self.assertEqual(moved_polyline.points[0], XY(1.0, 1.0))

    def test_rotated(self):
        points = [XY(0.0, 0.0), XY(1.0, 0.0), XY(1.0, 1.0)]
        polyline = Polyline(points)
        rotated_polyline = polyline.rotated(XY(0.0, 0.0), math.pi / 2)
        self.assertAlmostEqual(rotated_polyline.points[1].x, 0.0)
        self.assertAlmostEqual(rotated_polyline.points[1].y, 1.0)