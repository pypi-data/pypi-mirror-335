try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from . import conf
import os


class NodeModulesFinder(FileSystemFinder):
    """Find static files installed with yarnpkg"""

    def __init__(self, apps=None, *args, **kwargs):
        self.locations = []
        self.storages = OrderedDict()

        root = self._get_node_modules_location()
        if root is not None:
            prefix = ''
            self.locations.append((prefix, root))

            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage

    def _get_node_modules_location(self):
        """
        Return the node modules location, or None if one does not exist.
        """
        path = os.path.join(conf.NODE_MODULES_ROOT, 'node_modules')
        if os.path.exists(path):
            return path
