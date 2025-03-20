from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from ..yarn import yarn_adapter
import os
import shutil


try:
    TEST_NODE_MODULES_ROOT = os.path.join(
        settings.TEST_PROJECT_ROOT, 'node_modules',
    )
except AttributeError:
    TEST_NODE_MODULES_ROOT = '/tmp/node_modules/'


@override_settings(NODE_MODULES_ROOT=TEST_NODE_MODULES_ROOT)
class BaseYarnCase(TestCase):
    """Base bower test case"""

    def setUp(self):
        yarn_adapter.create_node_modules_root()

    def tearDown(self):
        self._remove_node_modules_root()

    def _remove_node_modules_root(self):
        """Remove node_modules root if exists"""
        if os.path.exists(TEST_NODE_MODULES_ROOT):
            shutil.rmtree(TEST_NODE_MODULES_ROOT)

    def assertCountEqual(self, *args, **kwargs):
        """Add python 2 support"""
        if hasattr(self, 'assertItemsEqual'):
            return self.assertItemsEqual(*args, **kwargs)
        else:
            return super(BaseYarnCase, self).assertCountEqual(*args, **kwargs)
