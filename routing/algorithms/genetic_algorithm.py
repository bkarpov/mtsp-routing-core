"""Генетический алгоритм для решения TSP

Ген - город на определенной позиции в маршруте

Хромосома - индивидуальное решение - маршрут
- Хромосомы сравниваются по длинам описываемых ими маршрутов

Гены -> хромосомы -> популяция

Алгоритм
- Создание базовой популяции из K случайных хромосом => города в маршрутах отсортированы случайным образом
- Цикл
- - Скрещивание - создание 0.6 * K хромосом из 2 случайных
- - Мутация - создание 0.3 * K хромосом из 1 случайной
- - Вливание - создание 0.1 * K полностью случайных хромосом
- - Отбор K наиболее приспособленных хромосом из 2K == K хромосом с предыдущей итерации + K созданных на текущей
"""

from __future__ import annotations

import random
import time

from routing import _spatial_objects as sp

_POPULATION_SIZE = 50
_CROSSOVER_SIZE = 30
_MUTATION_SIZE = 15
_INFUSED_SIZE = 5


def genetic_algorithm_for_tsp(genes: list[sp.Point], time_limit: int = 30) -> list[sp.Point]:
    """Генетический алгоритм для решения TSP

    Args:
        genes: Гены - точки, из которых строится маршрут
        time_limit: Лимит времени в секундах для поиска решения

    Returns:
        Лучшая хромосома - маршрут, являющийся лучшим решением из найденных алгоритмом
    """

    if len(genes) <= 3:
        return genes.copy()

    answer = []
    population = [random.sample(genes, len(genes)) for _ in range(_POPULATION_SIZE)]
    end_timing = time.time() + time_limit

    while time.time() <= end_timing:
        created_population = []

        for j in range(_CROSSOVER_SIZE):
            created_population.append(_crossover(*random.sample(population, 2)))  # Скрещивание

        for chromosome in random.sample(population, _MUTATION_SIZE):
            created_population.append(_mutation(chromosome))  # Мутация

        created_population += [  # Добавление случайных хромосом, чтобы не застрять на локальном минимуме
            random.sample(genes, len(genes)) for _ in range(_INFUSED_SIZE)
        ]

        population += created_population
        population.sort(key=_estimation)  # Оценка

        if not answer or _estimation(answer) > _estimation(population[0]):
            answer = population[0]

        population = population[:_POPULATION_SIZE]  # Отбор

    return answer


def _crossover(first: list[sp.Point], second: list[sp.Point]) -> list[sp.Point]:
    """Скрестить 2 хромосомы"""

    crossover_point = len(second) // 2
    crossover_part = first[crossover_point:]
    crossover_part_hashed = set(crossover_part)
    new_chromosome = [gene for gene in second if gene not in crossover_part_hashed]
    new_chromosome.extend(crossover_part)
    return new_chromosome


def _mutation(chromosome: list[sp.Point]) -> list[sp.Point]:
    """Провести мутацию в хромосоме"""

    mutation_part_length = random.randint(1, len(chromosome) - 1)
    start = random.randint(0, len(chromosome) - mutation_part_length)
    end = start + mutation_part_length
    return chromosome[start:end] + chromosome[:start] + chromosome[end:]


def _estimation(chromosome: list[sp.Point]) -> float:
    """Получить оценку хромосомы - подсчитать длину маршрута"""

    return sum([chromosome[i - 1].get_distance_to(chromosome[i]) for i in range(len(chromosome))])
