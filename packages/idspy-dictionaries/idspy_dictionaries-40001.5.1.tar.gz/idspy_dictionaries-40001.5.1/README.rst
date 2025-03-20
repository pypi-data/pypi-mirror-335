IDSPy_Dictionaries
==================

IMAS Data Dictionaries converted to Python Dataclass used in the  IDSPy suite.

Prerequisites
=============

To use this script, you need to have Python **3.9** or later installed. You can download Python from https://www.python.org/downloads/.
Please note that Python at least **3.10** is recommended.

Installation
============

To install the necessary packages, run the following command:

.. code-block:: console

   python -m pip install idspy_dictionaries

Usage
=====

To load the desired IDS :

.. code-block:: python

   from idspy_dictionaries import ids_gyrokinetics_local # or any other available IDS
   new_ids = ids_gyrokinetics_local.Gyrokinetics()

FAQ
===

**Q:** What is the minimum required version of Python to run this script?
  **A:** The  recommended version of Python is 3.10. It can be used with Python >= 3.9
          but there is no support in that case.

**Q:** Can I add new members to the dataclasses?
  **A:** This option is not possible to be sure that the dataclasses follow the IMAS conventions.

**Q:** Is the package compatible with pydantic and/or attrs?
  **A:** Short answer, no ;)

**Q:** I would really like to use python <3.9 is it really impossible?
  **A:** IDSPy_dictionaries used mainly python dataclasses and the slot property which had been added in python 3.10 only.
         The main reason to use __slots__ is to avoid addition of members in the IDS and remains fully compliant with IMAS.
         A version of the package had been published "as it is" without the slots dependency but need at least python 3.9.
         The way dataclasses are generated with the associated fields, at the opposite, is not compatible at all with python 3.8.


**Q:** Can I load all the dictionaries at once?
  **A:** For performances reasons, it's not possible right now.
