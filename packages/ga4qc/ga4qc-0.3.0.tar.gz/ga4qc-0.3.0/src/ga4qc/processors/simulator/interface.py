from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit
from ga4qc.processors.interface import ICircuitProcessor


class ISimulator(ICircuitProcessor):
    """Base class for all simulators.

    Wrapps the simulation of a population of
    circuits alongside everything that comes with
    it, including the translation from GA4QC gates
    to simulator gates."""

    @abstractmethod
    def process(self, circuits: List[Circuit], generation: int) -> None: ...
