"""Тесты генетического алгоритма, решающего TSP"""


import random

from routing import spatial_objects as sp
from routing.algorithms import genetic_algorithm as ga


def test_genetic_algorithm() -> None:
    points = [  # Выпуклая оболочка
        sp.Point(1, 3), sp.Point(2, 2), sp.Point(3, 1), sp.Point(5, 1),
        sp.Point(6, 2), sp.Point(7, 3), sp.Point(7, 5), sp.Point(6, 6),
        sp.Point(5, 7), sp.Point(3, 7), sp.Point(2, 6), sp.Point(1, 5),
    ]  # Вершины идут в порядке обхода

    result = ga.genetic_algorithm_for_tsp(random.sample(points, len(points)), 2)

    point_idx = points.index(result[0])  # Индекс первой вершины ответа в исходном списке точек
    forward_direction = result[-1] == points[point_idx - 1]

    for point_from_result in result:
        if point_idx >= len(points):
            point_idx = 0
        elif point_idx < 0:
            point_idx = len(points) - 1

        assert point_from_result == points[point_idx]

        point_idx += 1 if forward_direction else -1
