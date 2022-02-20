"""Решение MTSP"""

from __future__ import annotations

import multiprocessing as mp
import random
from typing import Iterator

from routing import _spatial_objects as sp
from routing.algorithms import a_star
from routing.algorithms import genetic_algorithm as ga
from routing.algorithms import k_means

_TSP_TIMELIMIT = 30  # Время решения TSP в 1 кластере
_ROUTING_TIMELIMIT = 10  # Время построения 1 маршрута в графе


def build_routes(
        points: list[sp.Point], clusters_amt: int, graph: sp.Graph
) -> Iterator[tuple[list[sp.Point], list[sp.Segment]]]:
    """Проложить указанное число маршрутов

    Этапы решения
    - Разделить список точек на k списков
    - Определить порядок обхода точек в кластере == решить TSP в каждом кластере
    - - Выполнять параллельно в нескольких кластерах
    - Проложить маршрут в графе
    - - Выполнять параллельно в нескольких кластерах

    Args:
        points: Список точек, который нужно кластеризовать
        clusters_amt: Количество кластеров, на которые нужно разбить точки
        graph: Граф для прокладывания маршрутов, представленный списками смежности

    Returns:
        Кортеж из списка кластеров и списка соответствующих им маршрутов
    """

    if not points:
        raise ValueError("empty list of clustering points")
    elif clusters_amt <= 0:
        raise ValueError("wrong amount of clusters")

    unreachable_points = _find_unreachable_points(points, graph)

    if unreachable_points:
        raise ValueError(f"unreachable points found: {unreachable_points}")

    unordered_clusters = k_means.k_means(points, clusters_amt)  # Кластеризовать точки
    ordered_clusters = []

    with mp.Pool() as pool:  # Решить TSP в каждом кластере
        tsp_jobs = []

        for cluster in unordered_clusters:
            tsp_jobs.append(pool.apply_async(ga.genetic_algorithm_for_tsp, (cluster, _TSP_TIMELIMIT)))

        for job in tsp_jobs:
            ordered_clusters.append(job.get(_TSP_TIMELIMIT + 1))

    with mp.Pool() as pool:  # Построить маршруты в кластерах
        mapping_jobs = []

        for cluster in ordered_clusters:
            mapping_jobs.append(pool.apply_async(_map_route_on_graph, (cluster, graph)))

        routes = [job.get(_ROUTING_TIMELIMIT) for job in mapping_jobs]

    return zip(ordered_clusters, routes)


def _find_unreachable_points(points: list[sp.Point], graph: sp.Graph) -> list[sp.Point]:
    """Найти недостижимые точки

    Точки должны быть в графе, т.е. у каждой точки должен быть свой список смежности
    Точки должны быть достижимы из любой другой точки => граф сильно связный

    Args:
        points: Список точек, который нужно кластеризовать
        graph: Граф, в котором будут строиться маршруты
    """

    isolated_points = []

    for point in points:  # Найти изолированные вершины
        if point not in graph:
            points.remove(point)
            isolated_points.append(point)

    if not points:
        return isolated_points

    stack = [random.choice(points)]
    visited_points = set()

    while stack:  # Найти вершины не посещенной компоненты связности
        point = stack.pop()

        if point in visited_points:
            continue

        visited_points.add(point)

        for edge in graph.adjacency_lists[point]:
            stack.append(edge.get_another_border(point))

    return isolated_points + list(set(points) - visited_points)


def _map_route_on_graph(ordered_cluster: sp.Cluster, graph: sp.Graph) -> list[sp.Segment]:
    """Построить маршрут в графе

    Args:
        ordered_cluster: Кластер с заданным порядком обхода точек
        graph: Граф для прокладывания маршрута

    Returns:
        Построенный маршрут
    """

    route = []  # Путь - список ребер графа

    for i, start in enumerate(ordered_cluster):
        finish = ordered_cluster[i + 1 if (i + 1) < len(ordered_cluster) else (i + 1 - len(ordered_cluster))]
        route.extend(a_star.a_star(start, finish, graph))

    return route
