from enum import Enum
from typing import Tuple, Any, Dict, Literal, List

from pydcop.algorithms import ComputationDef, AlgoParameterDef
from pydcop.computations_graph.constraints_hypergraph import VariableComputationNode
from pydcop.computations_graph.objects import Link
from pydcop.dcop.relations import assignment_cost
from pydcop.infrastructure.computations import message_type, VariableComputation, register, SynchronousComputationMixin, \
    Message
# Type of computation graph that must be used with kopt
from pydcop.utils.various import number_translator

GRAPH_TYPE = 'constraints_hypergraph'
HEADER_SIZE = 0
UNIT_SIZE = 1


class KOPTValueMessage(Message):
    _value: Any
    """Current value of this variable"""

    def __init__(self, value):
        super().__init__("kopt_value", None)
        # need to avoid sending messages with numpy numerals in it
        self._value = number_translator(value)

    @property
    def value(self):
        return self._value

    @property
    def size(self):
        return 1

    def __str__(self):
        return "KOPTMessage({})".format(self.value)

    def __repr__(self):
        return "KOPTMessage({})".format(self.value)

    def __eq__(self, other):
        if type(other) != KOPTValueMessage:
            return False
        if self.value == other.value:
            return True
        return False


class KOPTNeighborInformation(Message):
    variable_name: str
    """Name of the variable hosted on the sender"""

    domain: List[Any]

    constraints: List[Any]

    def __init__(self, variable_name: str, domain: List[Any], constraints: List[Any]):
        super().__init__("kopt_neighbor_info", None)
        # need to avoid sending messages with numpy numerals in it
        self.variable_name = variable_name
        self.domain = domain
        self.constraints = constraints

    @property
    def size(self):
        return 1

    def __str__(self):
        return "KOPTNeighborInformation({})".format(self.variable_name)

    def __repr__(self):
        return "KOPTNeighborInformation({})".format(self.variable_name)

    def __eq__(self, other):
        if type(other) != KOPTNeighborInformation:
            return False
        if self.variable == other.variable:
            # we assume that the constraints are the same, since we can't
            # effectively check them.
            return True
        return False


algo_params = [
    AlgoParameterDef("stop_cycle", "int", None, 0),
]


class KoptState(Enum):
    SEND_VALUE = "send_value"
    SEND_VARIABLE_INFO = "send_var_info"
    FORM_GROUP = "form_group"


# Computation Nodes
class KoptComputation(SynchronousComputationMixin, VariableComputation):
    r"""
    Attributes
    """
    mode: Literal['min', 'max']
    comp_state: KoptState
    current_cycle_assign: Dict[str, Any]
    """Dict representation of the current cycle's assignment to this node's neighbors"""

    next_cycle_assign: Dict[str, Any]
    """Dict representation of the next cycle's assignment to this node's neighbors"""

    @property
    def name(self) -> str:
        return self.variable.name

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
        self.comp_state = KoptState.SEND_VALUE
        # This picks a random value from the domain of the variable
        self.random_value_selection()

        # The currently selected value is available through self.current_value.
        self.post_to_all_neighbors(KOPTValueMessage(number_translator(self.current_value)))

    def share_constraint_info(self):
        self.comp_state = KoptState.SEND_VARIABLE_INFO
        self.post_to_all_neighbors(KOPTNeighborInformation(self.name, self.variable.domain, self.constraints))

    @register("kopt_neighbor_info")
    def on_neighbor_info_msg(self, variable_name: str, msg: KOPTNeighborInformation, _t: float):
        assert self.comp_state == KoptState.SEND_VARIABLE_INFO
        if variable_name not in self.neighbor_info:
            self.neighbor_info[variable_name] = msg.domain, msg.constraints
        else:
            raise ValueError(f"Got duplicate kopt_neighbor_info message from {variable_name}")
        if self.is_cycle_complete():
            self.form_group()

    def form_group(self):
        raise NotImplementedError("Still need to write code for forming group.")

    @register("kopt_value")
    def on_value_msg(self, variable_name, recv_msg, t):
        assert self.comp_state == KoptState.SEND_VALUE

        if variable_name not in self.current_cycle_assign:
            self.current_cycle_assign[variable_name] = recv_msg.value
            if self.is_cycle_complete():
                self.update_neighbor_values()
                self.share_constraint_info()

        else:  # The message for the next cycle
            raise ValueError("Received unexpected on kopt_value messages.")
            # self.next_cycle_assign[variable_name] = recv_msg.value

    def update_neighbor_values(self):
        r"""
        Update the values stored for the neighbors for cycles.
        """
        self.current_cycle_assign, self.next_cycle_assign = self.next_cycle_assign, {}

    def update_value(self):
        raise NotImplementedError("update_value method should not be invoked.")

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
    """Return the memory footprint of a KOPT computation.

    Notes
    -----
    With KOPT, a computation must only remember the current value for each
    of its neighbors.
    FIXME: this is not true: it must hold also the constraints.

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
