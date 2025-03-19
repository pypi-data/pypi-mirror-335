from random import randint
from typing import List

from ga4qc.circuit import Circuit
from .interface import ICrossover


class OnePointCrossover(ICrossover):

    prob: float

    def __init__(self, prob: float = 1.0):
        self.prob = prob

    def cross(self, circuit1: Circuit, circuit2: Circuit, generation: int) -> None:
        max_position = min(len(circuit1), len(circuit2))
        crx_idx = randint(1, max_position - 1)

        circuit1.gates[crx_idx:], circuit2.gates[crx_idx:] = (
            circuit2.gates[crx_idx:],
            circuit1.gates[crx_idx:],
        )
