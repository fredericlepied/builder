#!/usr/bin/env python
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

# example.py ends here
