import unittest

from pygeometry2d import XY, Line

class TestLine(unittest.TestCase):
    def test_length(self):
        line = Line(XY(0.0, 0.0), XY(3.0, 4.0))
        self.assertEqual(line.length, 5.0)

    def test_is_horizontal(self):
        horizontal_line = Line(XY(0.0, 0.0), XY(1.0, 0.0))
        non_horizontal_line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        self.assertTrue(horizontal_line.is_horizontal)
        self.assertFalse(non_horizontal_line.is_horizontal)

    def test_is_vertical(self):
        vertical_line = Line(XY(0.0, 0.0), XY(0.0, 1.0))
        non_vertical_line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        self.assertTrue(vertical_line.is_vertical)
        self.assertFalse(non_vertical_line.is_vertical)

    def test_is_ortho(self):
        horizontal_line = Line(XY(0.0, 0.0), XY(1.0, 0.0))
        vertical_line = Line(XY(0.0, 0.0), XY(0.0, 1.0))
        diagonal_line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        self.assertTrue(horizontal_line.is_ortho)
        self.assertTrue(vertical_line.is_ortho)
        self.assertFalse(diagonal_line.is_ortho)

    def test_general_equation_coefficients(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        a, b, c = line.general_equation_coefficients
        self.assertEqual(a, 1.0)
        self.assertEqual(b, -1.0)
        self.assertEqual(c, 0.0)

    def test_reduced_equation_coefficients(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        m, b = line.reduced_equation_coefficients
        self.assertEqual(m, 1.0)
        self.assertEqual(b, 0.0)

    def test_distance(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 0.0))
        point = XY(0.0, 1.0)
        self.assertEqual(line.distance(point), 1.0)

    def test_has_same_direction(self):
        line1 = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        line2 = Line(XY(0.0, 0.0), XY(2.0, 2.0))
        line3 = Line(XY(0.0, 0.0), XY(-1.0, -1.0))
        line4 = Line(XY(0.0, 0.0), XY(-1.0, 0))
        self.assertTrue(line1.has_same_direction(line2))
        self.assertTrue(line1.has_same_direction(line3))
        self.assertFalse(line1.has_same_direction(line4))

    def test_is_point_in(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        point_on_line = XY(0.5, 0.5)
        point_not_on_line = XY(1.0, 2.0)
        self.assertTrue(line.is_point_in(point_on_line))
        self.assertFalse(line.is_point_in(point_not_on_line))

    def test_offset(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 0.0))
        offset_line = line.offset(1.0)
        self.assertEqual(offset_line.start, XY(0.0, 1.0))
        self.assertEqual(offset_line.end, XY(1.0, 1.0))

    def test_intersection(self):
        line1 = Line(XY(0.0, 0.0), XY(2.0, 2.0))
        line2 = Line(XY(0.0, 2.0), XY(2.0, 0.0))
        intersection = line1.intersection(line2)
        self.assertEqual(intersection, XY(1.0, 1.0))

    def test_discretize(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        points = line.discretize(2)
        self.assertEqual(len(points), 3)
        self.assertEqual(points[0], XY(0.0, 0.0))
        self.assertEqual(points[1], XY(0.5, 0.5))
        self.assertEqual(points[2], XY(1.0, 1.0))

    def test_to_unbound(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        unbound_line = line.to_unbound()
        self.assertTrue(unbound_line.is_unbound)

    def test_is_consecutive(self):
        line1 = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        line2 = Line(XY(1.0, 1.0), XY(2.0, 2.0))
        self.assertTrue(line1.is_consecutive(line2))

    def test_to_readable_direction(self):
        line = Line(XY(1.0, 1.0), XY(0.0, 0.0))
        readable_line = line.to_readable_direction()
        self.assertEqual(readable_line.start, XY(0.0, 0.0))
        self.assertEqual(readable_line.end, XY(1.0, 1.0))

    def test_to_points(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        points = line.to_points()
        self.assertEqual(points, [XY(0.0, 0.0), XY(1.0, 1.0)])

    def test_to_polyline(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        polyline = line.to_polyline()
        self.assertEqual(polyline.points, [XY(0.0, 0.0), XY(1.0, 1.0)])

    def test_mirror(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        point = XY(1.0, 0.0)
        mirrored_point = line.mirror(point)
        self.assertEqual(mirrored_point, XY(0.0, 1.0))

    def test_perpendicular(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        perpendicular_line = line.perpendicular()
        self.assertEqual(perpendicular_line.start, XY(0.0, 0.0))
        self.assertEqual(perpendicular_line.end, XY(-1.0, 1.0))

    def test_is_point_above(self):
        line = Line(XY(0.0, 0.0), XY(1.0, 1.0))
        point_above = XY(0.0, 1.0)
        point_below = XY(1.0, 0.0)
        self.assertTrue(line.is_point_above(point_above))
        self.assertFalse(line.is_point_above(point_below))