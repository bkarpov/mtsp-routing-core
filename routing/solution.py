"""Решение MTSP"""

from __future__ import annotations

import multiprocessing as mp
import random
from typing import Iterator

from routing import _exceptions as ex
from routing import _limits
from routing import _spatial_objects as sp
from routing.algorithms import a_star
from routing.algorithms import genetic_algorithm as ga
from routing.algorithms import k_means


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
    elif len(points) > _limits.POINTS_AMOUNT:
        raise ex.LimitExceededError("amount of points exceeded the limit")
    elif clusters_amt <= 0:
        raise ValueError("wrong amount of clusters")
    elif clusters_amt > _limits.CLUSTERS_AMOUNT:
        raise ex.LimitExceededError("amount of clusters exceeded the limit")
    elif not _points_are_reachable(points, graph):
        raise ValueError("all points in the graph must be reachable")
    elif len(points) // clusters_amt > _limits.POINTS_PER_CLUSTER:
        raise ex.LimitExceededError("amount of points per cluster exceeded the limit")

    unordered_clusters = k_means.k_means(points, clusters_amt)  # Кластеризовать точки
    ordered_clusters = []

    with mp.Pool() as pool:  # Решить TSP в каждом кластере
        tsp_jobs = []

        for cluster in unordered_clusters:
            tsp_jobs.append(pool.apply_async(ga.genetic_algorithm_for_tsp, (cluster, _limits.TSP_TIME)))

        for job in tsp_jobs:
            ordered_clusters.append(job.get(_limits.TSP_TIME + 1))

    with mp.Pool() as pool:  # Построить маршруты в кластерах
        mapping_jobs = []

        for cluster in ordered_clusters:
            mapping_jobs.append(pool.apply_async(_map_route_on_graph, (cluster, graph)))

        routes = [job.get(_limits.ROUTING_TIME) for job in mapping_jobs]

    return zip(ordered_clusters, routes)


def _points_are_reachable(points: list[sp.Point], graph: sp.Graph) -> bool:
    """Проверить, что все переданные точки достижимы

    Точки должны быть в графе, т.е. у каждой точки должен быть свой список смежности
    Точки должны быть достижимы из любой другой точки => граф сильно связный

    Args:
        points: Список точек, который нужно кластеризовать
        graph: Граф, в котором будут строиться маршруты
    """

    for point in points:
        if point not in graph:
            return False

    stack = [random.choice(points)]
    visited_points = set()

    while stack:  # Обход графа DFS
        point = stack.pop()

        if point in visited_points:
            continue

        visited_points.add(point)

        for edge in graph.adjacency_lists[point]:
            stack.append(edge.get_another_border(point))

    if not visited_points.issuperset(points):
        return False  # Не все точки посещены

    return True


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
