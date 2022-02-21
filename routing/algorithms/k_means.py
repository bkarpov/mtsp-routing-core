"""Алгоритм кластеризации K-Means"""

from __future__ import annotations

import itertools
import random

from ortools.graph import pywrapgraph

from routing import _spatial_objects as sp
from routing.algorithms import graham_scan as gs

_MAX_ITERATIONS = 10  # Предельное количество итераций в K-Means


class KMeansError(Exception):
    """Ошибка в алгоритме K-Means"""

    pass


def k_means(points: list[sp.Point], clusters_amt: int) -> list[sp.Cluster]:
    """Алгоритм K-Means с ограничением максимального размера кластера

    Если точки не делятся на равные кластеры, то остаток от деления распределяется по кластерам по 1 точке

    Алгоритм K-Means
    - Выбрать начальные центры кластеров
    - - Построить выпуклую оболочку алгоритмом Грэхема  # O(n*logn)
    - - Выбрать 2 наиболее удаленные точки из выпуклой оболочки - 2 первых центра  # O(n^2)
    - - Выбрать оставшиеся центры, как наиболее удаленные от текущих выбранных центров  # O(k*n)
    - Цикл, пока меняются центроиды и пока не достигнут лимит итераций
    - - Разделить точки на кластеры
    - - Обновить центроиды

    Args:
        points: Список точек, который нужно кластеризовать
        clusters_amt: Количество кластеров, на которые нужно разбить точки

    Returns:
        Стабилизированные кластеры, полученные при разделении переданного списка точек
    """

    if clusters_amt == 1:
        return [sp.Cluster(points)]
    elif clusters_amt >= len(points):
        return [sp.Cluster([point]) for point in points]

    clusters: list[sp.Cluster] = []
    centroids: list[sp.Point] = _get_initial_clusters_centers(points, clusters_amt)  # O(n^2)

    for j in range(_MAX_ITERATIONS):
        clusters = _divide_points_into_clusters(points, clusters_amt, centroids)  # O(n^3*log(n*C))
        centroids_buffer = centroids
        centroids = []

        for cluster in clusters:  # Пересчитать центроиды
            centroids.append(cluster.get_geometric_center() if cluster else random.choice(points))
            # Если кластер пустой, выбрать случайную точку в качестве центроида

        if centroids == centroids_buffer:
            break

    return clusters


def _get_initial_clusters_centers(points: list[sp.Point], clusters_amt: int) -> list[sp.Point]:
    """Выбрать центры кластеров из списка кластеризуемых точек

    Алгоритм
    - Построить выпуклую оболочку алгоритмом Грэхема
    - Выбрать 2 наиболее удаленные точки из выпуклой оболочки == 2 первых центра
    - Цикл пока не найдено достаточное количество центров
    - - Добавить в список центров точку, наиболее удаленную от уже выбранных

    Временная сложность O(n^2)

    Источник - исходный код QGIS

    Returns:
        Список с вершинами, выбранными в качестве центров кластеров
    """

    convex_hull: list[sp.Point] = gs.graham_scan(points)
    max_distance = -1  # Максимальное расстояние между парой вершин в оболочке
    first_center = second_center = None

    for i, j in itertools.combinations(convex_hull, r=2):  # Найти максимальное расстояние между парой точек O(n^2)
        distance_in_pair = i.get_distance_to(j)

        if distance_in_pair > max_distance:
            first_center, second_center = i, j
            max_distance = distance_in_pair

    centers_indexes = [points.index(first_center), points.index(second_center)]
    distances = [float("inf")] * len(points)  # Минимальные расстояния от вершин до любого из центров
    distances[centers_indexes[0]] = distances[centers_indexes[1]] = 0  # Расстояния до центров кластеров == 0

    for i in range(2, clusters_amt):  # Выбрать вершины в качестве центров O(kn)
        last_added_center = points[centers_indexes[-1]]
        distance_to_candidate = float("-inf")  # Наибольшее расстояние до точки, не являющейся центром кластера
        candidate_index = -1

        for j, current_distance in enumerate(distances):
            if not current_distance:  # Пропустить центры кластеров
                continue

            distances[j] = min(current_distance, points[j].get_distance_to(last_added_center))

            if distances[j] > distance_to_candidate:
                candidate_index = j
                distance_to_candidate = distances[j]

        centers_indexes.append(candidate_index)  # Добавить новый центр кластера
        distances[candidate_index] = 0  # Обнулить расстояние до центра кластера из него самого

    return [points[i] for i in centers_indexes]


