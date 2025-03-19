from abc import ABC, abstractmethod

from statistics import mean, stdev
from typing import List, Callable


from ga4qc.circuit import Circuit
from .interface import ICallback


class BestCircuitCallback(ICallback, ABC):
    objective_count: int

    def __init__(self, objective_count: int = 1):
        self.objective_count = objective_count

    def __call__(self, circuits: List[Circuit], generation: int) -> None:
        best_circuits: List[Circuit] = []

        for obj_i in range(self.objective_count):
            fitness_scores = [circuit.fitness_values[obj_i] for circuit in circuits]

            best_fit = min(fitness_scores)
            min_idx = fitness_scores.index(best_fit)

            best_circuit = circuits[min_idx]
            best_circuits.append(best_circuit)

        self.handle(best_circuits, generation)

    @abstractmethod
    def handle(
        self,
        circuits: List[Circuit],
        generation: int = None,
    ) -> None: ...
