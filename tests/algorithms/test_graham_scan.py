"""Тесты сканирования Грэхема"""


from routing import spatial_objects as sp
from routing.algorithms import graham_scan as gs


def test_cross_product_calculation() -> None:
    """Тест подсчета векторного произведения векторов

    Если вектор из векторного произведения направлен вверх, то выполнен поворот по часовой стрелке"""

    assert gs._is_turn_counterclockwise([sp.Point(1, 1), sp.Point(3, 5)], sp.Point(1, 4))


def test_graham_scan() -> None:
    """Тест нахождения выпуклой оболочки"""

    test_case = [
        sp.Point(2, 0), sp.Point(2, -2), sp.Point(1, -1), sp.Point(0, -2),
        sp.Point(-2, -1), sp.Point(-2, 2), sp.Point(-1, -1.5)
    ]

    correct_result = [
        sp.Point(0, -2), sp.Point(2, -2), sp.Point(2, 0), sp.Point(-2, 2), sp.Point(-2, -1)
    ]

    assert gs.graham_scan(test_case) == correct_result
