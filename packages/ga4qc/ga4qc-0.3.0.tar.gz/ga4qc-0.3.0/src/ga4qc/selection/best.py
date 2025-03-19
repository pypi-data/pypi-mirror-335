from random import choice
from typing import List

from ga4qc.circuit import Circuit
from .interface import ISelection


class BestSelection(ISelection):
    objective_i: int

    def __init__(self, objective_i: int = 0):
        self.objective_i = objective_i

    def select(self, circuits: List[Circuit], k: int, generation: int) -> List[Circuit]:
        sorted_circuits = sorted(
            circuits, key=lambda circuit: circuit.fitness_values[self.objective_i]
        )

        selection = [circuit.copy() for circuit in sorted_circuits[:k]]
        return selection
