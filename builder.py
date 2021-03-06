#
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Author: Frederic Lepied <frederic.lepied@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

'''Module to build a dependency graph of shell commands like the make
tool using the power of the Python language to be able to build more
sophisticated rules.
'''

import inspect
import os
import os.path
import re
import select
import subprocess
import sys


_RULES = {}
_FIRST = None


def mtime(path):
    '''Return the modification time of the file or -1 if the file
doesn't exist.
'''
    try:
        return os.path.getmtime(path)
    except os.error:
        return -1


def rule(target, build, *reqs):
    '''Define a new rule in the ruleset. The rule defines how to build
``target`` using the ``build`` function. ``reqs`` are the list of targets
to satisfy before trying to build ``target``.

These calls must be done between calls to ``init_vars`` and
``process_targets``.
'''
    global _FIRST

    glob = inspect.stack()[-1][0].f_globals

    target = subst_vars(glob, target)

    if not _FIRST:
        _FIRST = target

    _RULES[target] = ([subst_vars(glob, x) for x in reqs], build)


def build_target(target):
    '''Build a target by comparing modification times between the dependencies
and the target recursively.
'''
    try:
        rul = _RULES[target]
        target_mtime = mtime(target)
        rebuild = (target_mtime == -1)
        for req in rul[0]:
            req_mtime = mtime(req)
            if req_mtime == -1:
                if not build_target(req):
                    return False
                else:
                    req_mtime = mtime(req)
            if req_mtime > target_mtime:
                rebuild = True
        if rebuild:
            if rul[1]:
                return rul[1](target, rul[0])
            else:
                return True
        else:
            return True
    except KeyError:
        sys.stderr.write('*** UNKNOWN TARGET %s.\n' % target)
        return False


VAR_REGEXP = re.compile(r'\$\(([^)]+)\)')


def subst_vars(arr, string):
    '''Substitute variable in the form $(VAR) from the ``arr`` argument.'''
    substs = []
    for match in VAR_REGEXP.finditer(string):
        substs.insert(0,
                      (match.start(),
                       match.end(),
                       arr.get(match.group(1), '')))
    for subst in substs:
        string = string[0:subst[0]] + subst[2] + string[subst[1]:]
    return string


def cmd(*args):
    '''Build the command from ``args``. Then display it before displaying its
output. Return ``True`` if the command exists with 0 or ``False`` for other
values.

If the command starts with @, the command is not discplayed.

If the command starts with -, its exit status is ignored.
'''
    ignore_failure = False
    args = list(args)
    if args[0][0] == '-':
        ignore_failure = True
        args[0] = args[0][1:]
    command_output = True
    if args[0][0] == '@':
        command_output = False
        args[0] = args[0][1:]
    if command_output:
        sys.stderr.write('+ %s\n' % ' '.join(args))
    glob = inspect.stack()[-1][0].f_globals
    status = run_command([subst_vars(glob, x) for x in args])
    if not ignore_failure and status != 0:
        sys.stderr.write('*** Error %d\n' % status)
        return False
    return True


def run_command(args):
    '''Run a command incrementaly displaying its standard
and error outputs.
'''
    pipe = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    inputset = [pipe.stdout, pipe.stderr]
    while inputset != []:
        inputs, _, _ = select.select(inputset, (), ())
        if pipe.stdout in inputs:
            chars = os.read(pipe.stdout.fileno(), 1024)
            if chars and chars != '':
                sys.stdout.write(chars.decode('ascii'))
            else:
                pipe.stdout.close()
                inputset.remove(pipe.stdout)
        if pipe.stderr in inputs:
            chars = os.read(pipe.stderr.fileno(), 1024)
            if chars and chars != '':
                sys.stderr.write(chars.decode('ascii'))
            else:
                pipe.stderr.close()
                inputset.remove(pipe.stderr)
    return pipe.wait()


def run(*args):
    '''Return a function that will launch a command when called. The arguments
are split according to space to allow to pass a list or a string with spaces.
'''
    largs = sum([x.split() for x in args], [])

    def do_run(_target, _reqs):
        '''Generated function to run the command captured by the closure.'''
        return cmd(*largs)
    return do_run


def touch(*args):
    '''Return a function that will touch its argument or if called without
argument, it will touch the target.
'''
    if len(args) == 0:
        def do_touch(target, _reqs):
            '''Touch the target.'''
            return cmd('touch', target)
        return do_touch
    else:
        return run('touch', *args)


def steps(*lsteps):
    '''Return a function that run all the steps passed in argument
sequentially. If one step fails, it returns ``False``.
'''
    def do_steps(target, reqs):
        '''run multiple functions in sequence.'''
        for step in lsteps:
            if not step(target, reqs):
                return False
        return True
    return do_steps


def end_rules():
    '''Satisfy the targets passed on the command line or start with the first
target defined in the rules file.

This call must be placed at the end of the rules file.
'''
    if len(sys.argv[1:]) == 0:
        if not _FIRST:
            sys.stderr.write("*** NO TARGET.\n")
            return 1
        if not build_target(_FIRST):
            return 1
    else:
        for target in sys.argv[1:]:
            if not build_target(target):
                return 1
    return 0


def process_vars(args):
    '''Inject variable in the globals of the toplevel frame (in the form
VAR=VAL) and return the list without these entries.
'''
    glob = inspect.stack()[-1][0].f_globals
    for var in [x for x in args if '=' in x]:
        key, val = var.split('=')
        glob[key] = val

    for key in glob:
        if isinstance(glob[key], str):
            os.environ[key] = glob[key]

    return [x for x in args if '=' not in x]


def end_vars():
    '''Process variable on the command line (in the form VAR=VAL) and inject
them in the  globals of the top level frame. The sys.argv is changed by
removing the variable arguments.

This call must be placed after the declaration of variables in the rules file.
'''
    args = process_vars(sys.argv[1:])
    sys.argv = [sys.argv[0], ] + args

# builder.py ends here
