# BSD-3-Clause License
#
# Copyright 2017 Orange
# Additional code copyright 2022 SIFT, LLC and Robert P. Goldman
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from datetime import datetime
from unittest.mock import MagicMock, call

from pydcop.algorithms import kopt, AlgorithmDef, ComputationDef
from pydcop.algorithms.kopt import KoptComputation, KOPTValueMessage
from pydcop.computations_graph.constraints_hypergraph \
    import VariableComputationNode
from pydcop.dcop.objects import Variable
from pydcop.dcop.relations import UnaryFunctionRelation, \
    AsNAryFunctionRelation, relation_from_str, constraint_from_str
from pydcop.utils.various import number_translator


def test_communication_load():
    v = Variable('v1', list(range(10)))
    var_node = VariableComputationNode(v, [])
    assert 0 == kopt.communication_load(var_node, 'f1')
    # assert kopt.UNIT_SIZE + kopt.HEADER_SIZE == kopt.communication_load(
    #     var_node, 'f1')


def test_computation_memory_one_constraint():
    v1 = Variable('v1', list(range(10)))
    v2 = Variable('v2', list(range(10)))
    v3 = Variable('v3', list(range(10)))
    c1 = constraint_from_str('c1', ' v1 + v2 == v3', [v1, v2, v3])
    v1_node = VariableComputationNode(v1, [c1])

    # here, we have a hyperlink with 3 vertices
    assert kopt.computation_memory(v1_node) == kopt.UNIT_SIZE * 2


def test_computation_memory_two_constraints():
    v1 = Variable('v1', list(range(10)))
    v2 = Variable('v2', list(range(10)))
    v3 = Variable('v3', list(range(10)))
    v4 = Variable('v4', list(range(10)))
    c1 = constraint_from_str('c1', ' v1 == v2', [v1, v2])
    c2 = constraint_from_str('c2', ' v1 == v3', [v1, v3])
    c3 = constraint_from_str('c3', ' v1 == v4', [v1, v4])
    v1_node = VariableComputationNode(v1, [c1, c2, c3])

    # here, we have 3 edges , one for each constraint
    assert kopt.computation_memory(v1_node) == kopt.UNIT_SIZE * 3


def test_footprint_on_computation_object():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])
    c1 = relation_from_str('c1', '0 if v1 == v2 else  1', [v1, v2])
    n1 = VariableComputationNode(v1, [c1])
    _n2 = VariableComputationNode(v2, [c1])
    comp_def = ComputationDef(
        n1, AlgorithmDef.build_with_default_param('kopt', mode='min'))
    c = KoptComputation(comp_def)

    # Must fix unit size otherwise the tests fails when we change the default
    # value
    kopt.UNIT_SIZE = 1

    footprint = c.footprint()
    assert footprint == 1


def test_build_computation_default_params():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    n1 = VariableComputationNode(v1, [])
    comp_def = ComputationDef(
        n1, AlgorithmDef.build_with_default_param('kopt'))
    c = KoptComputation(comp_def)
    assert c.mode == 'min'
    assert c.stop_cycle == 0


def test_build_computation_max_mode():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    n1 = VariableComputationNode(v1, [])
    comp_def = ComputationDef(
        n1, AlgorithmDef.build_with_default_param('kopt', mode='max'))
    c = KoptComputation(comp_def)
    assert c.mode == 'max'


def test_build_computation_with_params():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    n1 = VariableComputationNode(v1, [])
    comp_def = ComputationDef(
        n1, AlgorithmDef.build_with_default_param(
            'kopt', mode='max', params={'stop_cycle': 10}))
    c = KoptComputation(comp_def)
    assert c.mode == 'max'
    assert c.stop_cycle == 10


def test_1_unary_constraint_means_no_neighbors():
    variable = Variable('a', [0, 1, 2, 3, 4])
    c1 = UnaryFunctionRelation('c1', variable, lambda x: abs(x - 2))

    node = VariableComputationNode(variable, [c1])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    assert len(computation.neighbors) == 0


def test_2_unary_constraint_means_no_neighbors():
    variable = Variable('a', [0, 1, 2, 3, 4])
    c1 = UnaryFunctionRelation('c1', variable, lambda x: abs(x - 3))
    c2 = UnaryFunctionRelation('c1', variable, lambda x: abs(x - 1) * 2)

    node = VariableComputationNode(variable, [c1, c2])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    assert len(computation.neighbors) == 0


