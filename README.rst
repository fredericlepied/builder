builder
=======

.. image:: https://secure.travis-ci.org/fredericlepied/builder.png?branch=master
   :alt: Build Status
   :target: http://travis-ci.org/fredericlepied/builder

.. image:: https://coveralls.io/repos/fredericlepied/builder/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/fredericlepied/builder?branch=master

builder is a python module to build Makefile like scripts in Python.

Here is an example called example.py::

  #!/usr/bin/env python
  
  from builder import end_rules, rule, run, end_vars, touch
  
  VERSION = '1'
  
  end_vars()
  
  rule('version', run('@echo $(VERSION)'))
  rule('all', None, 'req', 'target')
  rule('target', touch(), 'req')
  rule('req', touch())
  rule('fail', run('false'))
  rule('env', run('env'))
  rule('clean', run('-rm -f target req'))
  
  end_rules()

There are 2 parts in all such scripts:

1. the definition of variables closed by the ``end_vars()`` call.
2. the definition of rules for building targets closed by the ``end_rules()`` call.

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

   * ``run`` execute the given command. If the command starts with an
     ``@`` then don't output the command. If the command starts with
     ``-`` then ignore its exit status.
   * ``touch`` create the files given in argument or the target if no
     argument is given. If the files already exist, the modification
     time is updated to the current time.
   * ``steps`` to execute multipe steps for a rule.

The remaining optional arguments are the target dependencies.

.. Local variables:
.. mode: rst
.. End:


.. image:: https://d2weczhvl823v0.cloudfront.net/fredericlepied/builder/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

