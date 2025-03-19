from abc import ABC, abstractmethod

from statistics import mean, stdev
from typing import List, Callable


from ga4qc.circuit import Circuit
from .interface import ICallback


class FitnessStatsCallback(ICallback, ABC):
    objective_count: int

    def __init__(self, objective_count: int = 1):
        self.objective_count = objective_count

    def __call__(self, circuits: List[Circuit], generation: int) -> None:
        fit_means: List[float] = []
        fit_mins: List[float] = []
        fit_maxs: List[float] = []
        fit_stdevs: List[float] = []

        for obj_i in range(self.objective_count):
            fitness_scores = [circuit.fitness_values[obj_i] for circuit in circuits]

            fit_means.append(mean(fitness_scores))
            fit_mins.append(min(fitness_scores))
            fit_maxs.append(max(fitness_scores))
            fit_stdevs.append(stdev(fitness_scores))

        self.handle(fit_means, fit_mins, fit_maxs, fit_stdevs, generation)

    @abstractmethod
    def handle(
        self,
        fit_means: List[float],
        fit_mins: List[float],
        fit_maxs: List[float],
        fit_stdevs: List[float],
        generation: int = None,
    ) -> None: ...
