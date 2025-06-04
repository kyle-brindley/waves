#########
|project|
#########

********
Synopsis
********

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :nosubcommands:

***********
Description
***********

.. include:: project_brief.txt

*********************
|PROJECT| Subcommands
*********************
****
docs
****

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: docs

.. _waves_fetch_cli:

*********************
|PROJECT| Subcommands
*********************
*****
fetch
*****

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: fetch

.. _waves_visualize_cli:

*********************
|PROJECT| Subcommands
*********************
*********
visualize
*********

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: visualize

.. _waves_build_cli:

*********************
|PROJECT| Subcommands
*********************
*****
build
*****

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: build

.. _waves_cartesian_product_cli:

*********************
|PROJECT| Subcommands
*********************
*****************
cartesian_product
*****************

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: cartesian_product

.. _waves_custom_study_cli:

*********************
|PROJECT| Subcommands
*********************
************
custom_study
************

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: custom_study

.. _waves_latin_hypercube_cli:

*********************
|PROJECT| Subcommands
*********************
***************
latin_hypercube
***************

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: latin_hypercube

.. _waves_sobol_sequence_cli:

*********************
|PROJECT| Subcommands
*********************
**************
sobol_sequence
**************

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: sobol_sequence

.. _waves_one_at_a_time_cli:

*********************
|PROJECT| Subcommands
*********************
*************
one_at_a_time
*************

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: one_at_a_time

.. _waves_print_study_cli:

*********************
|PROJECT| Subcommands
*********************
***********
print_study
***********

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: print_study

.. _qoi_cli:

*********************
|PROJECT| Subcommands
*********************
***
qoi
***

.. argparse::
   :ref: waves._main.get_parser
   :nodefault:
   :path: qoi

******************
Python Package API
******************
****************
SCons Extensions
****************

.. automodule:: waves.scons_extensions
    :members:
    :show-inheritance:
    :special-members: __call__

******************
Python Package API
******************
********************
Parameter Generators
********************

.. automodule:: waves.parameter_generators
    :members:
    :show-inheritance:

******************
Python Package API
******************
**********
Exceptions
**********

.. automodule:: waves.exceptions
    :members:
    :show-inheritance:

****************
Bundled commands
****************
.. _odb_extract_cli:

***********
ODB Extract
***********

.. argparse::
   :ref: waves._abaqus.odb_extract.get_parser
