import pytest

from tracking.geospatial import (
    distance_to_polygon,
    point_fully_inside_polygon,
    point_in_polygon,
)


SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]


@pytest.mark.parametrize('point, expected', [((5, 5), True), ((15, 5), False), ((0, 5), False)])
def test_point_in_polygon_handles_inside_outside_and_boundary(point, expected):
    assert point_in_polygon(point[1], point[0], SQUARE) is expected


def test_polygon_helpers_handle_degenerate_polygons():
    assert point_in_polygon(1, 1, [[0, 0], [1, 1]]) is False
    assert distance_to_polygon(1, 1, [[0, 0], [1, 1]]) == float('inf')


def test_point_fully_inside_requires_accuracy_circle_to_fit():
    assert point_fully_inside_polygon(5, 5, 0, SQUARE) is True
    assert point_fully_inside_polygon(5, 5, 100, SQUARE) is True
    assert point_fully_inside_polygon(0.0001, 5, 100, SQUARE) is False
