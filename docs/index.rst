.. pydcop documentation master file, created by
   sphinx-quickstart on Thu Jun 22 12:21:25 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyDCOP: DCOP solver in python
==================================


Overview
--------

pyDCOP is a library and command line application for **Distributed Constraint
Optimization Problems** (DCOP).

A Distributed Constraint Optimization Problem is traditionally represented as
a tuple 
:math:`\langle \mathcal{A}, \mathcal{X}, \mathcal{D}, \mathcal{C}, \mu \rangle`
, where:

* :math:`\mathcal{A} = \{a_1,\ldots,a_{|A|}\}` is a set of agents; 
* :math:`\mathcal{X} = \{x_1,\ldots, x_n\}` are variables owned by the agents;
* :math:`\mathcal{D} = \{\mathcal{D}_{x_1},\ldots,\mathcal{D}_{x_n}\}` is a set of finite
  domains, such that variable :math:`x_i` takes values in :math:`\mathcal{D}_{x_i} = \{v_1,\ldots, v_k\}`;
* :math:`\mathcal{C} = \{c_1,\ldots,c_m\}` is a set of soft constraints, where each :math:`c_i`
  defines a cost :math:`\in \mathbb{R} \cup \{\infty\}` for each combination of assignments to a
  subset of variables (a constraint is initially known only to the agents involved);
* :math:`\mu: \mathcal{X} \rightarrow \mathcal{A}` is a function mapping variables to their associated agent.


A *solution* to the DCOP is an assignment to all variables that minimizes 
the overall sum of costs.


pyDCOP has already been used for several scientific papers.


Features
--------

- pyDCOP provides implementations of many classic DCOP algorithms
  (DSA, MGM, MaxSum, DPOP, etc.).
- pyDCOP allows you to implement our own DCOP algorithm easily, by providing
  all the required infrastructure: agents, messaging system,
  metrics collection, etc.
- Agents can run on the same computer or on different machines, making real
  distributed experiments easy.
- Multi-platform : pyDCOP can run on windows, Mac and Linux.
- pyDCOP is especially suited for the IoT use-case and can run
  agents on single-board computers like the Raspberry Pi.
- In addition to classical DCOP algorithms, pyDCOP also provides novel approaches
  for using DCOP in IoT systems: several strategies are available to distribute
  DCOP computations on agents and achieve resilience.




Documentation
-------------

.. toctree::
   :maxdepth: 1

   installation
   tutorials
   usage
   implementation
   algorithms
   zbibliography


Contributing
------------

We welcome contributions, especially the implementation of DCOP algorithms
(novel or well-known). Join us on  
`GitHub <https://github.com/rpgoldman/pyDcop>`_.

Licence 
-------

pyDCOP is licensed under the BSD-3-clause license.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

