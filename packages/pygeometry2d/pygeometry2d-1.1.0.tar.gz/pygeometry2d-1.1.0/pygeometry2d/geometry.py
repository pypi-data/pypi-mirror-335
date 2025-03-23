from __future__ import annotations
import math
from typing import Any, List, Tuple, Optional, Union, Generator, Dict
from contextlib import contextmanager

# Tolerance for handling floating-point inaccuracies
_geom_fuzz = 0.00001
_geom_precision = 5

def set_precision(decimal_precision: int) -> None:
    """Sets the global decimal precision for geometric calculations.

    Args:
        decimal_precision (int): The number of decimal places for precision.
    """
    global _geom_fuzz, _geom_precision

    _geom_precision = decimal_precision
    _geom_fuzz = 0.1**decimal_precision

@contextmanager
def set_temp_precision(decimal_precision: int) -> Generator[None, None, None]:
    """Temporarily sets the global precision within a context.

    Args:
        decimal_precision (int): The number of decimal places to use within the context.

    Yields:
        None: Restores the previous precision after execution.
    """
    try:
        old_precision = _geom_precision
        set_precision(decimal_precision)
        yield

    finally:
        set_precision(old_precision)

class XY:
    """A class representing a 2D point or 2D vector with x and y coordinates."""

    @staticmethod
    def zero() -> XY:
        return XY(0, 0)

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    def __repr__(self) -> str:
        return f"({round(self.x, _geom_precision)}, {round(self.y, _geom_precision)})"

    def __add__(self, other_point: XY) -> XY:
        return XY(self.x + other_point.x, self.y + other_point.y)

    def __sub__(self, other_point: XY) -> XY:
        return XY(self.x - other_point.x, self.y - other_point.y)

    def __mul__(self, multiplier: float) -> XY:
        return XY(self.x * multiplier, self.y * multiplier)

    def __rmul__(self, multiplier: float) -> XY:
        return XY(self.x * multiplier, self.y * multiplier)

    def __truediv__(self, divisor: float) -> XY:
        return XY(self.x / divisor, self.y / divisor)

    def __eq__(self, other_point: XY) -> bool:
        return abs(self.x - other_point.x) <= _geom_fuzz and abs(self.y - other_point.y) <= _geom_fuzz

    def __hash__(self) -> int:
        return hash((round(self.x, _geom_precision), round(self.y, _geom_precision)))

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError('list index out of range')

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        #Prevents modification of the x-coordinate.
        raise AttributeError('XY does not support attribute assignment')

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        #Prevents modification of the y-coordinate.
        raise AttributeError('XY does not support attribute assignment')

    @property
    def length(self) -> float:
        """Returns the Euclidean length of the point vector.

        Returns:
            float: The length of the vector.
        """
        return math.sqrt(self.x**2 + self.y**2)

    @property
    def angle(self) -> float:
        """Returns the normalized angle of the point vector in radians.

        Returns:
            float: The angle in radians.
        """
        return GeomUtils.normalize_angle(math.atan2(self.y, self.x))

    @staticmethod
    def mid(point1: XY, point2: XY) -> XY:
        """Returns the midpoint between two points.

        Args:
            point1 (XY): The first point.
            point2 (XY): The second point.

        Returns:
            XY: The midpoint between the two points.
        """
        return (point1 + point2) / 2

    def offset(self, delta_x: float, delta_y: float) -> XY:
        """Returns a new point offset by the given deltas.

        Args:
            delta_x (float): The x offset.
            delta_y (float): The y offset.

        Returns:
            XY: The offset point.
        """
        return self + XY(delta_x, delta_y)

    def distance(self, other_point: XY) -> float:
        """Returns the Euclidean distance between two points.

        Args:
            other_point (XY): The other point.

        Returns:
            float: The distance between the points.
        """
        return math.sqrt((self.x - other_point.x)**2 + (self.y - other_point.y)**2)

    def normalize(self) -> XY:
        """Returns a normalized version of the point vector.

        Returns:
            XY: The normalized vector.
        """
        return self / self.length

    def dot_product(self, v2: XY) -> float:
        """Returns the dot product of two vectors.

        Args:
            v2 (XY): The other vector.

        Returns:
            float: The dot product.
        """
        return self.x * v2.x + self.y * v2.y

    def perpendicular(self) -> XY:
        """Returns a perpendicular vector.

        Returns:
            XY: The perpendicular vector.
        """
        return XY(-self.y, self.x)

    def rotate(self, angle: float, center: Optional[XY] = None) -> XY:
        """Rotates the point around a center by a given angle.

        Args:
            angle (float): The angle in radians.
            center (Optional[XY]): The center of rotation. Defaults to the origin.

        Returns:
            XY: The rotated point.
        """
        if not center:
            center = XY.zero()
        relative_point = (self - center)
        x = relative_point.x * math.cos(-angle) + relative_point.y * math.sin(-angle)
        y = -relative_point.x * math.sin(-angle) + relative_point.y * math.cos(-angle)
        return XY(x, y) + center