def test_one_binary_constraint_one_neighbor():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])

    @AsNAryFunctionRelation(v1, v2)
    def c1(v1_, v2_):
        return abs(v1_ - v2_)

    node = VariableComputationNode(v1, [c1])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    assert len(computation.neighbors) == 1


def test_2_binary_constraints_one_neighbor():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])

    @AsNAryFunctionRelation(v1, v2)
    def c1(v1_, v2_):
        return abs(v1_ - v2_)

    @AsNAryFunctionRelation(v1, v2)
    def c2(v1_, v2_):
        return abs(v1_ + v2_)

    node = VariableComputationNode(v1, [c1, c2])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    assert len(computation.neighbors) == 1


def test_3ary_constraint_2_neighbors():
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])
    v3 = Variable('v3', [0, 1, 2, 3, 4])

    @AsNAryFunctionRelation(v1, v2, v3)
    def c1(v1_, v2_, v3_):
        return abs(v1_ - v2_ + v3_)

    node = VariableComputationNode(v1, [c1])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    assert len(computation.neighbors) == 2


################################################################################


def test_select_and_send_random_value_when_starting():
    # When starting, a kopt computation select a random value and send it to
    # all neighbors
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])
    v3 = Variable('v3', [0, 1, 2, 3, 4])

    @AsNAryFunctionRelation(v1, v2, v3)
    def c1(v1_, v2_, v3_):
        return abs(v1_ - v2_ + v3_)

    node = VariableComputationNode(v1, [c1])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    message_sender = MagicMock()
    computation.message_sender = message_sender

    computation.start()

    assert computation.current_value in v1.domain
    expected_message = KOPTValueMessage(number_translator(computation.current_value))
    print(f"\nexpected value message is {expected_message}")
    print("message_sender.mock_calls:")
    for c in message_sender.mock_calls:
        print("\t" + str(c))
    message_sender.assert_has_calls(
        [call('v1', 'v2', expected_message, None, None),
         call('v1', 'v3', expected_message, None, None)],
        any_order=True
    )

def test_terminate_cycle():
    # When starting, a kopt computation select a random value and send it to
    # all neighbors
    v1 = Variable('v1', [0, 1, 2, 3, 4])
    v2 = Variable('v2', [0, 1, 2, 3, 4])
    v3 = Variable('v3', [0, 1, 2, 3, 4])

    @AsNAryFunctionRelation(v1, v2, v3)
    def c1(v1_, v2_, v3_):
        return abs(v1_ - v2_ + v3_)

    node = VariableComputationNode(v1, [c1])
    comp_def = ComputationDef(node,
                              AlgorithmDef.build_with_default_param('kopt'))

    computation = KoptComputation(comp_def=comp_def)
    message_sender = MagicMock()
    computation.message_sender = message_sender
    update_neighbor_values = MagicMock()
    computation.update_neighbor_values = update_neighbor_values
    computation.start()
    computation.on_value_msg('v2', KOPTValueMessage(2), datetime.now().time())
    computation.on_value_msg('v3', KOPTValueMessage(3), datetime.now().time())


    # if the agent receives messages from both its neighbors, its cycle should end
    update_neighbor_values.assert_has_calls([call()])
    assert computation.current_cycle_assign['v2'] == 2
    assert computation.current_cycle_assign['v3'] == 3


################################################################################


def test_str_kopt_class():
    variable = Variable('a', [0, 1, 2, 3, 4])
    c1 = UnaryFunctionRelation('c1', variable, lambda x: abs(x - 2))

    computation = KoptComputation(
        ComputationDef(VariableComputationNode(variable, [c1]),
                       AlgorithmDef.build_with_default_param('kopt')))

    assert str(computation) == "kopt.KoptComputation(a)"


def test_repr_kopt_class():
    variable = Variable('a', [0, 1, 2, 3, 4])
    c1 = UnaryFunctionRelation('c1', variable, lambda x: abs(x - 2))

    computation = KoptComputation(
        ComputationDef(VariableComputationNode(variable, [c1]),
                       AlgorithmDef.build_with_default_param('kopt')))

    assert repr(computation) == "kopt.KoptComputation(a)"
