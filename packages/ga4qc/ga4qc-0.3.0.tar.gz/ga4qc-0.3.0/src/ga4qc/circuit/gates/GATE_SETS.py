from .interfaces import IGate
from .single_qubit import H, S, Identity, T
from .controlled import CX

CLIFFORD = [H, S, CX]
CLIFFORD_PLUS_T = [H, S, CX, T]