class BoundingBox:
    """A class representing a 2D bounding box defined by two corner points."""

    def __init__(self, min_point: XY, max_point: XY):
        self.min = min_point
        self.max = max_point
        self.size_x, self.size_y = max_point - min_point
        self.vertices = [XY(min_point.x, max_point.y), max_point, XY(max_point.x, min_point.y), min_point]

    def __repr__(self) -> str:
        return f"BoundingBox({self.min}, {self.max})"

    def to_outline(self) -> Line:
        """Converts the bounding box to a line representing its outline.

        Returns:
            Line: The outline of the bounding box.
        """
        return Line(self.min, self.max)

    @property
    def mid(self) -> XY:
        """Returns the midpoint of the bounding box.

        Returns:
            XY: The midpoint.
        """
        return XY.mid(self.min, self.max)


class Arc:
    """A class representing a 2D arc defined by a center, radius, and angles."""

    def __init__(self, center: XY, radius: float, start_angle: float, end_angle: float):
        self.center = center
        self.radius = radius
        self.start_angle = start_angle #radians
        self.end_angle = end_angle #radians

    def __repr__(self) -> str:
        return f"Arc({self.center}, {self.radius}, {self.start_angle}, {self.end_angle})"

    @property
    def diameter(self) -> float:
        return self.radius * 2

    @property
    def length(self) -> float:
        return abs(self.end_angle - self.start_angle) * self.radius

    def discretize(self, number_of_segments: int) -> List[XY]:
        """Discretizes the arc into a list of points.

        Args:
            number_of_segments (int): The number of segments to divide the arc into.

        Returns:
            List[XY]: The list of points representing the arc.
        """
        segment_angle = (self.end_angle - self.start_angle) / number_of_segments

        points = []
        for i in range(number_of_segments + 1):
            current_angle = self.start_angle + i * segment_angle
            x = self.center.x + self.radius * math.cos(current_angle)
            y = self.center.y + self.radius * math.sin(current_angle)
            points.append(XY(x, y))
        return points

    def is_point_on_edge(self, point: XY) -> bool:
        """Checks if a point lies on the edge of the arc.

        Args:
            point (XY): The point to check.

        Returns:
            bool: True if the point is on the edge, False otherwise.
        """
        if abs(point.distance(self.center) - self.radius) >= _geom_fuzz:
            return False

        angle = GeomUtils.normalize_angle(math.atan2(point.y - self.center.y, point.x - self.center.x))

        return self.start_angle <= angle <= self.end_angle or self.start_angle <= angle + 2 * math.pi <= self.end_angle

    def intersection(self, line: Line) -> List[XY]:
        """Finds the intersection points between the arc and a line.

        Args:
            line (Line): The line to intersect with.

        Returns:
            List[XY]: The list of intersection points.
        """
        if line.distance(self.center) > self.radius + _geom_fuzz:
            return []

        if abs(line.end.x - line.start.x) <= _geom_fuzz:
            y = math.sqrt(self.radius**2 - (line.start.x - self.center.x)**2) + self.center.y
            return [point for point in [XY(line.start.x, y), XY(line.start.x, -y)] if self.is_point_on_edge(point) and line.is_point_in(point)]

        m, b = line.reduced_equation_coefficients

        A = 1 + m**2
        B = 2 * (m * b - m * self.center.y - self.center.x)
        C = self.center.y**2 - self.radius**2 + self.center.x**2 - 2 * b * self.center.y + b**2

        discriminant = B**2 - 4 * A * C

        if discriminant < 0:
            return []

        elif discriminant == 0:
            x = -B / (2 * A)
            y = m * x + b
            point = XY(x, y)
            return [point] if self.is_point_on_edge(point) and line.is_point_in(point) else []

        elif discriminant > 0:
            x1 = (-B + math.sqrt(discriminant)) / (2 * A)
            y1 = m * x1 + b
            x2 = (-B - math.sqrt(discriminant)) / (2 * A)
            y2 = m * x2 + b
            return [point for point in [XY(x1, y1), XY(x2, y2)] if self.is_point_on_edge(point) and line.is_point_in(point)]


class Circle(Arc):
    """A class representing a 2D circle, which is a special case of an arc."""

    def __init__(self, center: XY, diameter: float):
        super().__init__(center, diameter / 2, 0, math.pi * 2)

    def __repr__(self) -> str:
        return f"Circle({self.center}, {self.diameter})"


