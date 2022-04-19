from typing import Tuple, Any, Dict

from numpy import random

from pydcop.algorithms import ComputationDef
from pydcop.dcop.relations import assignment_cost, find_optimal
from pydcop.infrastructure.computations import message_type, VariableComputation, register, SynchronousComputationMixin

# Type of computation graph that must be used with kopt
GRAPH_TYPE = 'constraints_hypergraph'

KOPTValueMessage = message_type("kopt_value", ["value"])


# Computation Nodes
class KoptComputation(SynchronousComputationMixin, VariableComputation):
    r"""
    Attributes
    """

    current_cycle_assign: Dict[str, Any]
    """Dict representation of the current cycle's assignment to this node's neighbors"""

    next_cycle_assign: Dict[str, Any]
    """Dict representation of the next cycle's assignment to this node's neighbors"""

    def __init__(self, computation_definition: ComputationDef):
        # Always call the super class constructor !
        super().__init__(computation_definition.node.variable,
                         computation_definition)

        # Constraints involving this variable are available on the
        # ComputationNode:
        self.constraints = computation_definition.node.constraints

        # The assignment of our neighbors for the current and next cycle
        self.current_cycle_assign = {}
        self.next_cycle_assign = {}

    def on_start(self):
        # This picks a random value form the domain of the variable
        self.random_value_selection()

        # The currently selected value is available through self.current_value.
        self.post_to_all_neighbors(KOPTValueMessage(self.current_value))
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
