"""Тесты алгоритма кластеризации K-Means с ограничением"""


from __future__ import annotations

import itertools
import random

import pytest

from routing import spatial_objects as sp
from routing.algorithms import k_means as km


def test_clustering_without_remainder() -> None:
    points, clusters_amt = _get_test_case(use_remainder=False)
    result = km.k_means(points, clusters_amt)

    assert len(result) == clusters_amt  # Количество кластеров соответствует переданному в алгоритм

    cluster_size = len(points) // clusters_amt

    for cluster in result:  # Размер кластеров в допуске
        assert cluster_size == len(cluster)

    result_points = list(itertools.chain(*result))
    assert len(result_points) == len(points) and set(result_points) == set(points)  # Все точки кластеризованы

    # Проверка того, что расстояния между центроидами кластеров больше наибольших расстояний в самих кластерах
    max_distance_in_clusters = []

    for cluster in result:
        max_distance = 0

        for first, second in itertools.combinations(cluster.points, 2):
            max_distance = max(max_distance, first.get_distance_to(second))

        max_distance_in_clusters.append(max_distance)

    for i, cluster in enumerate(result):
        first_centroid = cluster.get_geometric_center()

        for j in range(i + 1, clusters_amt):
            second_centroid = result[j].get_geometric_center()
            distance = first_centroid.get_distance_to(second_centroid)

            assert distance > max_distance_in_clusters[i] and distance > max_distance_in_clusters[j]


def test_clustering_with_remainder() -> None:
    points, clusters_amt = _get_test_case()
    result = km.k_means(points, clusters_amt)

    assert len(result) == clusters_amt  # Количество кластеров соответствует переданному в алгоритм

    cluster_size = len(points) // clusters_amt

    for cluster in result:  # Размер кластеров в допуске
        assert cluster_size <= len(cluster) <= cluster_size + 1

    result_points = list(itertools.chain(*result))
    assert len(result_points) == len(points) and set(result_points) == set(points)  # Все точки кластеризованы


@pytest.mark.timeout(60)  # Время выполнения 1 попытки не более 1 минуты
def test_clustering_performance(benchmark) -> None:
    points, clusters_amt = _get_test_case(clusters_amt_bounds=(10, 100), points_per_cluster_bounds=(100, 200))
    benchmark.pedantic(km.k_means, (points, clusters_amt), rounds=5)


def _get_test_case(
        clusters_amt_bounds=(5, 10),
        points_per_cluster_bounds=(5, 10),
        use_remainder=True
) -> tuple[list[sp.Point], int]:
    """Сгенерировать список точек для кластеризации

    Args:
        clusters_amt_bounds: Границы количества кластеров, границы включаются
        points_per_cluster_bounds: Границы количества точек в кластере, границы включаются
        use_remainder: Добавлять ли дополнительные точки == остаток при делении количества точек на кластеры

    Returns:
        Список точек и количество кластеров
    """

    clusters_amt = random.randint(*clusters_amt_bounds)
    points_per_cluster = random.randint(*points_per_cluster_bounds)
    points = []

    for i in range(clusters_amt):  # Точки по кластерам, расстояние между точками << расстояние между кластерами
        for j in range(points_per_cluster):
            points.append(sp.Point(random.random() + i * 10, random.random() + i * 10))

    if use_remainder:
        remainder = random.randint(1, points_per_cluster)  # Случайные точки

        for i in range(remainder):
            points.append(sp.Point(random.randint(0, clusters_amt * 10), random.randint(0, clusters_amt * 10)))

    return points, clusters_amt
