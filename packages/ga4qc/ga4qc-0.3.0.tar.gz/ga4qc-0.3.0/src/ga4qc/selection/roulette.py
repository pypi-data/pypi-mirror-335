from random import random
from typing import List

from ga4qc.circuit import Circuit
from .interface import ISelection


class RouletteWheelSelection(ISelection):
    objective_i: int

    def __init__(self, objective_i: int = 0):
        self.objective_i = objective_i

    def select(self, circuits: List[Circuit], k: int, generation: int) -> List[Circuit]:
        sorted_circuits = sorted(
            circuits, key=lambda circuit: circuit.fitness_values[self.objective_i], reverse=True
        )

        scores = [circuit.fitness_values[self.objective_i]
                  for circuit in sorted_circuits]

        assert min(
            scores) >= 0, "Roulette wheel selection only works on non-negative fitness values!"
        assert max(
            scores) > 0, "Roulette wheel selection does not work if all fitness values are 0!"

        score_sum = sum(scores)

        selection = []
        for _ in range(k):
            roulette_value = random() * score_sum

            encountered_sum = 0
            for circuit in sorted_circuits:
                encountered_sum += circuit.fitness_values[self.objective_i]

                if encountered_sum >= roulette_value:
                    selection.append(circuit)
                    break

        return selection
