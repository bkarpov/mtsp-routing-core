"""Пространственные объекты"""


from __future__ import annotations

import math
from typing import Iterator


class Point:
    """Точка на плоскости"""

    PRECISION = 6  # Количество знаков после запятой в координатах, расстояниях между точками

    def __init__(self, x: float, y: float) -> None:
        self._x = round(x, self.PRECISION)
        self._y = round(y, self.PRECISION)

    def __eq__(self, other) -> bool:
        return self._x == other.x and self._y == other.y if isinstance(other, Point) else False

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._x}, {self._y})"

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def get_distance_to(self, point: Point) -> float:
        return round(math.sqrt((self._x - point.x) ** 2 + (self._y - point.y) ** 2), self.PRECISION)


class Cluster:
    """Кластер точек"""

    def __init__(self, points: list[Point]) -> None:
        self.points = points

    def __len__(self) -> int:
        return len(self.points)

    def __iter__(self) -> Iterator:
        return iter(self.points)

    def get_geometric_center(self) -> Point:
        """Вычислить геометрический центр кластера"""

        if len(self) == 0:
            raise ValueError("calculating geometric center of empty cluster")
        elif len(self) == 1:
            return self.points[0]

        return Point(
            sum((point.x for point in self.points)) / len(self),
            sum((point.y for point in self.points)) / len(self)
        )


class Segment:
    """Отрезок, соединяющий две точки"""

    def __init__(self, start: Point, finish: Point, length: float):
        self._start = start
        self._finish = finish
        self._length = length

    @property
    def start(self) -> Point:
        return self._start

    @property
    def finish(self) -> Point:
        return self._finish

    @property
    def length(self) -> float:
        """Длина отрезка

        Задается в конструкторе, тк отрезок может представлять ломаную или кривую с длиной > расстояния между точками
        """

        return self._length

    def get_another_border(self, point: Point) -> Point:
        return self._start if point != self._start else self._finish


class Graph:
    """Ориентированный взвешенный граф, представленный списками смежности"""

    def __init__(self) -> None:
        self._adjacency_lists: dict[Point, list[Segment]] = {}

    def __contains__(self, item) -> bool:
        return item in self._adjacency_lists

    @property
    def adjacency_lists(self) -> dict[Point, list[Segment]]:
        return self._adjacency_lists

    def add_edge(self, edge: Segment) -> None:
        for node in edge.start, edge.finish:
            if node not in self._adjacency_lists:
                self._adjacency_lists[node] = []

            self._adjacency_lists[node].append(edge)
