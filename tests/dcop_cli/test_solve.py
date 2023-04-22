# BSD-3-Clause License
#
# Copyright 2017 Orange
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


import json
import os.path
import unittest
from subprocess import STDOUT, check_output, CalledProcessError
from typing import Optional, List

from tests.dcop_cli.utils import instance_path, dcop_invoke_path

from logging.config import fileConfig

fileConfig(os.path.join(os.path.dirname(__file__), '../../kopt_logging.conf'))


class SimpleSecpDCOP1(unittest.TestCase):

    def check_results(self, results):
        # No convergence detection for now, always stop on timeout
        self.assertEqual(results['status'], 'TIMEOUT')
        assignment = results['assignment']
        self.assertEqual(assignment['l1'], 0)
        self.assertEqual(assignment['l2'], 3)
        self.assertEqual(assignment['l3'], 4)
        self.assertEqual(assignment['m1'], 3)

    def test_maxsum_ilp_fgdp(self):
        result = run_solve('maxsum', 'ilp_fgdp', 'secp_simple1.yaml', 5)
        print(result)
        self.check_results(result)

    def test_maxsum_ilp_fgdp_process(self):
        result = run_solve('maxsum', 'ilp_fgdp', 'secp_simple1.yaml', 5,
                           'process')
        self.check_results(result)

    def test_maxsum_adhoc(self):
        result = run_solve('maxsum', 'adhoc', 'secp_simple1.yaml', 5)
        self.check_results(result)

    def test_maxsum_adhoc_process(self):
        result = run_solve('maxsum', 'adhoc', 'secp_simple1.yaml', 5,
                           'process')
        self.check_results(result)

    def test_maxsum_oneagent(self):
        # Must fail : there is not enough agent for the oneagent
        # distribution method.
        self.assertRaises(CalledProcessError, run_solve,
                          'maxsum', 'oneagent', 'secp_simple1.yaml', 5)

    @unittest.skip
    # Skip the test, adhoc requires an algorithm with computation footprint
    # and dcop does not have it
    def test_dpop_adhoc(self):
        result = run_solve('dpop', 'adhoc', 'secp_simple1.yaml', 5)
        self.check_results(result)

    @unittest.skip
    # Skip the test, adhoc requires an algorithm with computation footprint
    # and dcop does not have it
    def test_dpop_adhoc_process(self):
        result = run_solve('dpop', 'adhoc', 'secp_simple1.yaml', 5, 'process')
        self.check_results(result)

    def test_dsa_adhoc(self):
        result = run_solve('dsa', 'adhoc', 'secp_simple1.yaml', 5)
        # Do not really check the results, dsa performs poorly on this pb
        # self.check_results(result)

    def test_dsa_adhoc_process(self):
        result = run_solve('dsa', 'adhoc', 'secp_simple1.yaml', 5, 'process')
        # Do not really check the results, dsa performs poorly on this pb
        # self.check_results(result)


class GraphColoring1(unittest.TestCase):

    def check_results(self, results, status='TIMEOUT'):
        # No convergence detection for now, always stop on timeout
        self.assertEqual(results['status'], status)
        assignment = results['assignment']
        self.assertEqual(assignment['v1'], 'R')
        self.assertEqual(assignment['v2'], 'G')
        self.assertEqual(assignment['v3'], 'R')

    def test_maxsum_ilp_fgdp(self):
        result = run_solve('maxsum', 'ilp_fgdp', 'graph_coloring1.yaml', 5)
        self.check_results(result)

    def test_maxsum_adhoc(self):
        result = run_solve('maxsum', 'adhoc', 'graph_coloring1.yaml', 1)
        self.check_results(result)

    def test_maxsum_adhoc_process(self):
        result = run_solve('maxsum', 'adhoc', 'graph_coloring1.yaml', 3,
                           'process')
        self.check_results(result)

    def test_maxsum_oneagent(self):
        result = run_solve('maxsum', 'oneagent', 'graph_coloring1.yaml', 1)
        self.check_results(result)

    def test_maxsum_oneagent_process(self):
        result = run_solve('maxsum', 'oneagent', 'graph_coloring1.yaml', 3,
                           'process')
        self.check_results(result)

    @unittest.skip
    # Skip the test, adhoc requires an algorithm with computation footprint
    # and dcop does not have it
    def test_dpop_adhoc(self):
        result = run_solve('dpop', 'adhoc', 'graph_coloring1.yaml', 1)
        self.check_results(result)

    @unittest.skip
    # Skip the test, adhoc requires an algorithm with computation footprint
    # and dcop does not have it
    def test_dpop_adhoc_process(self):
        result = run_solve('dpop', 'adhoc', 'graph_coloring1.yaml', 3,
                           'process')
        self.check_results(result)

    def test_dpop_oneagent(self):
        result = run_solve('dpop', 'oneagent', 'graph_coloring1.yaml', 2)
        self.check_results(result, 'FINISHED')

    def test_dpop_oneagent_process(self):
        result = run_solve('dpop', 'oneagent', 'graph_coloring1.yaml', 3,
                           'process')
        self.check_results(result, 'FINISHED')

    def test_dpop_ilp_fgdp(self):
        # ILP-FGDP does not work for dpop, it should return an error
        self.assertRaises(CalledProcessError, run_solve,
                          'dpop', 'ilp_fgdp', 'graph_coloring1.yaml', 1)

    def test_dsa_adhoc(self):
        result = run_solve('dsa', 'adhoc', 'graph_coloring1.yaml', 1)
        # Do not really check the results, dsa often don't find the best
        # solution this pb
        # self.check_results(result)

    def test_dsa_adhoc_process(self):
        result = run_solve('dsa', 'adhoc', 'graph_coloring1.yaml', 3,
                           'process')
        # Do not really check the results, dsa often don't find the best
        # solution this pb
        # self.check_results(result)

    def test_dsa_oneagent(self):
        result = run_solve('dsa', 'oneagent', 'graph_coloring1.yaml', 1)
        # Do not really check the results, dsa often don't find the best
        # solution this pb
        # self.check_results(result)

    def test_dsa_oneagent_process(self):
        result = run_solve('dsa', 'oneagent', 'graph_coloring1.yaml', 3,
                           'process')
        # Do not really check the results, dsa often don't find the best
        # solution this pb
        # self.check_results(result)

    def test_dsa_ilp_fgdp(self):
        # ILP-FGDP does not work for dsa, it should return an error
        self.assertRaises(CalledProcessError, run_solve,
                          'dsa', 'ilp_fgdp', 'graph_coloring1.yaml', 1)


