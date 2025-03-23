from __future__ import annotations
import math
from typing import Any
from contextlib import contextmanager

#Tolerância para tratar imprecisões
_geom_fuzz = 0.00001
_geom_precision = 5

def set_precision(decimal_precision: int):
    global _geom_fuzz, _geom_precision

    _geom_precision = decimal_precision
    _geom_fuzz = 0.1**decimal_precision

@contextmanager
def set_temp_precision(decimal_precision: int):
    try:
        old_precision = _geom_precision
        set_precision(decimal_precision)
        yield

    finally:
        set_precision(old_precision)

class XY():
    @staticmethod
    def zero() -> XY:
        return XY(0,0)

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
    
    def __repr__(self) -> str:
        return f"[{round(self.x, _geom_precision)}, {round(self.y, _geom_precision)}]"
    
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
    def x (self) -> float:
        return self._x
    
    @x.setter
    def x (self):
        raise AttributeError('XY does not support attribute assignment')
    
    @property
    def y (self) -> float:
        return self._y
    
    @y.setter
    def y (self):
        raise AttributeError('XY does not support attribute assignment')
        
    @property
    def length (self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    @property
    def angle(self) -> float:
        return GeomUtils.normalize_angle(math.atan2(self.y, self.x))
    
    @staticmethod
    def mid(point1, point2) -> XY:
        return (point1 + point2) / 2
    
    def offset(self, delta_x: float, delta_y: float) -> XY:
        return self + XY(delta_x, delta_y)

    def distance (self, other_point: XY) -> float:
        return math.sqrt((self.x - other_point.x)**2 + (self.y - other_point.y)**2)
    
    def normalize (self) -> XY:
        return self / self.length

    def dot_product(self, v2: XY) -> float:
        return self.x * v2.x + self.y * v2.y

    def perpendicular(self) -> XY:
        return XY(-self.y, self.x)

    def rotate(self, angle: float, center: XY = None) -> XY:
        if not center:
            center = XY.zero()
        relative_point = (self - center)
        x = relative_point.x * math.cos(-angle) + relative_point.y * math.sin(-angle)
        y = -relative_point.x * math.sin(-angle) + relative_point.y * math.cos(-angle)
        return XY(x,y) + center
    
    def copy(self) -> XY:
        return XY(self.x, self.y)


class BoundingBox():
    def __init__(self, min_point: XY, max_point: XY):
        self.min = min_point
        self.max = max_point
        self.size_x, self.size_y = max_point - min_point
        self.vertices = [XY(min_point.x, max_point.y), max_point, XY(max_point.x, min_point.y), min_point]

    def __repr__(self) -> str:
        return f"[{self.min}, {self.max}]"
    
    def to_outline(self) -> Line:
        return Line(self.min, self.max)
    
    @property
    def mid(self) -> XY:
        return XY.mid(self.min, self.max)

class Arc():
    def __init__(self, center: XY, radius: float, start_angle: float, end_angle: float):
            self.center = center
            self.radius = radius
            self.start_angle = start_angle
            self.end_angle = end_angle
   
    def __repr__(self) -> str:
        return f"({self.center}, {self.radius}, {self.start_angle}, {self.end_angle})"

    @property
    def diameter(self) -> float:
        return self.radius * 2 

    @property
    def length(self) -> float:
        return abs(self.end_angle - self.start_angle) * self.radius

    def discretize(self, number_of_segments: int) -> list[XY]:
        segment_angle = (self.end_angle - self.start_angle) / number_of_segments
        
        points = []
        for i in range(number_of_segments+1):
            current_angle = self.start_angle + i * segment_angle
            x = self.center.x + self.radius * math.cos(current_angle)
            y = self.center.y + self.radius * math.sin(current_angle)
            points.append(XY(x,y))
        return points

    def is_point_on_edge(self, point: XY) -> bool:
        if abs(point.distance(self.center) - self.radius) >= _geom_fuzz:
            return False

        angle = GeomUtils.normalize_angle(math.atan2(point.y - self.center.y, point.x - self.center.x))

        return self.start_angle <= angle <= self.end_angle or self.start_angle <= angle + 2*math.pi <= self.end_angle

    def intersection(self, line: Line) -> list[XY]:
        if line.distance(self.center) > self.radius+_geom_fuzz:
            return []

        if abs(line.end.x - line.start.x) <= _geom_fuzz:
            y = math.sqrt(self.radius**2 - (line.start.x - self.center.x)**2) + self.center.y
            return [point for point in [XY(line.start.x, y), XY(line.start.x, -y)] if self.is_point_on_edge(point) and line.is_point_in(point)]  
        
        m, b = line.reduction_equation_coefficients

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
    def __init__(self, center: XY, diameter: float):
        super().__init__(center, diameter/2, 0, math.pi*2)

    def __repr__(self) -> str:
        return f"({self.center}, {self.diameter})"

class Line():
    @staticmethod
    def basis_x() -> Line:
        return Line(0,0,1,0,is_unbound=True)
    
    @staticmethod
    def basis_y() -> Line:
        return Line(0,0,0,1,is_unbound=True)

    def __init__(self, x0: float | XY, y0: float | XY, x1: float = None, y1: float = None, is_unbound: bool = False):
        if x1 != None and y1 != None:
            self.start: XY = XY(x0, y0)
            self.end: XY = XY(x1, y1)
        else:
            self.start: XY = x0
            self.end: XY = y0

        self.is_unbound = is_unbound
    
    def __repr__(self) -> str:
        return f"[{round(self.start.x, _geom_precision)}, {round(self.start.y, _geom_precision)}, {round(self.end.x, _geom_precision)}, {round(self.end.y, _geom_precision)}]"

    @property
    def mid (self) -> XY:
        return XY.mid(self.start, self.end)

    @property
    def length (self) -> float:
        return math.inf if self.is_unbound else ((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)**(1/2)
    
    @property
    def angle(self) -> float:
        return (self.end - self.start).angle
    
    @property
    def inverted_angle(self) -> float:
        return (self.start - self.end).angle
    
    @property
    def is_horizontal(self) -> bool:
        return GeomUtils.is_horizontal(self.angle)
    
    @property
    def is_vertical(self) -> bool:
        return GeomUtils.is_vertical(self.angle)
    
    @property
    def is_ortho(self) -> bool:
        return self.is_horizontal or self.is_vertical

    @property
    def general_equation_coefficients(self) -> tuple[float]:
        a = self.end.y - self.start.y
        b = self.start.x - self.end.x
        c = self.end.x*self.start.y - self.start.x*self.end.y
        return (1, b/a, c/a) if round(a, _geom_precision) != 0 else (a/b, 1, c/b)
    
    @property
    def reduction_equation_coefficients(self) -> tuple:
       angular_coefficient = (self.end.y - self.start.y) / (self.end.x - self.start.x)
       y_intercept = self.start.y - angular_coefficient * self.start.x
       return (angular_coefficient, y_intercept)

    def distance(self, point: XY) -> float:
       return abs((self.end.x - self.start.x) * (self.start.y - point.y) - (self.end.y - self.start.y) * (self.start.x - point.x)) \
              / ((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)**(1/2)
    
    def has_same_direction(self, other: XY | Line | Any) -> bool:
       return GeomUtils.has_same_direction(self.angle, other.angle)

    def is_point_in(self, point: XY) -> bool:
        if self.is_unbound:
            return self.distance(point) <= _geom_fuzz
        crossproduct = (point.y - self.start.y) * (self.end.x - self.start.x) - (point.x - self.start.x) * (self.end.y - self.start.y)

        if abs(crossproduct) > _geom_fuzz:
            return False

        dotproduct = (point.x - self.start.x) * (self.end.x - self.start.x) + (point.y - self.start.y)*(self.end.y - self.start.y)
        return -math.sqrt(_geom_fuzz) < dotproduct <= (self.length**2 + math.sqrt(_geom_fuzz))
    
    def offset(self, offset: float) -> Line:
        offset_vector = (self.end - self.start).normalize().perpendicular() * offset
        return Line(self.start + offset_vector, self.end + offset_vector)

    def intersection(self, other_line: Line, extend_segments_to_infinity = False) -> XY:
        a, b, c = self.general_equation_coefficients 
        d, e, f = other_line.general_equation_coefficients
        
        d1 = math.sqrt(a*a + b*b)
        d2 = math.sqrt(d*d + e*e)
        div = (e*a - d*b)

        if d1 < _geom_fuzz or d2 < _geom_fuzz or abs(div) < _geom_fuzz:
            return None

        x = (f*b -  c*e) / div
        y = (d*c  - f*a) / div

        intersection_point = XY(x, y)
        
        if not extend_segments_to_infinity and (not self.is_point_in(intersection_point) or not other_line.is_point_in(intersection_point)):
            return None

        return intersection_point
    
    def discretize(self, number_of_segments: int) -> list[XY]:
        segment_vector = (self.end - self.start).normalize() * (self.length / number_of_segments)

        return [self.start + segment_vector * i for i in range(number_of_segments+1)]
    
    def to_unbound (self) -> Line:
        return Line(self.start.x, self.start.y, self.end.x, self.end.y, is_unbound=True)
    
    def is_consecutive (self, otherLine: Line) -> bool:
        return self.end.distance(otherLine.start) <= _geom_fuzz
    
    def to_readable_direction (self) -> Line:
        if math.pi/2 + _geom_fuzz < self.angle < 3*math.pi/2 + _geom_fuzz:
            return Line(self.end, self.start, is_unbound=self.is_unbound)
        else:
            return Line(self.start, self.end, is_unbound=self.is_unbound)
        
    def to_points (self) -> list[XY]:
        return [self.start, self.end]
    
    def to_polyline (self) -> Polyline:
        return Polyline([self.start, self.end])
    
    def reversed (self) -> list[XY]:
        return Line(self.end, self.start, is_unbound=self.is_unbound)

    def mirror(self, point: XY) -> XY:
        a, b, c = self.general_equation_coefficients
        temp = -2 * (a * point.x + b * point.y + c) /(a * a + b * b)
        x = temp * a + point.x
        y = temp * b + point.y
        return XY(x, y)
    
    def perpendicular(self) -> Line:
        vector: XY = self.end - self.start
        return Line(XY.zero(), vector.perpendicular())
    
    def is_point_above(self, point: XY) -> bool:
        vector_to_point = point - self.start
        line_vector = self.end - self.start

        return line_vector.x * vector_to_point.y - line_vector.y * vector_to_point.x > 0
    
class Polyline():
    def __init__(self, points: list[XY]):
           self.points: list[XY] = points

    def __getitem__(self, index: int) -> XY:
        return self.points[index]
    
    def __setitem__(self, index: int, item: XY):
        self.points[index] = item

    @property
    def length(self) -> float:
        return sum(seg.length for seg in self.to_segments())
    
    @property
    def is_closed(self) -> bool:
        return self.points[0].distance(self.points[-1]) < _geom_fuzz
    
    @property
    def start(self) -> XY:
        return self.points[0]
    
    @property
    def end(self) -> XY:
        return self.points[-1]
    
    @property
    def num_points(self) -> float:
        return len(self.points)
    
    @property
    def signed_area(self) -> float:
        area_accumulator = 0
        for i in range(self.num_points):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % self.num_points]
            area_accumulator += (p1.x * p2.y - p2.x * p1.y)

        return area_accumulator / 2
    
    @property
    def area(self) -> float:
        return round(abs(self.signed_area), _geom_precision)
    
    @property
    def is_clockwise(self) -> bool:
        return self.signed_area < 0
    
    @property
    def is_counter_clockwise(self) -> bool:
        return self.signed_area > 0
    
    def is_equivalent(self, other: Polyline) -> bool:
        min_point_pl1 = XY(min(point.x for point in self), min(point.y for point in self))
        min_point_pl2 = XY(min(point.x for point in other), min(point.y for point in other))
        pl1 = Polyline([point - min_point_pl1 for point in self])
        pl2 = Polyline([point - min_point_pl2 for point in other])
        return all(pl1.is_point_in_edge(point) for point in pl2) and all(pl2.is_point_in_edge(point) for point in pl1)
    
    def is_scaled_equivalent(self, other: Polyline) -> bool:
        return self.is_equivalent(other.scaled(self.length/other.length))

    def reverse(self) -> Polyline:
        self.points = self.points[::-1]
        return self
    
    def reversed(self) -> Polyline:
        return Polyline(self.points[::-1])

    def close(self) -> Polyline:
        if not self.is_closed:
            self.points.append(XY(self.points[0].x, self.points[0].y))
        return self
    
    def closed(self) -> Polyline:
        if self.is_closed:
            return self.copy()
        return Polyline(self.points + [self.points[0]])
    
    def scaled(self, scale_factor: float, scale_point: XY = None) -> Polyline:
        scale_point = scale_point or XY.zero()
        return Polyline([scale_point + (point - scale_point) * scale_factor for point in self.points])

    def to_segments(self) -> list[Line]:
        return [Line(self.points[i], self.points[i+1]) for i in range(self.num_points-1)]
    
    def to_points (self) -> list[XY]:
        return self.points.copy()
         
    def is_point_in_edge(self, point: XY) -> bool:
        return any(segment.is_point_in(point) for segment in self.to_segments())
    
    def is_point_inside(self, point: XY) -> bool:
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
    
    def join(self, line: Line | Polyline ) -> Polyline:
        if self.start == line.start:
            self.points = line.reversed().to_points()[:-1] + self.to_points()
        elif self.start == line.end:
            self.points = line.to_points()[:-1] + self.to_points()
        elif self.end == line.start:
            self.points = self.to_points()[:-1] + line.to_points()
        elif self.end == line.end:
            self.points = self.to_points()[:-1] + line.reversed().to_points()
        return self
    
    def intersection(self, geometry_object: Line|Polyline|Arc) -> list[XY]:
        if isinstance(geometry_object, (Line, Arc)):
            return list({intersection for segment in self.to_segments() if (intersection := geometry_object.intersection(segment))})
        elif isinstance(geometry_object, Polyline):
            return list({intersection for line in self.to_segments() for other_line in geometry_object.to_segments() if (intersection := line.intersection(other_line))})
        return []

    def copy(self) -> Polyline:
        return Polyline([point.copy() for point in self.points])

    def center(self) -> XY:
        points = self.points if self.num_points == 1 or not self.is_closed else self.points[:-1]
        sum_x = sum(point.x for point in points)
        sum_y = sum(point.y for point in points)
        
        return XY(sum_x, sum_y) / (self.num_points if self.num_points == 1 or not self.is_closed else self.num_points - 1)

    def offset(self, offset: float) -> Polyline:
        offset_points = []
        points = self.points[:-1] if self.is_closed else self.points[:] 
        points = [v for i, v in enumerate(points) if i == 0 or v != points[i-1]]
        num_point = len(points)
        
        for curr in range(num_point):
            current_point: XY = points[curr]
            prev_point: XY = points[(curr + num_point - 1) % num_point]
            next_point: XY = points[(curr + 1) % num_point]

            next_vector = (next_point - current_point).normalize().perpendicular() if (curr != num_point - 1 or self.is_closed) else XY.zero()
            previous_vector = (current_point - prev_point).normalize().perpendicular() if (curr != 0 or self.is_closed) else XY.zero()

            bisector = (next_vector + previous_vector).normalize()

            bislen = offset / math.sqrt((1 + next_vector.x*previous_vector.x + next_vector.y*previous_vector.y)/2) if (curr not in [0, num_point - 1] or self.is_closed) else offset
            
            offset_points.append(points[curr] + bisector * bislen)
        
        if self.is_closed:
            offset_points.append(offset_points[0])
        
        return Polyline(offset_points)
    
    def enclosing_polyline(self, offset: float, end_point_offset: float = None) -> Polyline:
        if self.num_points < 2:
            return None
        
        end_point_offset = 0 if self.is_closed else (offset if end_point_offset is None else end_point_offset)

        pl1 = self.offset(offset)
        pl1[0] = pl1[0] + (pl1[0]-pl1[1]).normalize() * end_point_offset
        pl1[-1] = pl1[-1] + (pl1[-1]-pl1[-2]).normalize() * end_point_offset
        
        pl2 = self.offset(-offset)
        pl2[0] = pl2[0] + (pl2[0]-pl2[1]).normalize() * end_point_offset
        pl2[-1] = pl2[-1] + (pl2[-1]-pl2[-2]).normalize() * end_point_offset

        return Polyline(pl1.points + pl2.points[::-1]).close()
    
    def moved(self, vector: XY) -> Polyline:
        return Polyline([point.offset(vector.x, vector.y) for point in self.points])
    
    def rotated(self, center: XY, angle: float) -> Polyline:
        return Polyline([point.rotate(angle, center) for point in self.points])
    
class Rectangle(Polyline):
    def __init__(self, corner1: XY, corner2: XY):
        x1, y1 = corner1
        x2, y2 = corner2
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        super().__init__([XY(x1, y1), XY(x2, y1), XY(x2, y2), XY(x1, y2), XY(x1, y1)])
        self.min_corner = XY(x1, y1)
        self.max_corner = XY(x2, y2)
    
    @property
    def center(self) -> XY:
        return (self.max_corner + self.min_corner) / 2
    
    def discretize(self, horizontal_partitions: int, vertical_partitions: int) -> list[Rectangle]:
        h_size = (self.max_corner.x - self.min_corner.x) / horizontal_partitions
        v_size = (self.max_corner.y - self.min_corner.y) / vertical_partitions
        x_positions = [self.min_corner.x+i*h_size for i in range(horizontal_partitions+1)]
        y_positions = [self.min_corner.y+i*v_size for i in range(vertical_partitions+1)][::-1]

        return [Rectangle(XY(x, y), XY(x_positions[i+1], y_positions[j+1])) for j, y in enumerate(y_positions[:-1]) for i, x in enumerate(x_positions[:-1])]

class GeomUtils():
    @staticmethod
    def angle_to_vector(angle: float) -> XY:
        x = math.cos(angle)
        y = math.sin(angle)
        return XY(x, y)
    
    @staticmethod
    def has_same_direction(angle1: float, angle2: float) -> bool:
        return round(abs(GeomUtils.normalize_angle(angle1) - GeomUtils.normalize_angle(angle2)), _geom_precision) in [0, round(math.pi, _geom_precision), round(2 * math.pi, _geom_precision)]
    
    @staticmethod
    def normalize_angle(angle):
        return ((angle % (2*math.pi)) + 2*math.pi) % (2*math.pi)
    
    @staticmethod
    def angle_to_nearest_orthogonal_angle(angle):
        return sorted([i - GeomUtils.normalize_angle(angle) for i in [0, 0.5 * math.pi, math.pi, 1.5 * math.pi, 2 * math.pi]], key=abs)[0]

    @staticmethod
    def is_horizontal(angle: float) -> bool:
        return abs(math.sin(angle)) < _geom_fuzz
    
    @staticmethod
    def is_vertical(angle: float) -> bool:
        return abs(math.cos(angle)) < _geom_fuzz
    
    @staticmethod
    def is_ortho(angle: float) -> bool:
        return GeomUtils.is_vertical(angle) or GeomUtils.is_horizontal(angle)
    
    @staticmethod
    def rad_to_deg(angle: float) -> float:
        return angle * 180 / math.pi
    
    @staticmethod
    def deg_to_rad(angle: float) -> float:
        return angle * math.pi / 180 
    
    @staticmethod
    def optimize_segments(segments: list[Line]) -> list[Line]:
        def _optimize_segment(seg: Line, seg_list: list[Line], coefs: tuple[float, float, float]) -> Line:
            if not seg_list:
                return seg
            elif (coefs[1] != 0 and seg.end.x + _geom_fuzz >= seg_list[0].start.x) or (coefs[1] == 0 and seg.end.y + _geom_fuzz >= seg_list[0].start.y):
                end_point = seg_list[0].end
                seg_list.remove(seg_list[0])
                return _optimize_segment(Line(seg.start, end_point), seg_list, coefs)
            return seg
        
        segments = [segment.to_readable_direction() for segment in segments if segment.start != segment.end]
        segment_dict: dict[tuple[float, float, float], list[Line]] = {coeficients: [] for coeficients in {tuple(round(coef, _geom_precision) for coef in segment.general_equation_coefficients) for segment in segments}}
        for segment in segments:
            segment_dict[tuple(round(coef, _geom_precision) for coef in segment.general_equation_coefficients)].append(segment)

        optimized_segments: list[Line] = []
        for coefs, seg_list in segment_dict.items():
            seg_list = sorted(seg_list, key= lambda seg: seg.start.x if coefs[1] != 0 else seg.start.y)
            while seg_list:
                optimized_segments.append(_optimize_segment(seg_list.pop(0), seg_list, coefs))

        return optimized_segments

    @staticmethod
    def join(lines: list[Polyline|Line]) -> list[Polyline]:
        def _find_and_join(pl: Polyline, polyline_dict: dict[XY, list[Polyline]]) -> Polyline:
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
    def boundary(points: list[XY]) -> Polyline:
        sorted_points = sorted(points, key=lambda pt: pt.x)
        p, q = sorted_points[0], sorted_points[-1]
        line = Line(p, q)
        above = [point for point in sorted_points if line.is_point_above(point)]
        below = [point for point in sorted_points if point not in above]
        above.sort(key=lambda pt: pt.x, reverse=True)
        below.sort(key=lambda pt: pt.x)

        return Polyline(below+above).closed()



    @staticmethod
    def get_min_max_point(point_list: list[XY]) -> BoundingBox:
        min_point = XY(min(point.x for point in point_list), min(point.y for point in point_list))
        max_point = XY(max(point.x for point in point_list), max(point.y for point in point_list))
        return BoundingBox(min_point, max_point)
    
    @staticmethod
    def circle_by_3_points(point1: XY, point2: XY, point3: XY) -> tuple:
        mid1 = XY.mid(point1, point2)
        mid2 = XY.mid(point2, point3)
        vector1 = point2 - point1
        vector2 = point3 - point2
        segment1 = Line(mid1, mid1.offset(-vector1.y, vector1.x))
        segment2 = Line(mid2, mid2.offset(-vector2.y, vector2.x))
        center = segment1.intersection(segment2, True)
        return (center, point1.distance(center)) if center else None

    @staticmethod
    def arc_by_3_points(point1: XY, point2: XY, point3: XY) -> tuple:
        center, radius = GeomUtils.circle_by_3_points(point1, point2, point3)
        if math.sin((point3-point1).angle - (point2-point1).angle) < 0:
            point1, point3 = point3, point1
        return (center, radius, (point1 - center).angle, (point3 - center).angle)
