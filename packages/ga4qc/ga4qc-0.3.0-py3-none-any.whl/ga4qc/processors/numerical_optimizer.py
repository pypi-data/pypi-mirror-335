from functools import partial
import numpy as np
from scipy.optimize import minimize, OptimizeResult
from typing import List, Tuple, Union

from ga4qc.circuit import Circuit, update_params, extract_params
from ga4qc.circuit.gates import IOptimizableGate
from .interface import ICircuitProcessor
from .fitness import IFitness
from .simulator import ISimulator


def get_bounds(params: List[float]) -> List[Tuple[float, float]]:
    bounds = []
    for _ in params:
        bounds.append((-np.pi, np.pi))
    return bounds


def evaluate(
    params: List[float], circuit: Circuit, simulator: ISimulator, fitness: IFitness, generation: int
) -> float:
    update_params(circuit, params)
    simulator.process([circuit], generation)
    fitness.process([circuit], generation)
    score = circuit.fitness_values[0]
    return score


class NumericalOptimizer(ICircuitProcessor):
    simulator: ISimulator
    fitness: IFitness
    rounds: int

    def __init__(self, simulator: ISimulator, fitness: IFitness, rounds: int = 10):
        self.simulator = simulator
        self.fitness = fitness
        self.rounds = rounds

    def process(self, circuits: List[Circuit], generation: int) -> None:
        for circuit in circuits:
            initial_params = extract_params(circuit)

            if len(initial_params) == 0:
                self.simulator.process([circuit], generation)
                self.fitness.process([circuit], generation)
                continue

            bounds = get_bounds(initial_params)

            objective_function = partial(
                evaluate,
                circuit=circuit,
                simulator=self.simulator,
                fitness=self.fitness,
                generation=generation
            )

            optimization_result: OptimizeResult = minimize(
                objective_function,
                x0=initial_params,
                method="Nelder-Mead",
                bounds=bounds,
                tol=0,
                options={"maxiter": self.rounds, "disp": False},
            )

            best_params = optimization_result.x
            update_params(circuit, best_params)
