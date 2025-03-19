import random
from typing import List

from .interface import IMutation
from ga4qc.circuit import Circuit
from ga4qc.circuit.gates import IOptimizableGate


class ParameterChangeMutation(IMutation):

    prob: float
    gate_prob: float

    mean: float
    stdev: float

    def __init__(
        self, circ_prob: float, gate_prob: float, mean: float = 0, stdev: float = 0.1
    ):
        self.prob = circ_prob
        self.gate_prob = gate_prob

        self.mean = mean
        self.stdev = stdev

    def mutate(self, circuit: Circuit, generation: int) -> None:
        for i, gate in enumerate(circuit.gates):

            if not issubclass(gate.__class__, IOptimizableGate):
                continue

            if random.random() < self.gate_prob:
                params: List[float] = gate.params

                for i, param in enumerate(params):
                    params[i] += random.gauss(mu=self.mean, sigma=self.stdev)

                gate.set_params(params)
