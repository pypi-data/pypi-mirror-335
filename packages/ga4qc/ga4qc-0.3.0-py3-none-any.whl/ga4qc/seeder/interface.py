from abc import ABC, abstractmethod
from typing import List

from ga4qc.circuit import Circuit


class ISeeder(ABC):
    """Base class for all population seeding."""

    @abstractmethod
    def seed(self, population_size: int) -> List[Circuit]: ...
