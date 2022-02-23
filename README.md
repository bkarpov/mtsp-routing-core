[RU](README.ru.md)

# mtsp-routing-core

Solve the multiple travelling salesman problem (MTSP).

---

## Initial data
1. A - list of destinations, all vertices from which should be reachable in graph G
2. K - number of clusters
3. G - strongly connected weighted graph represented by adjacency lists. The weight of an edge is equal to its length 
   1. n - number of vertices in the graph
   2. m - number of edges

---

## Algorithm

### I. Check that points from A are reachable in G
The time complexity is O(n<sup>2</sup>).

### II. Divide points from A into clusters
The time complexity of 1 iteration of the algorithm is O(n<sup>2</sup> * m * log(n * P)), P is the largest edge length.

Iteration limit = 1000.

The [Constrained K-Means](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2000-65.pdf)
algorithm is used for clustering points.

To solve the minimum-cost flow problem (MCFP), the
[Google OR-Tools](https://developers.google.com/optimization/flow/mincostflow) library is used.

### III. Solve the travelling salesman problem (TSP) in each cluster

Execution time in seconds = 30 * K / C, C - number of available CPU threads.

A genetic algorithm is used to solve the problem. The search for a solution for 1 cluster takes 30 seconds.

### IV. Build a route in each cluster

The time complexity is O(n * m).

To build a route between two vertices, the A* algorithm is used.

---

## API

### 1. Build routes
   1. Input - a list with destinations, the number of routes, a graph with a road network
   2. Output - an iterator that returns tuples with two lists (points and edges in the order of traversal of the route)
```
from routing import solution

solution.build_routes(
    points: list[Point], clusters_amt: int, graph: sp.Graph
) -> Iterator[tuple[list[Point], list[Segment]]]:
```

### 2. Create a point
   1. Coordinates are rounded to 6 decimal places
   2. The coordinates of the point cannot be changed
```
from routing import spatial_objects

spatial_objects.Point(x: float, y: float)
```

### 3. Create an edge of the graph
   1. The length of the segment is rounded to 6 decimal places
   2. If the length is not passed to the constructor, then it is calculated as the Euclidean distance between the ends
   3. The beginning of the segment, the end of the segment and the length cannot be changed
```
from routing import spatial_objects

spatial_objects.Segment(start: Point, finish: Point, length: float = 0)
```

### 4. Create a graph
```
from routing import spatial_objects

spatial_objects.Graph()
```

### 5. Add an edge to the graph
```
from routing import spatial_objects

spatial_objects.Graph().add_edge(edge: Segment) -> None
```
