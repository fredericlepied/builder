#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from distutils.core import setup


setup(name='builder',
      long_description='Build a dependency graph of shell '
      'commands like the make tool',
      version='0.1',
      keywords=['make', 'build'],
      author=u'Frédéric Lepied',
      author_email='frederic.lepied@enovance.com',
      url='https://github.com/enovance/builder',
      license='Apache',
      py_modules=['builder', ])

# setup.py ends here
