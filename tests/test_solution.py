"""Тесты отдельных функций, используемых при решении MTSP, и всего решения в целом"""

import random

import pytest

from routing import _limits
from routing import _spatial_objects as sp
from routing import solution as sl


def test_points_reachability_check() -> None:
    """Тест проверки списков смежности и обхода графа

    Граф - две компоненты связности"""

    points = [
        sp.Point(1, 2), sp.Point(2, 3), sp.Point(2, 1), sp.Point(4, 1),  # Первая компонента связности
        sp.Point(4, 3), sp.Point(5, 2),  # Вторая компонента связности
    ]

    edges = [
        # Первая компонента связности
        sp.Segment(sp.Point(1, 2), sp.Point(2, 3)),
        sp.Segment(sp.Point(2, 1), sp.Point(3, 2)),
        sp.Segment(sp.Point(2, 3), sp.Point(3, 2)),
        sp.Segment(sp.Point(3, 2), sp.Point(4, 1)),
        # Вторая компонента связности
        sp.Segment(sp.Point(4, 3), sp.Point(5, 2)),
    ]

    graph = sp.Graph()

    for edge in edges:
        graph.add_edge(edge)

    assert not sl._points_are_reachable([sp.Point(0, 0)], graph)
    assert not sl._points_are_reachable(points, graph)

    graph.add_edge(sp.Segment(sp.Point(2, 3), sp.Point(4, 3)))  # Добавить мост, соединяющий компоненты связности

    assert sl._points_are_reachable(points, graph)


def test_route_mapping() -> None:
    """Тест поиска пути в графе

    Граф - дерево"""

    # points = [
    #     sp.Point(1, 2), sp.Point(2, 3), sp.Point(2, 1), sp.Point(4, 1),
    #     sp.Point(4, 3), sp.Point(5, 2), sp.Point(2, 6)
    # ]

    route = sp.Cluster([sp.Point(2, 6), sp.Point(4, 1), sp.Point(5, 2)])

    edges = [
        sp.Segment(sp.Point(1, 2), sp.Point(2, 3)),
        sp.Segment(sp.Point(2, 1), sp.Point(3, 2)),
        sp.Segment(sp.Point(2, 3), sp.Point(3, 2)),
        sp.Segment(sp.Point(3, 2), sp.Point(4, 1)),
        sp.Segment(sp.Point(4, 3), sp.Point(5, 2)),
        sp.Segment(sp.Point(2, 3), sp.Point(4, 3)),
        sp.Segment(sp.Point(2, 6), sp.Point(2, 3)),
    ]

    graph = sp.Graph()

    for edge in edges:
        graph.add_edge(edge)

    answer = [
        sp.Segment(sp.Point(2, 6), sp.Point(2, 3)),  # (2, 6) -> (2, 3)
        sp.Segment(sp.Point(2, 3), sp.Point(3, 2)),  # ______ -> (3, 2)
        sp.Segment(sp.Point(3, 2), sp.Point(4, 1)),  # ______ -> (4, 1)
        sp.Segment(sp.Point(3, 2), sp.Point(4, 1)),  # ______ -> (3, 2)
        sp.Segment(sp.Point(2, 3), sp.Point(3, 2)),  # ______ -> (2, 3)
        sp.Segment(sp.Point(2, 3), sp.Point(4, 3)),  # ______ -> (4, 3)
        sp.Segment(sp.Point(4, 3), sp.Point(5, 2)),  # ______ -> (5, 2)
        sp.Segment(sp.Point(4, 3), sp.Point(5, 2)),  # ______ -> (4, 3)
        sp.Segment(sp.Point(2, 3), sp.Point(4, 3)),  # ______ -> (2, 3)
        sp.Segment(sp.Point(2, 6), sp.Point(2, 3)),  # ______ -> (2, 6)
    ]

    calculated_route = sl._map_route_on_graph(route, graph)

    assert calculated_route == answer


