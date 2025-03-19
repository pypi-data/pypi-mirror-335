import random
from typing import List, Type

from .interface import IMutation
from ga4qc.circuit import Circuit, IGate, random_gate
from ga4qc.params import GAParams


class RandomGateMutation(IMutation):

    prob: float
    gate_prob: float

    ga_params: GAParams

    def __init__(
        self,
        params: GAParams,
        circ_prob: float = 1.0,
        gate_prob: float = 0.1,
    ):
        self.ga_params = params

        self.prob = circ_prob
        self.gate_prob = gate_prob

    def mutate(self, circuit: Circuit, generation: int) -> None:
        for i, gate in enumerate(circuit.gates):
            if random.random() < self.gate_prob:
                circuit.gates[i] = random_gate(
                    self.ga_params.gate_set, self.ga_params.qubit_num)
