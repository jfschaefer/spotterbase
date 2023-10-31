Notes for developers/contributors
=================================


Running tests
-------------

You can run the tests with (assuming you are in the root of the spotterbase repository):

.. code-block:: console

   $ python -m spotterbase.test

We also use ``flake8`` and ``mypy`` to check the code for style and type errors:

.. code-block:: console

   $ flake8 spotterbase
   $ mypy spotterbase

Documentation
-------------

You can generate the documentation by running

.. code-block:: console

   $ make html

in the ``doc`` folder. This will likely require installing some additional packages.
You can view the documentation by opening ``doc/build/html/index.html``.
