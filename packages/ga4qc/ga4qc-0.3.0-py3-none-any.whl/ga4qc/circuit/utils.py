import math
import numpy as np
from random import choice
from typing import List, Tuple, Union, Type
import warnings

from ga4qc.circuit import Circuit
from ga4qc.circuit.gates import IOptimizableGate, IGate


def extract_params(circuit: Circuit) -> List[float]:
    params = []
    for gate in circuit.gates:
        if issubclass(gate.__class__, IOptimizableGate):
            params.extend(gate.params)

    return params


def update_params(circuit: Circuit, params: List[float]) -> None:
    for gate in circuit.gates:
        if issubclass(gate.__class__, IOptimizableGate):
            param_count = len(gate.params)

            gate_params, params = (params[:param_count], params[param_count:])
            gate.set_params(gate_params)


def state_vector_to_dist(state: np.ndarray) -> np.ndarray:
    conjugate = state.conjugate()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Ignore "np.complex128Warning: Casting np.complex128 values to real discards the imaginary part"
        # since that is precisely what we want.
        return np.multiply(state, conjugate).astype(np.float64)


def random_gate(gate_types: Type[IGate], qubit_num: int) -> IGate:
    GateType = choice(gate_types)
    gate = GateType().randomize(qubit_num)
    return gate


def random_circuit(gate_types: Type[IGate], gate_count: int, qubit_num: int) -> Circuit:
    gates = []

    for _ in range(gate_count):
        gate = random_gate(gate_types, qubit_num)
        gates.append(gate)

    circuit = Circuit(gates, qubit_num)
    return circuit


def remove_ancillas(measurement_state: np.ndarray, ancillary_qubit_num: int) -> np.ndarray:
    if ancillary_qubit_num == 0:
        return measurement_state

    total_qubit_num = int(math.log(len(measurement_state), 2))

    measurement_qubit_num = total_qubit_num - ancillary_qubit_num

    aggregated_distribution: List[float] = []
    for _ in range(2**measurement_qubit_num):
        aggregated_distribution.append(0.0)

    for i in range(2**measurement_qubit_num):
        for j in range(2**ancillary_qubit_num):
            aggregated_distribution[i] += measurement_state[i * 2**ancillary_qubit_num + j]

    return np.array(aggregated_distribution, dtype=measurement_state.dtype)
