Configuration
=============

SpotterBase uses the `ConfigArgParse <https://pypi.org/project/ConfigArgParse/>`
library for managing the configuration.
It basically allows to load command line parameters from a configuration file.
The code for the configuration management is in
:mod:`spotterbase.config_loader`.

Introduction
------------

Let us create a simple example script to see the configuration
options in action:

.. code:: python

    import spotterbase.config_loader as config_loader

    greeting = config_loader.ConfigString('--greeting',
            description='the greeting', default='hi')
    config_loader.auto()
    print(f'Your greeting is {greeting.value}')

Let us try it out:

.. code::

    $ python3 greeting.py
    Your greeting is hi
    $ python3 greeting.py --greating hello
    Your greeting is hello

We can also create a configuration file ``greeting.config`` with the following content:

.. code::

    greeting='good morning'

and then use it with

.. code::

    $ python3 greeting.py --config greeting.config
    Your greeting is good morning

The config loader automatically looks for configuration files
with the name ``spotterbase.conf`` or ``.spotterbase.conf`` in
the current working directory and in the home directory.

If you import a SpotterBase library, it can automatically
add configuration parameters.
For example, if you import :mod:`spotterbase.data.zipfilecache` in the
beginning of the example script and run ``python3 greeting.py --help``,
you will see an option for specifying how many zip files can be opened simultaneously.