def _divide_points_into_clusters(
        points: list[sp.Point], clusters_amt: int, centroids: list[sp.Point]
) -> list[sp.Cluster]:
    """Разделить точки на кластеры одинаково размера

    Задача сводится к нахождению min-cost max flow в сети
    - Исток - фиктивная точка с количеством юнитов потока == количеству кластеризуемых вершин
    - - Исток соединен со всеми кластеризуемыми вершинами
    - - - Пропускная способность ребра = 1
    - - - Стоимость транспортировки одного юнита = 0
    - Кластеризуемые вершины - вершины с 0 юнитов потока
    - - Вершины соединены со всеми центроидами
    - - - Пропускная способность ребра = 1
    - - - Стоимость транспортировки юнита = расстоянию от вершины до центроида
    - Центроиды - вершины с 0 юнитов потока
    - - Центроиды соединены со стоком
    - - - Пропускная способность ребра ∈ ⌊n / k⌋, ⌈n / k⌉
    - - - Стоимость транспортировки одного юнита = 0
    - Сток - фиктивная точка с количеством юнитов потока == количеству кластеризуемых вершин * -1

    Min-cost max flow решается с помощью Google OR-Tools

    Источник - Constrained K-Means Clustering - Microsoft Research

    Временная сложность O(n^2*m*log(nC)), где n - количество вершин, m - количество ребер, C - наибольшая стоимость дуги

    Returns:
        Кластеры, полученные при разделении переданного списка точек
    """

    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    for i in range(1, len(points) + 1):  # Добавить ребра от истока до вершин, индексы вершин от 1 до n включительно
        point = points[i - 1]
        min_cost_flow.AddArcWithCapacityAndUnitCost(0, i, 1, 0)  # Start, end, capacity, cost

        for j in range(len(points) + 1, len(points) + clusters_amt + 1):  # Добавить ребра от вершины до центроидов
            centroid = centroids[j - len(points) - 1]
            min_cost_flow.AddArcWithCapacityAndUnitCost(
                i, j, 1, int(point.get_distance_to(centroid) * (10 ** sp.get_precision()))
            )  # Индексы центроидов от n+1 до n+k включительно

        min_cost_flow.SetNodeSupply(i, 0)  # Задать 0 количество юнитов для вершины

    # Индекс истока всегда = 0
    sink_idx = len(points) + clusters_amt + 1  # Сток с индексом n+k+1
    edge_capacity = len(points) // clusters_amt
    remainder = len(points) % clusters_amt

    for i in range(clusters_amt):  # Добавить ребра от центроидов до стока
        centroid_idx = i + len(points) + 1
        min_cost_flow.SetNodeSupply(centroid_idx, 0)  # Задать 0 количество юнитов для центроида

        # Увеличить пропускную способность на 1 у remained ребер для распределения остатка
        min_cost_flow.AddArcWithCapacityAndUnitCost(centroid_idx, sink_idx, edge_capacity + bool(i < remainder), 0)

    # Задать количество юнитов у истока и стока
    min_cost_flow.SetNodeSupply(0, len(points))
    min_cost_flow.SetNodeSupply(sink_idx, -len(points))

    status = min_cost_flow.Solve()

    if status != min_cost_flow.OPTIMAL:
        raise KMeansError("the optimal solution was not found in the network")

    clusters: list[sp.Cluster[sp.Point]] = [sp.Cluster() for _ in range(clusters_amt)]

    for arc in range(min_cost_flow.NumArcs()):
        arc_between_node_and_centroid = min_cost_flow.Tail(arc) != 0 and min_cost_flow.Head(arc) != sink_idx

        if arc_between_node_and_centroid and min_cost_flow.Flow(arc):  # У использованных ребер не нулевой поток
            point_idx = min_cost_flow.Tail(arc) - 1
            centroid_idx = min_cost_flow.Head(arc) - len(points) - 1
            cluster: sp.Cluster = clusters[centroid_idx]
            cluster.append(points[point_idx])

    return clusters
