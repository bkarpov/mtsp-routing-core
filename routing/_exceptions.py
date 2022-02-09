"""Исключения"""


class RoutingError(Exception):
    """Ошибка при выполнении маршрутизации"""

    pass


class KMeansError(Exception):
    """Ошибка в алгоритме K-Means"""

    pass


class LimitExceededError(Exception):
    """Превышен лимит, описанный в README.md"""

    pass
