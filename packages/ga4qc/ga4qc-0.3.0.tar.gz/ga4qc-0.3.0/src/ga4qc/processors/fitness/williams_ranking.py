import numpy as np
from typing import List

from ga4qc.circuit import Circuit
from ga4qc.circuit.gates import IGate, Identity
from .interface import IFitness


class WilliamsRankingFitness(IFitness):
    """Applies to a selected objective_i
    the ranking function defined in Williams, Colin P., and Alexander G. Gray. 
    "Automated design of quantum circuits." NASA International Conference on 
    Quantum Computing and Quantum Communications. Berlin, Heidelberg: Springer 
    Berlin Heidelberg, 1998. To replicate the fitness function from the paper, 
    apply the absolute deviation fitness first, then use the ranking scheme 
    presented here.
    """

    objective_i: int

    def __init__(self, objective_i: int = 0):
        self.objective_i = objective_i

    def process(self, circuits: List[Circuit], generation: int) -> None:
        scores = np.array([
            circuit.fitness_values[self.objective_i] for circuit in circuits
        ])
        order = scores.argsort()
        ranks = order.argsort()

        N = len(circuits)
        for circuit, rank in zip(circuits, ranks):
            rank_score = 6 * N / (1 - 3 * N + 2 * N ** 2) * rank ** 2 \
                + 6 / (N - 3 * N ** 2 + 2 * N ** 3) \
                - 12 / (1 - 3 * N + 2 * N ** 2)
            circuit.fitness_values.append(rank_score)
