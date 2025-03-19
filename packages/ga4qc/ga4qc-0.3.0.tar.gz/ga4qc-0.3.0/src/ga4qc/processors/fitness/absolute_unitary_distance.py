import numpy as np
from scipy.spatial import distance
from statistics import mean
from typing import List
import warnings

from ga4qc.circuit import Circuit, state_vector_to_dist, remove_ancillas
from .interface import IFitness
from ga4qc.params import GAParams


class AbsoluteUnitaryDistance(IFitness):
    """Computes the absolute derivation between each entry of the target
    and circuit unitaries as used by Williams, Colin P., and Alexander G. Gray. 
    "Automated design of quantum circuits." NASA International Conference on 
    Quantum Computing and Quantum Communications. Berlin, Heidelberg: Springer 
    Berlin Heidelberg, 1998.
    """

    ga_params: GAParams
    target_unitaries: List[np.ndarray]

    def __init__(self, params: GAParams, target_unitaries: List[np.ndarray]):
        self.ga_params = params
        self.target_unitaries = target_unitaries

    def process(self, circuits: List[Circuit], generation: int) -> None:
        for circuit in circuits:
            assert len(circuit.unitaries) > 0, (
                "The circuit has to be simulated before "
                "a (meaningful) fitness function can be computed. Make sure you call "
                "an instance of the simulator interface before calling any fitness functions."
            )

            circuit_unitaries = circuit.unitaries

            # Case: the circuit does not make use of an oracle it could
            # be using.
            if len(circuit_unitaries) == 1 and len(self.target_unitaries) > 1:
                for _ in range(len(self.target_unitaries) - len(circuit_unitaries)):
                    circuit_unitaries.append(circuit_unitaries[0])

            distances: List[float] = []

            for circuit_unitary, target_unitary in zip(circuit_unitaries, self.target_unitaries):
                N = 2 ** self.ga_params.qubit_num

                distance = 0
                for i in range(N):
                    for j in range(N):
                        distance += abs(circuit_unitary[i]
                                        [j] - target_unitary[i][j])

                distances.append(distance)

            mean_distance = mean(distances)
            circuit.fitness_values.append(mean_distance)
