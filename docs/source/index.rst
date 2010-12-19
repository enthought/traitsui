.. CodeTools documentation master file, created by sphinx-quickstart on Tue Jul 22 09:56:01 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the CodeTools documentation!
=======================================

The CodeTools project provide a series of modules for analysis and control of
code execution. The key components are Blocks, sections of code to execute,
and Contexts, dictionary-like objects which are used as namespaces for Block
execution. CodeTools is designed to perform such tasks as:

- executing code in a controlled environment
- performing dependency analysis on code so that expensive recalculations
  can be avoided
- having Traits-aware code listen for changes inside the namespace of
  executing code
- automatically converting or adapting variables on access from, or
  assignment to, a namespace

CodeTools depends upon Traits, with an optional dependency on SciMath and
Numpy for unit support, but has no major dependencies beyond that.

CodeTools is under active development, so the implementation and API are
somewhat fluid.

Contents
--------

.. toctree::
   
   tutorial.rst
   roadmap.rst


