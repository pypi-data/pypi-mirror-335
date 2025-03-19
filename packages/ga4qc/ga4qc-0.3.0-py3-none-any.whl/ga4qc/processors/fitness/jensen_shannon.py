import numpy as np
from scipy.spatial import distance
from statistics import mean
from typing import List
import warnings

from ga4qc.circuit import Circuit, state_vector_to_dist, remove_ancillas
from .interface import IFitness
from ga4qc.params import GAParams


class JensenShannonFitness(IFitness):
    """Computes fitness as the jensen shannon distance between
    the effect a circuit has on the |0...0>-state
    and the state distribution it should produce.
    """

    ga_params: GAParams
    target_dists: List[np.ndarray]

    def __init__(self, params: GAParams, target_dists: List[np.ndarray]):
        self.ga_params = params
        self.target_dists = target_dists

    def process(self, circuits: List[Circuit], generation: int) -> None:
        for circuit in circuits:
            assert len(circuit.unitaries) > 0, (
                "The circuit has to be simulated before "
                "a (meaningful) fitness function can be computed. Make sure you call "
                "an instance of the simulator interface before calling any fitness functions."
            )

            circuit_dists = [
                remove_ancillas(
                    state_vector_to_dist(state_vector), self.ga_params.ancillary_qubit_num
                )
                for state_vector in circuit.state_vectors
            ]

            # Case: the circuit does not make use of an oracle it could
            # be using.
            if len(circuit_dists) == 1 and len(self.target_dists) > 1:
                for _ in range(len(self.target_dists) - len(circuit_dists)):
                    circuit_dists.append(circuit_dists[0])

            errors: List[float] = []
            for circuit_dist, target_dist in zip(circuit_dists, self.target_dists):
                assert len(circuit_dist) == len(
                    target_dist
                ), f"Missmatch between produced distribution (len {len(circuit_dist)}) and target distribution (len {len(target_dist)})"

                error = distance.jensenshannon(circuit_dist, target_dist)
                errors.append(error)

            error = mean(errors)

            circuit.fitness_values.append(error)