def test_route_mapping_performance() -> None:
    """Тест производительности поиска пути в графе"""

    points = [sp.Point(random.randint(1, 1000), random.randint(1, 1000)) for _ in range(_limits.POINTS_AMOUNT)]
    points = list(set(points))  # Удалить дубликаты точек

    edges = []

    for i in range(_limits.EDGES_AMOUNT // _limits.POINTS_AMOUNT):
        for j in range(1, len(points)):
            start = random.choice(points[:j])
            finish = random.choice(points[j:])

            if start == finish:
                continue

            if start < finish:
                start, finish = finish, start

            edges.append(  # Соединить случайную обработанную вершину со случайной необработанной
                sp.Segment(start, finish)
            )

    edges = list(set(edges))  # Удалить дубликаты ребер
    graph = sp.Graph()

    for edge in edges:
        graph.add_edge(edge)

    @pytest.mark.timeout(_limits.MAPPING_TIME)
    def performance_test() -> None:
        """Запуск поиска пути в отдельной функции, чтобы не включать в тайминг подготовку данных"""

        sl._map_route_on_graph(sp.Cluster(points), graph)

    performance_test()


def test_solution_full() -> None:
    """Тест всего решения

    Граф - две выпуклые фигуры, соединенные 1 ребром"""

    points = (  # Кластеризуемые вершины
        # Фигура 1
        sp.Point(1, 1), sp.Point(1, 2),
        sp.Point(2, 3), sp.Point(3, 3),
        sp.Point(3, 2), sp.Point(2, 1),
        # Фигура 2
        sp.Point(7, 6), sp.Point(7, 7),
        sp.Point(8, 8), sp.Point(9, 8),
        sp.Point(10, 7), sp.Point(10, 6),
    )

    clusters_amt = 2

    edges = (  # Ребра графа
        # Контур 1 фигуры
        sp.Segment(sp.Point(1, 1), sp.Point(1, 2)),
        sp.Segment(sp.Point(1, 2), sp.Point(2, 3)),
        sp.Segment(sp.Point(2, 3), sp.Point(3, 3)),
        sp.Segment(sp.Point(3, 3), sp.Point(3, 2)),
        sp.Segment(sp.Point(3, 2), sp.Point(2, 1)),
        sp.Segment(sp.Point(2, 1), sp.Point(1, 1)),
        # Ребра внутри 1 фигуры, включают пересечения в точках, не являющихся вершинами фигуры
        sp.Segment(sp.Point(1, 1), sp.Point(2, 2)),
        sp.Segment(sp.Point(2, 2), sp.Point(3, 3)),
        sp.Segment(sp.Point(1, 2), sp.Point(2, 1)),
        sp.Segment(sp.Point(2, 3), sp.Point(3, 2)),
        sp.Segment(sp.Point(2, 3), sp.Point(2, 2)),
        sp.Segment(sp.Point(2, 2), sp.Point(2, 1)),
        sp.Segment(sp.Point(1, 2), sp.Point(2, 2)),
        sp.Segment(sp.Point(2, 2), sp.Point(3, 2)),
        # Контур 2 фигуры
        sp.Segment(sp.Point(7, 6), sp.Point(7, 7)),
        sp.Segment(sp.Point(7, 7), sp.Point(8, 8)),
        sp.Segment(sp.Point(8, 8), sp.Point(9, 8)),
        sp.Segment(sp.Point(9, 8), sp.Point(10, 7)),
        sp.Segment(sp.Point(10, 7), sp.Point(10, 6)),
        sp.Segment(sp.Point(10, 6), sp.Point(7, 6)),
        # Ребра внутри 2 фигуры, включают пересечения в точках, не являющихся вершинами фигуры
        sp.Segment(sp.Point(7, 7), sp.Point(8, 7)),
        sp.Segment(sp.Point(8, 7), sp.Point(9, 7)),
        sp.Segment(sp.Point(9, 7), sp.Point(10, 7)),
        sp.Segment(sp.Point(8, 8), sp.Point(8, 7)),
        sp.Segment(sp.Point(8, 7), sp.Point(8, 6)),
        sp.Segment(sp.Point(9, 8), sp.Point(9, 7)),
        sp.Segment(sp.Point(9, 7), sp.Point(9, 6)),
        sp.Segment(sp.Point(3, 3), sp.Point(7, 6)),  # Мост
    )

    graph = sp.Graph()

    for edge in edges:
        graph.add_edge(edge)

    results = list(sl.build_routes(list(points), clusters_amt, graph))

    assert set(results[0][0]) == set(points[:6])  # Кластер с 1 фигурой
    assert set(results[0][1]) == set(edges[:6])  # Маршрут обхода совпадает с контуром

    assert set(results[1][0]) == set(points[6:])  # Кластер с 2 фигурой
    assert set(results[1][1]) == set(edges[14:20])  # Маршрут обхода совпадает с контуром
