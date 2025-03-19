import numpy as np
from scipy.spatial import distance
from statistics import mean
from typing import List
import warnings

from ga4qc.circuit import Circuit, state_vector_to_dist, remove_ancillas
from ga4qc.circuit.gates import IGate, Identity
from .interface import IFitness


class GateCountFitness(IFitness):

    def __init__(self):
        pass

    def process(self, circuits: List[Circuit], generation: int) -> None:
        for circuit in circuits:
            gate_count = 0

            for gate in circuit.gates:
                if type(gate) is Identity:
                    continue

                gate_count += 1

            circuit.fitness_values.append(gate_count)
