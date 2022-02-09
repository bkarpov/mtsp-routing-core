"""Алгоритм Грэхема - Graham scan

Сканирование Грэхема - метод нахождения выпуклой оболочки конечного набора точек

Дан список вершин A, для которых нужно найти выпуклую оболочку
- На плоскости выпуклая оболочка - выпуклый многоугольник, внутри которого находятся все вершины переданного массива
- Вершины, составляющие границу многоугольника, также являются элементами переданного массива

Алгоритм
- Найти вершину P с наименьшими координатами Y и X
- Отсортировать исходный массив по полярному углу вершин, образованному с P
- Положить вершину P на стек S

- Цикл по всем точкам исходного массива
- - V - вершина, которая рассматривается для добавления в оболочку
- - Пока размер стека S > 1 И поворот от верха S относительно V совершается против часовой стрелки
- - - Снять вершину со стека S, так как многоугольник, образованный с V, "включает" ее
- - Положить V на стек S, если V != P
- Вершины оставшиеся в стеке S - выпуклая оболочка

Временная сложность O(n*logn)
"""


from __future__ import annotations

import math

from routing import _spatial_objects as sp


def graham_scan(data: list[sp.Point]) -> list[sp.Point]:
    """Выполнить алгоритм

    Args:
        data: Список точек для нахождения выпуклой оболочки

    Returns:
        Список с точками, образующими выпуклую оболочку
    """

    if len(data) < 3:
        raise ValueError("creating a convex hull of 2 points")

    origin = data[0]

    for point in data:  # Поиск первой точки
        if point.y < origin.y or (point.y == origin.y and point.x < origin.x):
            origin = point

    points = data.copy()
    points.sort(  # Сортировка по полярному углу
        key=lambda k: math.acos((k.x - origin.x) / k.get_distance_to(origin)) if k is not origin else float("inf")
    )  # origin должна быть в points, чтобы проверить предпоследний отрезок контура
    stack = [origin]

    for current in points:
        while len(stack) > 1 and not _is_turn_counterclockwise(stack, current):
            stack.pop()

        if current is not origin:
            stack.append(current)

    return stack


def _is_turn_counterclockwise(stack: list[sp.Point], current: sp.Point) -> bool:
    """Проверить, совершается ли поворот, выполняемый при добавлении новой точки в оболочку, против часовой стрелки

    Если вектор из векторного произведения направлен вверх, то выполнен поворот по часовой стрелке

    Args:
        stack: Стек вершин выпуклой оболочки
        current: Вершина, к которой совершается поворот

    Returns:
        Выполняется ли поворот против часовой стрелки
    """

    top = stack[-1]
    second_top = stack[-2]

    first_vector = sp.Point(top.x - second_top.x, top.y - second_top.y)
    second_vector = sp.Point(current.x - second_top.x, current.y - second_top.y)

    return (first_vector.x*second_vector.y - first_vector.y*second_vector.x) > 0
