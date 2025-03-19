import numpy as np
from scipy.spatial import distance
from statistics import mean
from typing import List

from ga4qc.circuit import Circuit, state_vector_to_dist, remove_ancillas
from ga4qc.circuit.gates import IGate, Identity
from .interface import IFitness
from ga4qc.params import GAParams


class SpectorFitness(IFitness):
    """Computes the fitness function presented in 
    Spector, Lee, et al. "Genetic programming for quantum computers." 
    Genetic Programming (1998): 365-373.
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
                    state_vector_to_dist(
                        state_vector), self.ga_params.ancillary_qubit_num
                )
                for state_vector in circuit.state_vectors
            ]

            # Case: the circuit does not make use of an oracle it could
            # be using.
            if len(circuit_dists) == 1 and len(self.target_dists) > 1:
                for _ in range(len(self.target_dists) - len(circuit_dists)):
                    circuit_dists.append(circuit_dists[0])

            hits: int = len(self.target_dists)
            errors: List[float] = []

            for i, (state_distribution, target_distribution) in enumerate(
                zip(circuit_dists, self.target_dists)
            ):
                assert len(state_distribution) == len(
                    target_distribution
                ), f"Missmatch between produced distribution (len {len(state_distribution)}) and target distribution (len {len(target_distribution)})"

                match_index, = np.where(np.isclose(target_distribution, 1.0))
                assert (
                    match_index != -1
                ), f"Check the formatting of your target distributions. A 1 is missing in the {i + 1}. distribution."

                probability = state_distribution[match_index]
                if probability >= 0.52:
                    hits -= 1
                else:
                    error = distance.jensenshannon(
                        state_distribution, target_distribution)
                    errors.append(error)

            if len(errors) > 0:
                fitness_score = hits + sum(errors) / max(hits, 1)
                circuit.fitness_values.append(fitness_score)

            else:
                fitness_score = len(circuit.gates) / 100000
                circuit.fitness_values.append(fitness_score)
