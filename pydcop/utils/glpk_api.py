__all__ = ["glpk_solve"]

from pulp import LpProblem, LpSolver
import pulp
from typing import Optional

# None for OLD API
GLPK_SOLVER: Optional[LpSolver] = None
try:
    # old PuLP interface
    from pulp.solvers import GLPK_CMD

    GLPK_SOLVER = None
except ModuleNotFoundError:
    GLPK_SOLVER = pulp.getSolver('GLPK_CMD', keepFiles=1, msg=False,
                                 options=['--pcost'])


def glpk_solve(pb: LpProblem):
    # Old API
    if GLPK_SOLVER is None:
        return pb.solve(solver=GLPK_CMD(keepFiles=1, msg=False,
                                        options=['--pcost']))
    # New API
    return pb.solve(solver=GLPK_SOLVER)
