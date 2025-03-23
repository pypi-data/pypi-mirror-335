# 2D Geometry Library in Python
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/leonardopbatista/pygeometry2d/blob/master/README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](https://github.com/leonardopbatista/pygeometry2d/blob/master/README.pt-br.md)

This is a lightweight and simple library for handling 2D geometries using only Python's native libraries. It allows performing common geometric operations such as distance calculations, intersections, rotations, and other geometric transformations.

## Main Features

- Point manipulation (`XY` class).
- Creation and operations with lines (`Line`).
- Support for arcs (`Arc`) and circles (`Circle`).
- Bounding box generation (`BoundingBox`).
- Handling polylines (`Polyline`) and rectangles (`Rectangle`).
- Geometric utilities such as angle normalization, orthogonality checking, and shape intersections.

## Installation

Install the library via pip:

```sh
pip install pygeometry2d
```

Then, import it into your project:

```python
from pygeometry2d import XY, Line, Circle, Polyline
```

## Usage Examples

### Creating and Manipulating Points

```python
p1 = XY(3, 4)
p2 = XY(6, 8)
distance = p1.distance(p2)
print(distance)  # 5.0
```

### Creating and Manipulating Lines

```python
line = Line(XY(0, 0), XY(3, 4))
print(line.length)  # Line length
```

### Creating a Circle and Checking Intersections

```python
circle = Circle(XY(0, 0), 10)
line = Line(XY(-10, 0), XY(10, 0))
intersections = circle.intersection(line)
print(intersections)  # List of intersection points
```

### Working with Polylines

```python
polyline = Polyline([XY(0, 0), XY(3, 4), XY(6, 0)])
print(polyline.length)  # Total polyline length
```

## Contribution

If you would like to contribute with improvements or suggest new features, feel free to open a PR or create an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