class GraphColoring10(unittest.TestCase):

    def check_results(self, results):
        # No convergence detection for now, always stop on timeout
        self.assertEqual(results['status'], 'TIMEOUT')
        assignment = results['assignment']
        self.assertEqual(results['cost'], 0)

    def test_mgm_adhoc(self):
        result = run_solve('mgm', 'adhoc', 'graph_coloring_10_4_15_0.1.yml', 2)
        self.check_results(result)

    def test_dpop_oneagent(self):
        results = run_solve('dpop', 'oneagent', 'graph_coloring_10_4_15_0.1.yml', 3)
        self.assertEqual(results['status'], 'FINISHED')

        assignment = results['assignment']
        self.assertEqual(results['cost'], 0)


class GraphColoringCsp(unittest.TestCase):

    def check_results(self, results):
        # No convergence detection for now, always stop on timeout
        self.assertEqual(results['status'], 'FINISHED')
        assignment = results['assignment']
        self.assertEqual(results['cost'], 0)

    def test_dba_adhoc(self):
        result = run_solve('dba', 'adhoc', 'graph_coloring_csp.yaml', 3)
        self.check_results(result)

    def test_dba_adhoc_process(self):
        result = run_solve('dba', 'adhoc', 'graph_coloring_csp.yaml', 3,
                           'process')
        self.check_results(result)

    def test_dba_oneagent(self):
        result = run_solve('dba', 'oneagent', 'graph_coloring_csp.yaml', 3)
        self.check_results(result)

    def test_dba_oneagent_params(self):
        result = run_solve('dba', 'oneagent', 'graph_coloring_csp.yaml', 3,
                           algo_params=['infinity:10000', 'max_distance:3'])
        self.check_results(result)

    def test_dba_oneagent_params_process(self):
        result = run_solve('dba', 'oneagent', 'graph_coloring_csp.yaml', 4,
                           algo_params=['infinity:10000', 'max_distance:3'],
                           mode='process')
        self.check_results(result)


def run_solve(algo, distribution, filename, timeout: int, mode='thread',
              algo_params: Optional[List[str]] = None):
    filename = instance_path(filename)
    param_str = ''
    if algo_params is None:
        algo_params = []
    for p in algo_params:
        param_str += ' --algo_param ' + p
    cmd = f'{dcop_invoke_path()} pydcop -v 0 -t {timeout} solve -a {algo} {param_str} -d ' \
          f'{distribution} ' \
          f'-m {mode} ' \
          f'{filename}'
    extra = 4 if mode == 'thread' else 5
    print("Running command ", cmd)
    try:
        output = check_output(cmd, stderr=STDOUT, timeout=timeout + extra, shell=True)
    except CalledProcessError as e:
        print(f'Command {cmd} raised CalledProcessError {e.output}')
        raise e from e
    print(f'Output of {cmd} is {output}')
    res = {}
    try:
        res = json.loads(output.decode(encoding='utf-8'))
    except Exception as e:
        print(e)
        # don't swallow errors
        raise e from e
    return res
