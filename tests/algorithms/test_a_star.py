"""Тесты А*"""


from routing import spatial_objects as sp
from routing.algorithms import a_star


def test_finding_a_path() -> None:
    square_graph = sp.Graph()

    points = [
        sp.Point(3, 4), sp.Point(1, 3), sp.Point(2, 3), sp.Point(3, 3),
        sp.Point(1, 2), sp.Point(3, 2), sp.Point(1, 1), sp.Point(2, 1),
        sp.Point(3, 1)
    ]

    edges = [
        sp.Segment(points[6], points[4], 1),
        sp.Segment(points[6], points[7], 1),
        sp.Segment(points[4], points[2], 1.5),
        sp.Segment(points[4], points[1], 1),
        sp.Segment(points[1], points[2], 1),
        sp.Segment(points[7], points[8], 1),
        sp.Segment(points[7], points[5], 1.6),
        sp.Segment(points[2], points[3], 1),
        sp.Segment(points[3], points[0], 1),
    ]

    for bidirectional_edge in edges:
        square_graph.add_edge(bidirectional_edge)

    result = a_star.a_star(points[6], points[0], square_graph)
    assert result == [edges[0], edges[2], edges[7], edges[8]]
