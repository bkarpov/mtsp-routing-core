"""Тесты пространственных объектов"""


import pytest

from routing import _spatial_objects as sp

arguments = ("start", "finish", "distance")
data = (
    (sp.Point(1, 2), sp.Point(5, 5), 5),
    (sp.Point(-1, -2), sp.Point(2, 2), 5)
)


@pytest.mark.parametrize(arguments, data)
def test_calculation_distance_between_points(start: sp.Point, finish: sp.Point, distance: float) -> None:
    """Тест подсчета Евклидова расстояния"""

    assert start.get_distance_to(finish) == finish.get_distance_to(start) == distance


arguments = ("cluster", "center")
data = (
    (sp.Cluster([sp.Point(25, 40), sp.Point(15, 15), sp.Point(65, 20)]), sp.Point(35, 25)),
    (sp.Cluster([sp.Point(-3, -4), sp.Point(21, 6), sp.Point(54, -5)]), sp.Point(24, -1))
)


@pytest.mark.parametrize(arguments, data)
def test_getting_geometric_center_of_cluster(cluster: sp.Cluster, center: sp.Point) -> None:
    """Тест вычисления геометрического центра кластера"""

    assert cluster.get_geometric_center() == center
