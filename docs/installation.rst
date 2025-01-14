
.. _installation:


Installation
============

PyDCOP runs on python >= 3.6.
We recommend using ``pip`` and installing pyDCOP in a
`python venv <https://docs.python.org/3/library/venv.html>`_::

  python3 -m venv ~/pydcop_env
  source ~/pydcop_env/bin/activate

Then you can simply install using pip::

  git clone https://github.com/Orange-OpenSource/pyDcop.git
  cd pyDcop
  pip install .

When developing on pyDCOP, for example to implement a new DCOP algorithm, one
should instead use the following command, which installs pyDCOP in development
mode with test dependencies::

  pip install -e .[test]

To generate documentation, you need to install the corresponding dependencies::

  pip install -e .[doc]


Additionally, for distributed computation, pyDCOP uses the
`glpk <https://www.gnu.org/software/glpk/>`_ linear program solver, which must
be installed on the system (as it is not a python library, which could be
installed as a dependency by `pip`). For example, on an Ubuntu/Debian system::

  sudo apt-get install glpk-utils

on Mac OS::

  brew install glpk


.. note:: On many linux distributions, ``pip`` is not installed by default. On
  Ubuntu for example, install using::

    sudo apt-get install python3-setuptools
    sudo apt-get install python3-pip


.. note::  When installing pyDCOP over many machines (or virtual machines),
  for a really distributed system, we recommend automating the process.
  We provide an ansible playbook that can help you with this task.
  See the guide :ref:`usage_provisioning`.


.. note:: It is possible that `glpk` could more easily be installed
   using Anaconda. Perhaps an Anaconda wizard could provide a recipe.
