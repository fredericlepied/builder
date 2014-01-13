builder
=======

builder is a python module to build Makefile like scripts in Python.

Here is an example called example.py::

  #!/usr/bin/env python
  
  from builder import process_targets, rule, run, init_vars, touch
  
  VERSION = '1'
  
  init_vars()
  
  rule('version', run('@echo', VERSION))
  rule('all', None, 'req', 'target')
  rule('target', touch(), 'req')
  rule('req', touch())
  rule('fail', run('false'))
  rule('env', run('env'))
  rule('clean', run('-rm -f target req'))
  
  process_targets()

There are 2 parts in all such scripts:

1. the definition of variables closed by the ``init_vars()`` call.
2. the definition of rules for building targets closed by the ``process_targets()`` call.

You can then call the script like this::

  $ python example.py version VERSION=12
  12

giving the ``version`` target you want to satisfy after the script
name and overload the variable ``VERSION`` to 12.

``rule`` function takes 2 mandatory arguments:

1. the name of the  target.
2. the function returning the function to build the target. The
   returned function take 2 arguments: the target name and the list of
   dependencies. Predefined functions are available to simplify
   development:

   * ``run`` execute the given command.
   * ``touch`` create the files given in argument or the target if no
     argument is given. If the files already exist, the modification
     time is updated to the current time.

The remaining optional arguments are the target dependencies.

.. Local variables:
.. mode: rst
.. End:
