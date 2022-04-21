from typing import Tuple, Any, Dict, Literal

from pydcop.algorithms import ComputationDef, AlgoParameterDef
from pydcop.computations_graph.constraints_hypergraph import VariableComputationNode
from pydcop.computations_graph.objects import Link
from pydcop.dcop.relations import assignment_cost
from pydcop.infrastructure.computations import message_type, VariableComputation, register, SynchronousComputationMixin
# Type of computation graph that must be used with kopt
from pydcop.utils.various import number_translator

GRAPH_TYPE = 'constraints_hypergraph'
HEADER_SIZE = 0
UNIT_SIZE = 1

KOPTValueMessage = message_type("kopt_value", ["value"])


def compare_kvm(self: KOPTValueMessage, other) -> bool:
    if type(other) != KOPTValueMessage:
        return False
    if self.value == other.value:
        return True
    return False


KOPTValueMessage.__eq__ = compare_kvm

algo_params = [
    AlgoParameterDef("stop_cycle", "int", None, 0),
]


# Computation Nodes
class KoptComputation(SynchronousComputationMixin, VariableComputation):
    r"""
    Attributes
    """
    mode: Literal['min', 'max']

    @property
    def name(self) -> str:
        return self.variable.name

    current_cycle_assign: Dict[str, Any]
    """Dict representation of the current cycle's assignment to this node's neighbors"""

    next_cycle_assign: Dict[str, Any]
    """Dict representation of the next cycle's assignment to this node's neighbors"""

    def __init__(self, comp_def: ComputationDef):
        # Always call the super class constructor !
        super().__init__(comp_def.node.variable,
                         comp_def)

        assert (comp_def.algo.mode == "min") or (comp_def.algo.mode == "max")

        self.mode = comp_def.algo.mode
        self.stop_cycle = comp_def.algo.param_value("stop_cycle")

        # Constraints involving this variable are available on the
        # ComputationNode:
        self.constraints = comp_def.node.constraints

        # The assignment of our neighbors for the current and next cycle
        self.current_cycle_assign = {}
        self.next_cycle_assign = {}

    def on_start(self):
        # This picks a random value form the domain of the variable
        self.random_value_selection()

        # The currently selected value is available through self.current_value.
        self.post_to_all_neighbors(KOPTValueMessage(number_translator(self.current_value)))
        self.evaluate_cycle()  # Defined later

    @register("kopt_value")
    def on_value_msg(self, variable_name, recv_msg, t):

        raise NotImplementedError("Need to write the message-handler")

        if variable_name not in self.current_cycle_assign:
            self.current_cycle_assign[variable_name] = recv_msg.value
            if self.is_cycle_complete():
                self.evaluate_cycle()

        else:  # The message for the next cycle
            self.next_cycle_assign[variable_name] = recv_msg.value

    def evaluate_cycle(self):

        # self.current_cycle[self.variable.name] = self.current_value
        # current_cost = assignment_cost(self.current_cycle, self.constraints)
        # arg_min, min_cost = self.compute_best_value()
        #
        # if current_cost - min_cost > 0 and 0.5 > random.random():
        #     # Select a new value
        #     self.value_selection(arg_min)

        self.current_cycle_assign, self.next_cycle_assign = self.next_cycle_assign, {}
        self.post_to_all_neighbors(KOPTValueMessage(self.current_value))

    # FIXME: This might be breaking the function of the synchronous algorithm. *Something*
    # is keeping the system from bumping the cycle number.
    def is_cycle_complete(self):
        # The cycle is complete if we received a value from all the neighbors:
        return len(self.current_cycle_assign) == len(self.neighbors)

    def compute_best_value(self) -> Tuple[Any, float]:
        return 0, 0.0

        # compute the best possible value and associated cost
        arg_min, min_cost = None, float('inf')
        for value in self.variable.domain:
            self.current_cycle_assign[self.variable.name] = value
            cost = assignment_cost(self.current_cycle_assign, self.constraints)
            if cost < min_cost:
                min_cost, arg_min = cost, value
        return arg_min, min_cost


def communication_load(_src: VariableComputationNode, _target: str):
    # FIXME: placeholder, since we are not concerned with actual distribution RN
    return 0


def computation_memory(computation: VariableComputationNode) -> float:
    """Return the memory footprint of a DSA computation.

    Notes
    -----
    With KOPT, a computation must only remember the current value for each
    of its neighbors.

    Parameters
    ----------
    computation: VariableComputationNode
        a computation in the hyper-graph computation graph

    Returns
    -------
    float:
        the memory footprint of the computation.

    """
    neighbors = set(
        (n for l in computation.links for n in l.nodes if n not in computation.name)
    )
    return len(neighbors) * UNIT_SIZE
