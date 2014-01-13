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

import os.path
import tempfile
import unittest
import sys

from builder import build_target, end_rules, process_vars, \
    rule, run, steps, touch
import builder


class TestBuilderTest(unittest.TestCase):

    def setUp(self):
        def cmd(*args):
            self.run_cmd = ' '.join(args)
            print(self.run_cmd)
            return True

        self.run_cmd = None
        self.cmd = builder.cmd
        builder.cmd = cmd

        def mtime(path):
            try:
                t = self.time[path]
            except KeyError:
                t = -1
            if isinstance(t, int):
                return t
            else:
                return t.pop(-1)

        self.time = {}
        self.mtime = builder.mtime
        builder.mtime = mtime

    def tearDown(self):
        builder._RULES = {}
        builder._FIRST = None
        builder.cmd = self.cmd
        builder.mtime = self.mtime

    def test_rule(self):
        self.time = {'target': -1, 'req': 1}
        rule('target', touch(), 'req')
        self.assertTrue(build_target('target'))
        self.assertEqual(self.run_cmd, 'touch target')

    def test_empty(self):
        self.time = {'target': -1}
        rule('target', touch())
        self.assertTrue(build_target('target'))
        self.assertEqual(self.run_cmd, 'touch target')

    def test_first(self):
        rule('target', ('req',), touch)
        self.assertEqual(builder._FIRST, 'target')

    def test_complex(self):
        self.time = {'target': -1, 'req': [-1, 1]}
        rule('target', touch(), 'req')
        rule('req', touch)
        self.assertTrue(build_target('target'))
        self.assertEqual(self.run_cmd, 'touch target')

    def test_unknown_target(self):
        self.assertFalse(build_target('target'))

    def test_unknown_dep(self):
        rule('target', touch(), 'req')
        self.assertFalse(build_target('target'))

    def test_already_built(self):
        self.time = {'target': 1}
        rule('target', touch())
        self.assertTrue(build_target('target'))

    def test_mtime(self):
        temp = tempfile.NamedTemporaryFile()
        self.assertTrue(self.mtime(temp.name) != -1)
        temp.close()

    def test_mtime_does_not_exist(self):
        path = '/'
        while os.path.exists(path):
            path = path + '0'
        self.assertTrue(self.mtime(path) == -1)

    def test_cmd(self):
        self.assertTrue(self.cmd('true'))

    def test_failing_cmd(self):
        self.assertFalse(self.cmd('false'))

    def test_run(self):
        rule('target', run('touch', 'target'))
        self.assertTrue(build_target('target'))
        self.assertEqual(self.run_cmd, 'touch target')

    def test_end_rules(self):
        args = sys.argv
        rule('target', touch())
        sys.argv = ['make', 'target']
        self.assertEqual(end_rules(), 0)
        sys.argv = args
        self.assertEqual(self.run_cmd, 'touch target')

    def test_process_default_target(self):
        args = sys.argv
        rule('target', touch())
        sys.argv = ['make', ]
        self.assertEqual(end_rules(), 0)
        sys.argv = args
        self.assertEqual(self.run_cmd, 'touch target')

    def test_process_no_target(self):
        args = sys.argv
        sys.argv = ['make', ]
        self.assertEqual(end_rules(), 1)
        sys.argv = args

    def test_process_failed_target(self):
        args = sys.argv
        # run the real cmd to have the right exit status
        builder.cmd = self.cmd
        rule('target', run('false'))
        sys.argv = ['make', 'target']
        self.assertEqual(end_rules(), 1)
        sys.argv = args

    def test_process_failed_default_target(self):
        args = sys.argv
        # run the real cmd to have the right exit status
        builder.cmd = self.cmd
        rule('target', run('@false'))
        sys.argv = ['make', ]
        self.assertEqual(end_rules(), 1)
        sys.argv = args

    def test_process_vars(self):
        self.assertEqual(process_vars([]), [])

    def test_steps(self):
        rule('target', steps(touch()))
        self.assertTrue(build_target('target'))
        self.assertEqual(self.run_cmd, 'touch target')

    def test_ignore_result(self):
        # run the real cmd to have the right exit status
        builder.cmd = self.cmd
        rule('target', steps(run('-false')))
        self.assertTrue(build_target('target'))

if __name__ == "__main__":
    unittest.main()

# test_builder.py ends here
