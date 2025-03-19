import numpy as np
import quasim
from typing import List

from ga4qc.circuit import Circuit
from ga4qc.circuit.gates import (
    IGate,
    Oracle,
    X,
    Y,
    Z,
    H,
    S,
    T,
    RX,
    RY,
    RZ,
    Phase,
    CX,
    CY,
    CZ,
    CH,
    CS,
    CT,
    CRX,
    CRY,
    CRZ,
    CCX,
    CCZ,
    Swap,
    Identity,
)
from .interface import ISimulator


def to_quasim(circuit: Circuit) -> List[quasim.Circuit]:
    quasim_circuits = []

    for case_i in range(circuit.case_count):
        quasim_circuit = quasim.Circuit(circuit.qubit_num)

        for gate in circuit.gates:
            if type(gate) is Oracle:
                for gate_ in gate.get_gates(case_i):
                    quasim_gate = get_quasim_gate(gate_)
                    quasim_circuit.apply(quasim_gate)
            else:
                quasim_gate = get_quasim_gate(gate)
                quasim_circuit.apply(quasim_gate)

        quasim_circuits.append(quasim_circuit)

    return quasim_circuits


def get_quasim_gate(gate: IGate) -> quasim.gates.IGate:
    if type(gate) is X:
        return quasim.gates.X(gate.target)
    elif type(gate) is Y:
        return quasim.gates.Y(gate.target)
    elif type(gate) is Z:
        return quasim.gates.Z(gate.target)
    elif type(gate) is H:
        return quasim.gates.H(gate.target)
    elif type(gate) is S:
        return quasim.gates.S(gate.target)
    elif type(gate) is T:
        return quasim.gates.T(gate.target)
    elif type(gate) is RX:
        return quasim.gates.RX(gate.target, gate.theta)
    elif type(gate) is RY:
        return quasim.gates.RY(gate.target, gate.theta)
    elif type(gate) is RZ:
        return quasim.gates.RZ(gate.target, gate.theta)
    elif type(gate) is Phase:
        return quasim.gates.Phase(gate.target, gate.theta)
    elif type(gate) is CRX:
        return quasim.gates.CRX(gate.controll, gate.target, gate.theta)
    elif type(gate) is CRY:
        return quasim.gates.CRY(gate.controll, gate.target, gate.theta)
    elif type(gate) is CRZ:
        return quasim.gates.CRZ(gate.controll, gate.target, gate.theta)
    elif type(gate) is CX:
        return quasim.gates.CX(gate.controll, gate.target)
    elif type(gate) is CY:
        return quasim.gates.CY(gate.controll, gate.target)
    elif type(gate) is CZ:
        return quasim.gates.CZ(gate.controll, gate.target)
    elif type(gate) is CH:
        return quasim.gates.CH(gate.controll, gate.target)
    elif type(gate) is CS:
        return quasim.gates.CS(gate.controll, gate.target)
    elif type(gate) is CCX:
        return quasim.gates.CCX(gate.controll1, gate.controll2, gate.target)
    elif type(gate) is CCZ:
        return quasim.gates.CCZ(gate.controll1, gate.controll2, gate.target)
    elif type(gate) is Swap:
        return quasim.gates.Swap(gate.target1, gate.target2)
    elif type(gate) is Identity:
        # Workaround since quasim does not have an identity gate
        # as of version 1.0.0
        return quasim.gates.Phase(gate.target, 2 * np.pi)
    else:
        raise NotImplementedError(
            f"The gate of type {type(gate)} does not "
            "have a corresponding mapping in quasim specified."
        )


class QuasimSimulator(ISimulator):

    def process(self, circuits: List[Circuit], generation: int) -> None:
        for circuit in circuits:
            circuit.unitaries = []

            quasim_circuits = to_quasim(circuit)

            for quasim_circuit in quasim_circuits:
                unitary: np.ndarray = quasim.get_unitary(quasim_circuit)
                circuit.unitaries.append(unitary)
