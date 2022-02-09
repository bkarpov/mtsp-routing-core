"""Алгоритм А*

Алгоритм поиска кратчайшего пути между двумя вершинами во взвешенном ориентированном графе

Приоритет вершины f(x) = g(x) + h(x)
- g(x) - длина кратчайшего пути от начальной вершины до x
- h(x) - эвристическая оценка длины пути от x до искомой вершины
- - Оценка h(x) оптимистическая, т.е. h(x) <= реальной длины от x до искомой вершины
- - Чем меньше результаты h(x), тем больше вершин рассматривается, тем медленнее работает алгоритм
- - Если ∀x h(x) = 0, то A* ~ Dijkstra

Алгоритм
- Добавить начальную вершину в очередь
- Цикл
- - Извлечь вершину из очереди
- - Если вершина является искомой, выйти из цикла
- - Добавить в очередь все непосещенные вершины, смежные с извлеченной

Временная сложность O(|E|), E - множество ребер графа
"""

from __future__ import annotations

import collections
import heapq

from routing import _spatial_objects as sp


def a_star(start: sp.Point, finish: sp.Point, graph: sp.Graph) -> list[sp.Segment]:
    """Выполнить алгоритм А*

    Args:
        start: Вершина, из которой выполняется поиск
        finish: Искомая вершина
        graph: Граф, представленный списками смежности

    Returns:
        Кратчайший путь от начальной вершины к искомой
    """

    a_star_data = collections.namedtuple("AStarData", ["distance", "parent", "edge"])
    data = {start: a_star_data(0, None, None)}
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))
    path = []

    while priority_queue:
        current_node = heapq.heappop(priority_queue)[-1]

        if current_node == finish:
            while data[current_node].edge is not None:  # Восстановить путь
                path.append(data[current_node].edge)
                current_node = data[current_node].parent

            path.reverse()  # Развернуть путь, чтобы он был от старта к финишу
            break

        for edge in graph.adjacency_lists[current_node]:  # Добавить в очередь все смежные непосещенные вершины
            adjacent = edge.get_another_border(current_node)

            if adjacent not in data:
                data[adjacent] = a_star_data(data[current_node].distance + edge.length, current_node, edge)
                heapq.heappush(
                    priority_queue,
                    (data[adjacent].distance + adjacent.get_distance_to(finish), adjacent)
                )

    return path
