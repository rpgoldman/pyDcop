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

# from StackOverflow
def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt')
test_deps = parse_requirements('test-requirements.txt')
doc_deps = parse_requirements('doc-requirements.txt')


# Basic dependencies, required to run pyDCOP:
deps = [
        'pulp==2.0',
        'numpy',
        'networkx',
        'pyyaml==5.4.1',
        'requests',
        'websocket-server',
        'tqdm',
    ]


# Required to install dev dependencies with pip
#    pip install -e .[test]
extras = {
    'test': test_deps,
    'doc': doc_deps
}


from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'pydcop', 'version.py'), encoding='utf-8') as f:
    exec(f.read())

setup(
    name='pydcop',
    version=__version__,
    description='Several dcop algo implementation',

    long_description=long_description,
    long_description_content_type='text/markdown', 

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",

        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",    

        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    author='Pierre Rust (Orange)',
    author_email='pierre.rust@orange.com',

    keywords=['dcop', 'MAS'],

    install_requires=install_reqs,
    tests_require=test_deps,
    extras_require=extras,

    scripts=[
        'pydcop/pydcop',
        'pydcop/dcop_cli.py'
    ],

    packages =find_packages(),

    project_urls={
        'Documentation':  'http://pydcop.readthedocs.io',
        'Source': 'https://github.com/Orange-OpenSource/pyDcop',
        'Bug Reports': 'https://github.com/Orange-OpenSource/pyDcop/issues'
    }    
)