class Line:
    """A class representing a 2D line segment or an infinite line."""

    @staticmethod
    def basis_x() -> Line:
        """Returns the x-axis as a line.

        Returns:
            Line: The x-axis line.
        """
        return Line(0, 0, 1, 0, is_unbound=True)

    @staticmethod
    def basis_y() -> Line:
        """Returns the y-axis as a line.

        Returns:
            Line: The y-axis line.
        """
        return Line(0, 0, 0, 1, is_unbound=True)

    def __init__(self, x0: Union[float, XY], y0: Union[float, XY], x1: Optional[float] = None, y1: Optional[float] = None, is_unbound: bool = False):
        """Initializes the line.

        Args:
            x0 (Union[float, XY]): The x-coordinate of the start point or the start point itself.
            y0 (Union[float, XY]): The y-coordinate of the start point or the end point if x0 is a point.
            x1 (Optional[float]): The x-coordinate of the end point. Required if x0 and y0 are floats.
            y1 (Optional[float]): The y-coordinate of the end point. Required if x0 and y0 are floats.
            is_unbound (bool): Whether the line is infinite. Defaults to False.
        """
        if x1 is not None and y1 is not None:
            self.start: XY = XY(x0, y0)
            self.end: XY = XY(x1, y1)
        else:
            self.start: XY = x0
            self.end: XY = y0

        self.is_unbound = is_unbound

    def __repr__(self) -> str:
        return f"Line({self.start}, {self.end})"

    @property
    def mid(self) -> XY:
        """Returns the midpoint of the line.

        Returns:
            XY: The midpoint.
        """
        return XY.mid(self.start, self.end)

    @property
    def length(self) -> float:
        """Returns the length of the line.

        Returns:
            float: The length of the line.
        """
        return math.inf if self.is_unbound else ((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)**(1 / 2)

    @property
    def angle(self) -> float:
        """Returns the normalized angle of the line in radians.

        Returns:
            float: The angle in radians.
        """
        return (self.end - self.start).angle

    @property
    def inverted_angle(self) -> float:
        """Returns the inverted angle of the line in radians.

        Returns:
            float: The inverted angle in radians.
        """
        return (self.start - self.end).angle

    @property
    def is_horizontal(self) -> bool:
        """Checks if the line is horizontal.

        Returns:
            bool: True if the line is horizontal, False otherwise.
        """
        return GeomUtils.is_horizontal(self.angle)

    @property
    def is_vertical(self) -> bool:
        """Checks if the line is vertical.

        Returns:
            bool: True if the line is vertical, False otherwise.
        """
        return GeomUtils.is_vertical(self.angle)

    @property
    def is_ortho(self) -> bool:
        """Checks if the line is either horizontal or vertical.

        Returns:
            bool: True if the line is horizontal or vertical, False otherwise.
        """
        return self.is_horizontal or self.is_vertical

    @property
    def general_equation_coefficients(self) -> Tuple[float, float, float]:
        """Returns the coefficients of the general equation of the line (Ax + By + C = 0).

        Returns:
            Tuple[float, float, float]: The coefficients (A, B, C).
        """
        a = self.end.y - self.start.y
        b = self.start.x - self.end.x
        c = self.end.x * self.start.y - self.start.x * self.end.y
        return (1, b / a, c / a) if round(a, _geom_precision) != 0 else (a / b, 1, c / b)

    @property
    def reduced_equation_coefficients(self) -> Tuple[float, float]:
        """Returns the coefficients of the reduced equation of the line (y = mx + b).

        Returns:
            Tuple[float, float]: The coefficients (m, b).
        """
        angular_coefficient = (self.end.y - self.start.y) / (self.end.x - self.start.x)
        y_intercept = self.start.y - angular_coefficient * self.start.x
        return (angular_coefficient, y_intercept)

    def distance(self, point: XY) -> float:
        """Returns the shortest distance from the point to the line.

        Args:
            point (XY): The point to measure the distance from.

        Returns:
            float: The distance from the point to the line.
        """
        return abs((self.end.x - self.start.x) * (self.start.y - point.y) - (self.end.y - self.start.y) * (self.start.x - point.x)) \
            / ((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)**(1 / 2)

    def has_same_direction(self, other: Union[XY, Line, Any]) -> bool:
        """Checks if the line has the same direction as another line or vector.

        Args:
            other (Union[XY, Line, Any]): The other line or vector.

        Returns:
            bool: True if the directions are the same, False otherwise.
        """
        return GeomUtils.has_same_direction(self.angle, other.angle)

    def is_point_in(self, point: XY) -> bool:
        """Checks if a point lies on the line segment.

        Args:
            point (XY): The point to check.

        Returns:
            bool: True if the point is on the line segment, False otherwise.
        """
        if self.is_unbound:
            return self.distance(point) <= _geom_fuzz
        crossproduct = (point.y - self.start.y) * (self.end.x - self.start.x) - (point.x - self.start.x) * (self.end.y - self.start.y)

        if abs(crossproduct) > _geom_fuzz:
            return False

        dotproduct = (point.x - self.start.x) * (self.end.x - self.start.x) + (point.y - self.start.y) * (self.end.y - self.start.y)
        return -math.sqrt(_geom_fuzz) < dotproduct <= (self.length**2 + math.sqrt(_geom_fuzz))

    def offset(self, offset: float) -> Line:
        """Returns a new line offset by a given distance.

        Args:
            offset (float): The distance to offset the line.

        Returns:
            Line: The offset line.
        """
        offset_vector = (self.end - self.start).normalize().perpendicular() * offset
        return Line(self.start + offset_vector, self.end + offset_vector)

    def intersection(self, other_line: Line, extend_segments_to_infinity: bool = False) -> Optional[XY]:
        """Finds the intersection point between two lines.

        Args:
            other_line (Line): The other line to intersect with.
            extend_segments_to_infinity (bool): Whether to treat the lines as infinite. Defaults to False.

        Returns:
            Optional[XY]: The intersection point, or None if no intersection exists.
        """
        a, b, c = self.general_equation_coefficients
        d, e, f = other_line.general_equation_coefficients

        d1 = math.sqrt(a * a + b * b)
        d2 = math.sqrt(d * d + e * e)
        div = (e * a - d * b)

        if d1 < _geom_fuzz or d2 < _geom_fuzz or abs(div) < _geom_fuzz:
            return None

        x = (f * b - c * e) / div
        y = (d * c - f * a) / div

        intersection_point = XY(x, y)

        if not extend_segments_to_infinity and (not self.is_point_in(intersection_point) or not other_line.is_point_in(intersection_point)):
            return None

        return intersection_point

    def discretize(self, number_of_segments: int) -> List[XY]:
        """Discretizes the line into a list of points.

        Args:
            number_of_segments (int): The number of segments to divide the line into.

        Returns:
            List[XY]: The list of points representing the line.
        """
        segment_vector = (self.end - self.start).normalize() * (self.length / number_of_segments)

        return [self.start + segment_vector * i for i in range(number_of_segments + 1)]

    def to_unbound(self) -> Line:
        """Converts the line segment to an infinite line.

        Returns:
            Line: The infinite line.
        """
        return Line(self.start.x, self.start.y, self.end.x, self.end.y, is_unbound=True)

    def is_consecutive(self, other_line: Line) -> bool:
        """Checks if the end of this line is the start of another line.

        Args:
            other_line (Line): The other line to check.

        Returns:
            bool: True if the lines are consecutive, False otherwise.
        """
        return self.end.distance(other_line.start) <= _geom_fuzz

    def to_readable_direction(self) -> Line:
        """Returns a line with a consistent direction for readability.

        Returns:
            Line: The line with a consistent direction.
        """
        if math.pi / 2 + _geom_fuzz < self.angle < 3 * math.pi / 2 + _geom_fuzz:
            return Line(self.end, self.start, is_unbound=self.is_unbound)
        else:
            return Line(self.start, self.end, is_unbound=self.is_unbound)

    def to_points(self) -> List[XY]:
        """Returns the start and end points of the line.

        Returns:
            List[XY]: The start and end points.
        """
        return [self.start, self.end]

    def to_polyline(self) -> Polyline:
        """Converts the line to a polyline.

        Returns:
            Polyline: The polyline representation of the line.
        """
        return Polyline([self.start, self.end])

    def reversed(self) -> Line:
        """Returns a reversed version of the line.

        Returns:
            Line: The reversed line.
        """
        return Line(self.end, self.start, is_unbound=self.is_unbound)

    def mirror(self, point: XY) -> XY:
        """Returns the mirror image of a point across the line.

        Args:
            point (XY): The point to mirror.

        Returns:
            XY: The mirrored point.
        """
        a, b, c = self.general_equation_coefficients
        temp = -2 * (a * point.x + b * point.y + c) / (a * a + b * b)
        x = temp * a + point.x
        y = temp * b + point.y
        return XY(x, y)

    def perpendicular(self) -> Line:
        """Returns a perpendicular line at the origin.

        Returns:
            Line: The perpendicular line.
        """
        vector: XY = self.end - self.start
        return Line(XY.zero(), vector.perpendicular())

    def is_point_above(self, point: XY) -> bool:
        """Checks if a point is above the line.

        Args:
            point (XY): The point to check.

        Returns:
            bool: True if the point is above the line, False otherwise.
        """
        vector_to_point = point - self.start
        line_vector = self.end - self.start

        return line_vector.x * vector_to_point.y - line_vector.y * vector_to_point.x > 0


class Polyline:
    """A class representing a polyline, which is a sequence of connected line segments."""

    def __init__(self, points: List[XY]):
        self.points: List[XY] = points

    def __repr__(self) -> str:
        return f"Polyline({self.points})"

    def __getitem__(self, index: int) -> XY:
        return self.points[index]

    def __setitem__(self, index: int, item: XY):
        self.points[index] = item

    @property
    def length(self) -> float:
        """Returns the total length of the polyline.

        Returns:
            float: The total length.
        """
        return sum(seg.length for seg in self.to_segments())

    @property
    def is_closed(self) -> bool:
        """Checks if the polyline is closed.

        Returns:
            bool: True if the polyline is closed, False otherwise.
        """
        return self.points[0].distance(self.points[-1]) < _geom_fuzz

    @property
    def start(self) -> XY:
        """Returns the start point of the polyline.

        Returns:
            XY: The start point.
        """
        return self.points[0]

    @property
    def end(self) -> XY:
        """Returns the end point of the polyline.

        Returns:
            XY: The end point.
        """
        return self.points[-1]

    @property
    def num_points(self) -> int:
        """Returns the number of points in the polyline.

        Returns:
            int: The number of points.
        """
        return len(self.points)

    @property
    def signed_area(self) -> float:
        """Returns the signed area of the polyline.

        Returns:
            float: The signed area.
        """
        area_accumulator = 0
        for i in range(self.num_points):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % self.num_points]
            area_accumulator += (p1.x * p2.y - p2.x * p1.y)

        return area_accumulator / 2

    @property
    def area(self) -> float:
        """Returns the absolute area of the polyline.

        Returns:
            float: The absolute area.
        """
        return round(abs(self.signed_area), _geom_precision)

    @property
    def is_clockwise(self) -> bool:
        """Checks if the polyline is oriented clockwise.

        Returns:
            bool: True if clockwise, False otherwise.
        """
        return self.signed_area < 0

    @property
    def is_counter_clockwise(self) -> bool:
        """Checks if the polyline is oriented counter-clockwise.

        Returns:
            bool: True if counter-clockwise, False otherwise.
        """
        return self.signed_area > 0

    def is_equivalent(self, other: Polyline) -> bool:
        """Checks if two polylines are equivalent.

        Args:
            other (Polyline): The other polyline to compare.

        Returns:
            bool: True if the polylines are equivalent, False otherwise.
        """
        min_point_pl1 = XY(min(point.x for point in self), min(point.y for point in self))
        min_point_pl2 = XY(min(point.x for point in other), min(point.y for point in other))
        pl1 = Polyline([point - min_point_pl1 for point in self])
        pl2 = Polyline([point - min_point_pl2 for point in other])
        return all(pl1.is_point_in_edge(point) for point in pl2) and all(pl2.is_point_in_edge(point) for point in pl1)

    def is_scaled_equivalent(self, other: Polyline) -> bool:
        """Checks if two polylines are equivalent after scaling.

        Args:
            other (Polyline): The other polyline to compare.

        Returns:
            bool: True if the polylines are scaled equivalents, False otherwise.
        """
        return self.is_equivalent(other.scaled(self.length / other.length))

    def reverse(self) -> Polyline:
        """Reverses the order of points in the polyline.

        Returns:
            Polyline: The reversed polyline.
        """
        self.points = self.points[::-1]
        return self

    def reversed(self) -> Polyline:
        """Returns a reversed copy of the polyline.

        Returns:
            Polyline: The reversed polyline.
        """
        return Polyline(self.points[::-1])

    def close(self) -> Polyline:
        """Closes the polyline by adding the first point at the end if it's not closed yet.

        Returns:
            Polyline: The closed polyline.
        """
        if not self.is_closed:
            self.points.append(XY(self.points[0].x, self.points[0].y))
        return self

    def closed(self) -> Polyline:
        """Returns a closed copy of the polyline.

        Returns:
            Polyline: The closed polyline.
        """
        if self.is_closed:
            return self.copy()
        return Polyline(self.points + [self.points[0]])

    def scaled(self, scale_factor: float, scale_point: Optional[XY] = None) -> Polyline:
        """Returns a scaled copy of the polyline by a given factor.

        Args:
            scale_factor (float): The scaling factor.
            scale_point (Optional[XY]): The point to scale around. Defaults to the origin.

        Returns:
            Polyline: The scaled polyline.
        """
        scale_point = scale_point or XY.zero()
        return Polyline([scale_point + (point - scale_point) * scale_factor for point in self.points])

    def to_segments(self) -> List[Line]:
        """Converts the polyline to a list of line segments.

        Returns:
            List[Line]: The list of line segments.
        """
        return [Line(self.points[i], self.points[i + 1]) for i in range(self.num_points - 1)]

    def to_points(self) -> List[XY]:
        """Returns a copy of the points in the polyline.

        Returns:
            List[XY]: The list of points.
        """
        return self.points.copy()

    def is_point_in_edge(self, point: XY) -> bool:
        """Checks if a point lies on any edge of the polyline.

        Args:
            point (XY): The point to check.

        Returns:
            bool: True if the point is on an edge, False otherwise.
        """
        return any(segment.is_point_in(point) for segment in self.to_segments())

    def is_point_inside(self, point: XY) -> bool:
        """Checks if a point lies inside or lies on any edge of the polyline.

        Args:
            point (XY): The point to check.

        Returns:
            bool: True if the point is inside, False otherwise.
        """
        if self.is_point_in_edge(point):
            return True
        points = self.points[::-1] if self.is_clockwise else self.points
        inside = False
        p1x, p1y = points[0]
        for i in range(1, self.num_points + 1):
            p2x, p2y = points[i % self.num_points]
            if point.y > min(p1y, p2y) and point.y <= max(p1y, p2y) and point.x <= max(p1x, p2x):
                if p1y != p2y:
                    xints = (point.y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or point.x <= xints:
                    inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def join(self, line: Union[Line, Polyline]) -> Polyline:
        """Joins the polyline with another line or polyline. If the ends do not match, return the polyline without modification.

        Args:
            line (Union[Line, Polyline]): The line or polyline to join with.

        Returns:
            Polyline: The joined polyline.
        """
        if self.start == line.start:
            self.points = line.reversed().to_points()[:-1] + self.to_points()
        elif self.start == line.end:
            self.points = line.to_points()[:-1] + self.to_points()
        elif self.end == line.start:
            self.points = self.to_points()[:-1] + line.to_points()
        elif self.end == line.end:
            self.points = self.to_points()[:-1] + line.reversed().to_points()
        return self

    def intersection(self, geometry_object: Union[Line, Polyline, Arc]) -> List[XY]:
        """Finds the intersection points between the polyline and another geometry object.

        Args:
            geometry_object (Union[Line, Polyline, Arc]): The geometry object to intersect with.

        Returns:
            List[XY]: The list of intersection points.
        """
        if isinstance(geometry_object, (Line, Arc)):
            return list({intersection for segment in self.to_segments() if (intersection := geometry_object.intersection(segment))})
        elif isinstance(geometry_object, Polyline):
            return list({intersection for line in self.to_segments() for other_line in geometry_object.to_segments() if (intersection := line.intersection(other_line))})
        return []

    def copy(self) -> Polyline:
        """Returns a copy of the polyline.

        Returns:
            Polyline: A copy of the polyline.
        """
        return Polyline(self.points.copy())

    def center(self) -> XY:
        """Returns the centroid of the polyline.

        Returns:
            XY: The centroid.
        """
        points = self.points if self.num_points == 1 or not self.is_closed else self.points[:-1]
        sum_x = sum(point.x for point in points)
        sum_y = sum(point.y for point in points)

        return XY(sum_x, sum_y) / (self.num_points if self.num_points == 1 or not self.is_closed else self.num_points - 1)

    def offset(self, offset: float) -> Polyline:
        """Returns a new polyline offset by a given distance.

        Args:
            offset (float): The distance to offset.

        Returns:
            Polyline: The offset polyline.
        """
        offset_points = []
        points = self.points[:-1] if self.is_closed else self.points[:]
        points = [v for i, v in enumerate(points) if i == 0 or v != points[i - 1]]
        num_point = len(points)

        for curr in range(num_point):
            current_point: XY = points[curr]
            prev_point: XY = points[(curr + num_point - 1) % num_point]
            next_point: XY = points[(curr + 1) % num_point]

            next_vector = (next_point - current_point).normalize().perpendicular() if (curr != num_point - 1 or self.is_closed) else XY.zero()
            previous_vector = (current_point - prev_point).normalize().perpendicular() if (curr != 0 or self.is_closed) else XY.zero()

            bisector = (next_vector + previous_vector).normalize()

            bislen = offset / math.sqrt((1 + next_vector.x * previous_vector.x + next_vector.y * previous_vector.y) / 2) if (curr not in [0, num_point - 1] or self.is_closed) else offset

            offset_points.append(points[curr] + bisector * bislen)

        if self.is_closed:
            offset_points.append(offset_points[0])

        return Polyline(offset_points)

    def enclosing_polyline(self, offset: float, end_point_offset: Optional[float] = None) -> Optional[Polyline]:
        """Returns a polyline that encloses the original polyline with a given offset.

        Args:
            offset (float): The offset distance.
            end_point_offset (Optional[float]): The offset for the end points. Defaults to the main offset.

        Returns:
            Optional[Polyline]: The enclosing polyline, or None if the polyline has fewer than 2 points.
        """
        if self.num_points < 2:
            return None

        end_point_offset = 0 if self.is_closed else (offset if end_point_offset is None else end_point_offset)

        pl1 = self.offset(offset)
        pl1[0] = pl1[0] + (pl1[0] - pl1[1]).normalize() * end_point_offset
        pl1[-1] = pl1[-1] + (pl1[-1] - pl1[-2]).normalize() * end_point_offset

        pl2 = self.offset(-offset)
        pl2[0] = pl2[0] + (pl2[0] - pl2[1]).normalize() * end_point_offset
        pl2[-1] = pl2[-1] + (pl2[-1] - pl2[-2]).normalize() * end_point_offset

        return Polyline(pl1.points + pl2.points[::-1]).close()

    def moved(self, vector: XY) -> Polyline:
        """Returns a copy of the moved polyline by a given vector.

        Args:
            vector (XY): The vector to move by.

        Returns:
            Polyline: The moved polyline.
        """
        return Polyline([point.offset(vector.x, vector.y) for point in self.points])

    def rotated(self, center: XY, angle: float) -> Polyline:
        """Returns a copy of the rotated polyline around a center by a given angle.

        Args:
            center (XY): The center of rotation.
            angle (float): The angle in radians.

        Returns:
            Polyline: The rotated polyline.
        """
        return Polyline([point.rotate(angle, center) for point in self.points])


class Rectangle(Polyline):
    """A class representing a rectangle, which is a special case of a polyline."""

    def __init__(self, corner1: XY, corner2: XY):
        x1, y1 = corner1
        x2, y2 = corner2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        super().__init__([XY(x1, y1), XY(x2, y1), XY(x2, y2), XY(x1, y2), XY(x1, y1)])
        self.min_corner = XY(x1, y1)
        self.max_corner = XY(x2, y2)

    def __repr__(self) -> str:
        return f"Rectangle({self.min_corner}, {self.max_corner})"

    @property
    def center(self) -> XY:
        return (self.max_corner + self.min_corner) / 2

    def discretize(self, horizontal_partitions: int, vertical_partitions: int) -> List[Rectangle]:
        """Discretizes the rectangle into smaller rectangles.

        Args:
            horizontal_partitions (int): The number of horizontal partitions.
            vertical_partitions (int): The number of vertical partitions.

        Returns:
            List[Rectangle]: The list of smaller rectangles.
        """
        h_size = (self.max_corner.x - self.min_corner.x) / horizontal_partitions
        v_size = (self.max_corner.y - self.min_corner.y) / vertical_partitions
        x_positions = [self.min_corner.x + i * h_size for i in range(horizontal_partitions + 1)]
        y_positions = [self.min_corner.y + i * v_size for i in range(vertical_partitions + 1)][::-1]

        return [Rectangle(XY(x, y), XY(x_positions[i + 1], y_positions[j + 1])) for j, y in enumerate(y_positions[:-1]) for i, x in enumerate(x_positions[:-1])]


class GeomUtils:
    """A utility class for geometric operations."""

    @staticmethod
    def angle_to_vector(angle: float) -> XY:
        """Converts an angle to a unit vector.

        Args:
            angle (float): The angle in radians.

        Returns:
            XY: The unit vector.
        """
        x = math.cos(angle)
        y = math.sin(angle)
        return XY(x, y)

    @staticmethod
    def has_same_direction(angle1: float, angle2: float) -> bool:
        """Checks if two angles have the same direction.

        Args:
            angle1 (float): The first angle in radians.
            angle2 (float): The second angle in radians.

        Returns:
            bool: True if the angles have the same direction, False otherwise.
        """
        return round(abs(GeomUtils.normalize_angle(angle1) - GeomUtils.normalize_angle(angle2)), _geom_precision) in [0, round(math.pi, _geom_precision), round(2 * math.pi, _geom_precision)]

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normalizes an angle to the range [0, 2π).

        Args:
            angle (float): The angle in radians.

        Returns:
            float: The normalized angle.
        """
        return ((angle % (2 * math.pi)) + 2 * math.pi) % (2 * math.pi)

    @staticmethod
    def angle_to_nearest_orthogonal_angle(angle: float) -> float:
        """Finds the nearest orthogonal angle to a given angle.

        Args:
            angle (float): The angle in radians.

        Returns:
            float: The nearest orthogonal angle.
        """
        return sorted([i - GeomUtils.normalize_angle(angle) for i in [0, 0.5 * math.pi, math.pi, 1.5 * math.pi, 2 * math.pi]], key=abs)[0]

    @staticmethod
    def is_horizontal(angle: float) -> bool:
        """Checks if an angle is horizontal.

        Args:
            angle (float): The angle in radians.

        Returns:
            bool: True if the angle is horizontal, False otherwise.
        """
        return abs(math.sin(angle)) < _geom_fuzz

    @staticmethod
    def is_vertical(angle: float) -> bool:
        """Checks if an angle is vertical.

        Args:
            angle (float): The angle in radians.

        Returns:
            bool: True if the angle is vertical, False otherwise.
        """
        return abs(math.cos(angle)) < _geom_fuzz

    @staticmethod
    def is_ortho(angle: float) -> bool:
        """Checks if an angle is either horizontal or vertical.

        Args:
            angle (float): The angle in radians.

        Returns:
            bool: True if the angle is horizontal or vertical, False otherwise.
        """
        return GeomUtils.is_vertical(angle) or GeomUtils.is_horizontal(angle)

    @staticmethod
    def rad_to_deg(angle: float) -> float:
        """Converts an angle from radians to degrees.

        Args:
            angle (float): The angle in radians.

        Returns:
            float: The angle in degrees.
        """
        return angle * 180 / math.pi

    @staticmethod
    def deg_to_rad(angle: float) -> float:
        """Converts an angle from degrees to radians.

        Args:
            angle (float): The angle in degrees.

        Returns:
            float: The angle in radians.
        """
        return angle * math.pi / 180

    @staticmethod
    def optimize_segments(segments: List[Line]) -> List[Line]:
        """Optimizes a list of line segments by merging consecutive segments.

        Args:
            segments (List[Line]): The list of line segments.

        Returns:
            List[Line]: The optimized list of line segments.
        """
        def _optimize_segment(seg: Line, seg_list: List[Line], coefs: Tuple[float, float, float]) -> Line:
            if not seg_list:
                return seg
            elif (coefs[1] != 0 and seg.end.x + _geom_fuzz >= seg_list[0].start.x) or (coefs[1] == 0 and seg.end.y + _geom_fuzz >= seg_list[0].start.y):
                end_point = seg_list[0].end
                seg_list.remove(seg_list[0])
                return _optimize_segment(Line(seg.start, end_point), seg_list, coefs)
            return seg

        segments = [segment.to_readable_direction() for segment in segments if segment.start != segment.end]
        segment_dict: Dict[Tuple[float, float, float], List[Line]] = {coeficients: [] for coeficients in {tuple(round(coef, _geom_precision) for coef in segment.general_equation_coefficients) for segment in segments}}
        for segment in segments:
            segment_dict[tuple(round(coef, _geom_precision) for coef in segment.general_equation_coefficients)].append(segment)

        optimized_segments: List[Line] = []
        for coefs, seg_list in segment_dict.items():
            seg_list = sorted(seg_list, key=lambda seg: seg.start.x if coefs[1] != 0 else seg.start.y)
            while seg_list:
                optimized_segments.append(_optimize_segment(seg_list.pop(0), seg_list, coefs))

        return optimized_segments

    @staticmethod
    def join(lines: List[Union[Polyline, Line]]) -> List[Polyline]:
        """Joins a list of polylines and lines into a list of connected polylines.

        Args:
            lines (List[Union[Polyline, Line]]): The list of polylines and lines.

        Returns:
            List[Polyline]: The list of connected polylines.
        """
        def _find_and_join(pl: Polyline, polyline_dict: Dict[XY, List[Polyline]]) -> Polyline:
            if (match_polyline := polyline_dict.get(pl.start)) or (match_polyline := polyline_dict.get(pl.end)):
                match_polyline = match_polyline[0]
                pl.join(match_polyline)
                polyline_dict[match_polyline.start].remove(match_polyline)
                polyline_dict[match_polyline.end].remove(match_polyline)
                if not polyline_dict[match_polyline.start]:
                    del polyline_dict[match_polyline.start]
                if not polyline_dict[match_polyline.end]:
                    del polyline_dict[match_polyline.end]
                return _find_and_join(pl, polyline_dict)
            return pl

        polylines = [(pl if isinstance(pl, Polyline) else pl.to_polyline()) for pl in lines if pl.start != pl.end]
        unique_points = {pt for pl in polylines for pt in (pl.start, pl.end)}
        polyline_dict = {point: [] for point in unique_points}

        for pl in polylines:
            polyline_dict[pl.start].append(pl)
            polyline_dict[pl.end].append(pl)

        joined_polylines = []
        while polyline_dict:
            pl = polyline_dict[next(iter(polyline_dict))][0]
            polyline_dict[pl.start].remove(pl)
            polyline_dict[pl.end].remove(pl)
            if not polyline_dict[pl.start]:
                del polyline_dict[pl.start]
            if not polyline_dict[pl.end]:
                del polyline_dict[pl.end]
            joined_polylines.append(_find_and_join(pl, polyline_dict))

        return joined_polylines

    @staticmethod
    def boundary(points: List[XY]) -> Polyline:
        """Computes the convex hull of a set of points.

        Args:
            points (List[XY]): The list of points.

        Returns:
            Polyline: The convex hull as a polyline.
        """
        sorted_points = sorted(points, key=lambda pt: pt.x)
        p, q = sorted_points[0], sorted_points[-1]
        line = Line(p, q)
        above = [point for point in sorted_points if line.is_point_above(point)]
        below = [point for point in sorted_points if point not in above]
        above.sort(key=lambda pt: pt.x, reverse=True)
        below.sort(key=lambda pt: pt.x)

        return Polyline(below + above).closed()

    @staticmethod
    def get_min_max_point(point_list: List[XY]) -> BoundingBox:
        """Computes the bounding box of a list of points.

        Args:
            point_list (List[XY]): The list of points.

        Returns:
            BoundingBox: The bounding box.
        """
        min_point = XY(min(point.x for point in point_list), min(point.y for point in point_list))
        max_point = XY(max(point.x for point in point_list), max(point.y for point in point_list))
        return BoundingBox(min_point, max_point)

    @staticmethod
    def circle_by_3_points(point1: XY, point2: XY, point3: XY) -> Optional[Tuple[XY, float]]:
        """Computes the circle passing through three points.

        Args:
            point1 (XY): The first point.
            point2 (XY): The second point.
            point3 (XY): The third point.

        Returns:
            Optional[Tuple[XY, float]]: The center and radius of the circle, or None if the points are collinear.
        """
        mid1 = XY.mid(point1, point2)
        mid2 = XY.mid(point2, point3)
        vector1 = point2 - point1
        vector2 = point3 - point2
        segment1 = Line(mid1, mid1.offset(-vector1.y, vector1.x))
        segment2 = Line(mid2, mid2.offset(-vector2.y, vector2.x))
        center = segment1.intersection(segment2, True)
        return (center, point1.distance(center)) if center else None

    @staticmethod
    def arc_by_3_points(point1: XY, point2: XY, point3: XY) -> Optional[Tuple[XY, float, float, float]]:
        """Computes the arc passing through three points. The points must be in order.

        Args:
            point1 (XY): The first point.
            point2 (XY): The second point.
            point3 (XY): The third point.

        Returns:
            Optional[Tuple[XY, float, float, float]]: The center, radius, start angle, and end angle of the arc, or None if the points are collinear.
        """
        center, radius = GeomUtils.circle_by_3_points(point1, point2, point3)
        if math.sin((point3 - point1).angle - (point2 - point1).angle) < 0:
            point1, point3 = point3, point1
        return (center, radius, (point1 - center).angle, (point3 - center).angle)
    