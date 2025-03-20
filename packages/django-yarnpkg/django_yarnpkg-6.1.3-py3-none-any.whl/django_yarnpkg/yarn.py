from . import conf, shortcuts, exceptions
from shutil import which
import os
import subprocess
import sys
import json


class YarnAdapter(object):
    """Adapter for working with yarnpkg"""

    def __init__(self, yarn_path, node_modules_root):
        self._yarn_path = yarn_path
        self._node_modules_root = node_modules_root

    def is_yarn_exists(self):
        """Check is bower exists"""
        if shortcuts.is_executable(self._yarn_path)\
                or which(self._yarn_path):
            return True
        else:
            return False

    def create_node_modules_root(self):
        """Create node modules root if need"""
        if not os.path.exists(self._node_modules_root):
            os.makedirs(self._node_modules_root)

    def call_yarn(self, args):
        """Call yarn with a list of args"""
        proc = subprocess.Popen(
            [self._yarn_path] + list(args),
            cwd=self._node_modules_root)
        return proc.wait()

    def install(self, packages, *options):
        """Install packages from yarn"""
        self.call_yarn(["init", "--yes"])
        self.call_yarn(["config", "set", "nodeLinker", "node-modules"])
        return self.call_yarn(['add'] + list(options) + list(packages))

    def _accumulate_dependencies(self, data):
        """Accumulate dependencies"""
        for name, version in data['dependencies'].items():
            if version:
                full_name = '{0}@{1}'.format(name, version)
            else:
                full_name = name

            self._packages.append(full_name)
            self._accumulate_dependencies(params)

    def _parse_package_names(self, output):
        """Get package names in yarn"""
        data = json.loads(output)
        self._packages = []
        self._accumulate_dependencies(data)
        return self._packages

yarn_adapter = YarnAdapter(conf.YARN_PATH, conf.NODE_MODULES_ROOT)
