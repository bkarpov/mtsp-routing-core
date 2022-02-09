"""Пространственные объекты"""


from __future__ import annotations

import math

from routing import _exceptions as ex
from routing import _limits

PRECISION = 6  # Количество знаков после запятой в координатах, расстояниях между точками


class Point:
    """Точка на плоскости"""

    def __init__(self, x: float, y: float) -> None:
        self._x = round(x, PRECISION)
        self._y = round(y, PRECISION)

    def __eq__(self, other) -> bool:
        return self._x == other.x and self._y == other.y

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._x}, {self._y})"

    def __lt__(self, other) -> bool:
        if other == self:
            return False

        return self._x <= other.x and self._y <= other.y  # Или меньше сразу обе координаты, или 1 равна, а 2-ая меньше

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def get_distance_to(self, point: Point) -> float:
        return round(math.sqrt((self._x - point.x) ** 2 + (self._y - point.y) ** 2), PRECISION)


class Cluster(list):
    """Кластер точек"""

    def __init__(self, points: list[Point] = None) -> None:
        if not points:
            points = []

        super().__init__(points)

    def get_geometric_center(self) -> Point:
        """Вычислить геометрический центр кластера"""

        if len(self) == 0:
            raise ValueError("calculating geometric center of empty cluster")
        elif len(self) == 1:
            return self[0]

        return Point(
            sum((point.x for point in self)) / len(self),
            sum((point.y for point in self)) / len(self)
        )


class Segment:
    """Отрезок не нулевой длины, соединяющий две точки

    Attributes:
        _start: Начало отрезка
        _finish: Конец отрезка
        _length: Длина отрезка, по умолчанию Евклидово расстояние между началом и концом
    """

    def __init__(self, start: Point, finish: Point, length: float = 0):
        self._start = start
        self._finish = finish

        euclidian_distance = start.get_distance_to(finish)

        if length and length < euclidian_distance:
            raise ValueError("edge length cannot be less than the Euclidean distance")

        self._length = round(length, PRECISION) if length else euclidian_distance

    def __eq__(self, other) -> bool:
        return other.start == self._start and other.finish == self._finish

    def __hash__(self) -> int:
        return hash((self._start, self._finish))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._start}, {self._finish})"

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
        self._edges_amt = 0

    def __contains__(self, item) -> bool:
        return item in self._adjacency_lists

    @property
    def adjacency_lists(self) -> dict[Point, list[Segment]]:
        return self._adjacency_lists

    def add_edge(self, edge: Segment) -> None:
        if self._edges_amt == _limits.EDGES_AMOUNT:
            raise ex.LimitExceededError("trying to add an edge to the full graph")

        for node in edge.start, edge.finish:
            if node not in self._adjacency_lists:
                self._adjacency_lists[node] = []

            self._adjacency_lists[node].append(edge)

        self._edges_amt += 1
