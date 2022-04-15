"""Тесты отдельных функций, используемых при решении MTSP, и всего решения в целом"""


import itertools
import pytest
from timeit import default_timer as timer

from routing import solution as sl
from routing import spatial_objects as sp


def test_points_and_graph_validation() -> None:
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

    assert sl._find_unreachable_points([sp.Point(0, 0)], graph) == [sp.Point(0, 0)]

    unreachable_points = set(sl._find_unreachable_points(points, graph))
    assert unreachable_points == set(points[:4]) or unreachable_points == set(points[4:])  # Одна компонента недоступна

    graph.add_edge(sp.Segment(sp.Point(2, 3), sp.Point(4, 3)))  # Добавить мост, соединяющий компоненты связности
    assert not sl._find_unreachable_points(points, graph)


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


def test_solution() -> None:
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

    results = list(sl.build_routes(list(points), clusters_amt, graph))  # Маршрутизация с максимальной нагрузкой на CPU

    assert set(results[0][0]) == set(points[:6])  # Кластер с 1 фигурой
    assert set(results[0][1]) == set(edges[:6])  # Маршрут обхода совпадает с контуром

    assert set(results[1][0]) == set(points[6:])  # Кластер с 2 фигурой
    assert set(results[1][1]) == set(edges[14:20])  # Маршрут обхода совпадает с контуром


@pytest.mark.parametrize("processes_num", [1, 2, 4])  # Маркировка теста для многократного выполнения
def test_execution_time(processes_num: int) -> None:
    """Тест времени выполнения маршрутизации

    Чтобы тест работал корректно, количество логических процессоров должно быть не менее 4

    Args:
        processes_num: Количество доступных процессов
    """

    clusters_amt = 4

    points = (
        sp.Point(2, 1), sp.Point(3, 2), sp.Point(3, 3), sp.Point(2, 4), sp.Point(1, 3), sp.Point(1, 2),  # Figure 1
        sp.Point(8, 1), sp.Point(9, 2), sp.Point(9, 3), sp.Point(8, 4), sp.Point(7, 3), sp.Point(7, 2),  # Figure 2
        sp.Point(8, 8), sp.Point(9, 9), sp.Point(9, 10), sp.Point(8, 11), sp.Point(7, 10), sp.Point(7, 9),  # Figure 3
        sp.Point(2, 8), sp.Point(3, 9), sp.Point(3, 10), sp.Point(2, 11), sp.Point(1, 10), sp.Point(1, 9),  # Figure 4
    )

    points_combinations = []

    for start_idx in range(0, 24, 6):
        points_combinations.extend(list(itertools.combinations(points[start_idx:start_idx + 6], 2)))

    edges = [sp.Segment(first, second) for first, second in points_combinations]

    edges.extend([
        sp.Segment(points[0], points[6]), sp.Segment(points[0], points[12]), sp.Segment(points[0], points[18]),
        sp.Segment(points[6], points[12]), sp.Segment(points[6], points[18]),
        sp.Segment(points[12], points[18]),
    ])

    graph = sp.Graph()

    for edge in edges:
        graph.add_edge(edge)

    start = timer()
    sl.build_routes(list(points), clusters_amt, graph, processes_num)
    execution_time = timer() - start

    assert execution_time > sl._TSP_TIMELIMIT * clusters_amt / processes_num
    assert execution_time <= (sl._TSP_TIMELIMIT + sl._ROUTING_TIMELIMIT) * clusters_amt / processes_num
