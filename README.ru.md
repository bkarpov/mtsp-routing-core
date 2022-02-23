[EN](https://github.com/bkarpov/mtsp-routing-core/blob/main/README.md)

# mtsp-routing-core

Решить multiple traveling salesman problem (MTSP).

---

## Исходные данные
1. Список пунктов назначения A, все вершины из которого должны быть достижимы в графе G
2. Количество кластеров K
3. Сильно связный взвешенный граф G, представленный списками смежности, вес ребра равен его длине
   1. n - количество вершин в графе
   2. m - количество ребер

---

## Алгоритм

### I. Проверить, что точки из A достижимы в G
Временная сложность O(n<sup>2</sup>).

### II. Разбить точки из A на кластеры
Временная сложность 1 итерации алгоритма O(n<sup>2</sup> * m * log(n * P)), P - наибольшая длина ребра.

Лимит итераций = 1000.

Для разделения точек используется алгоритм
[Constrained K-Means](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2000-65.pdf).

Для решения minimum-cost flow problem используется библиотека
[Google OR-Tools](https://developers.google.com/optimization/flow/mincostflow).

### III. Решить TSP в каждом кластере

Время выполнения в секундах = 30 * K / C, C - количество доступных потоков.

Для решения используется генетический алгоритм. Поиск решения для 1 кластера выполняется 30 секунд.

### IV. Построить маршрут в каждом кластере

Временная сложность O(n * m).

Для построения маршрута между двумя вершинами используется алгоритм A*.

---

## API

### 1. Построить маршруты
   1. Входные данные - список с пунктами назначения, количество маршрутов, граф с дорожной сетью
   2. Результат - итератор, возвращающий кортежи с двумя списками (точки и ребра графа в порядке обхода маршрута)
```
from routing import solution

solution.build_routes(
    points: list[Point], clusters_amt: int, graph: sp.Graph
) -> Iterator[tuple[list[Point], list[Segment]]]:
```

### 2. Создать точку
   1. Координаты округляются до 6 знаков после запятой
   2. Координаты точки неизменяемы
```
from routing import spatial_objects

spatial_objects.Point(x: float, y: float)
```

### 3. Создать ребро графа
   1. Координаты округляются до 6 знаков после запятой
   2. Если длина не передана в конструктор, то она вычисляется как Евклидово расстояние между началом и концом
   3. Начало отрезка, конец отрезка и длина неизменяемы
```
from routing import spatial_objects

spatial_objects.Segment(start: Point, finish: Point, length: float = 0)
```

### 4. Создать граф
```
from routing import spatial_objects

spatial_objects.Graph()
```

### 5. Добавить ребро в граф
```
from routing import spatial_objects

spatial_objects.Graph().add_edge(edge: Segment) -> None
```
