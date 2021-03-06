#!/usr/bin/env python2

# Copyright 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import os
import re

macro_root = read_config('fbcode', 'macro_lib', '//macro_lib')
include_defs("{}/convert/base.py".format(macro_root), "base")
include_defs("{}/rule.py".format(macro_root))


class CppJvmLibrary(base.Converter):

    def get_fbconfig_rule_type(self):
        return 'cpp_jvm_library'

    def get_allowed_args(self):
        return set([
            'name',
            'major_version',
        ])

    def convert(self, base_path, name, major_version, visibility=None):
        attrs = collections.OrderedDict()
        attrs['name'] = name
        if visibility is not None:
            attrs['visibility'] = visibility

        ppflags = []
        ldflags = []
        for platform in self.get_platforms():
            # We use include/library paths to wrap the custom FB JDK installed
            # at system locations.  As such, we don't properly hash various
            # components (e.g. headers, libraries) pulled into the build.
            # Longer-term, we should move the FB JDK into tp2 to do this
            # properly.
            plat_re = '^{}$'.format(re.escape(platform))
            jvm_path = '/usr/local/fb-jdk-{}-{}'.format(major_version, platform)
            arch = self.get_platform_architecture(platform)
            # Remap arch to JVM-specific names.
            arch = {'x86_64': 'amd64'}.get(arch, arch)
            ppflags.append((
                plat_re,
                ['-isystem',
                 os.path.join(jvm_path, 'include'),
                 '-isystem',
                 os.path.join(jvm_path, 'include', 'linux')]))
            ldflags.append((
                plat_re,
                ['-L{}/jre/lib/{}/server'.format(jvm_path, arch),
                 '-Wl,-rpath={}/jre/lib/{}/server'.format(jvm_path, arch),
                 '-ljvm']))
        attrs['exported_platform_preprocessor_flags'] = ppflags
        attrs['exported_platform_linker_flags'] = ldflags

        return [Rule('cxx_library', attrs)]
