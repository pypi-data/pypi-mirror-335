from django.core.management import call_command
from django.conf import settings
from django.test import TestCase
from io import StringIO
from mock import MagicMock
from ..yarn import yarn_adapter, YarnAdapter
from .. import conf
from .base import BaseYarnCase, TEST_NODE_MODULES_ROOT
import os
import shutil


class YarnAdapterCase(TestCase):
    """
    YarnAdapter regression tests.
    """

    def test_create_node_modules_root_subdirs(self):
        """
        create_node_modules_root() creates missing intermediate directories.
        """
        if os.path.exists(TEST_NODE_MODULES_ROOT):
            shutil.rmtree(TEST_NODE_MODULES_ROOT)

        subdir = os.path.join(TEST_NODE_MODULES_ROOT, 'sub', 'dir')
        adapter = YarnAdapter(conf.YARN_PATH, subdir)
        adapter.create_node_modules_root()
        self.assertTrue(os.path.exists(subdir))

        shutil.rmtree(TEST_NODE_MODULES_ROOT)


class YarnInstallCase(BaseYarnCase):
    """Test case for yarn_install management command"""

    def setUp(self):
        super(YarnInstallCase, self).setUp()
        self.apps = settings.YARN_INSTALLED_APPS
        self._original_install = yarn_adapter.install
        yarn_adapter.install = MagicMock()

    def tearDown(self):
        super(YarnInstallCase, self).tearDown()
        yarn_adapter.install = self._original_install

    def test_create_node_modules_root(self):
        """Test create node_modules root"""
        self._remove_node_modules_root()
        call_command('yarn_install')

        self.assertTrue(os.path.exists(TEST_NODE_MODULES_ROOT))

    def test_install(self):
        """Test install yarn packages"""
        call_command('yarn_install')
        yarn_adapter.install.assert_called_once_with(self.apps)


class YarnExistsCase(BaseYarnCase):
    """
    Test yarn exists checker.
    This case need yarn to be installed.
    """

    def setUp(self):
        super(YarnExistsCase, self).setUp()
        self._original_exists = yarn_adapter.is_yarn_exists

    def tearDown(self):
        super(YarnExistsCase, self).tearDown()
        yarn_adapter.is_yarn_exists = self._original_exists

    def test_if_exists(self):
        """Test if yarn exists"""
        self.assertTrue(yarn_adapter.is_yarn_exists())

    def test_if_not_exists(self):
        """Test if yarn not exists"""
        adapter = YarnAdapter('/not/exists/path', TEST_NODE_MODULES_ROOT)
        self.assertFalse(adapter.is_yarn_exists())

    def _mock_exists_check(self):
        """Make exists check return false"""
        yarn_adapter.is_yarn_exists = MagicMock()
        yarn_adapter.is_yarn_exists.return_value = False


class YarnCommandCase(BaseYarnCase):
    """Test case for ./manage.py yarn something command"""

    def setUp(self):
        super(YarnCommandCase, self).setUp()
        self.apps = settings.YARN_INSTALLED_APPS
        self._mock_yarn_adapter()

    def _mock_yarn_adapter(self):
        self._original_install = yarn_adapter.install
        yarn_adapter.install = MagicMock()
        self._orig_call = yarn_adapter.call_yarn
        yarn_adapter.call_yarn = MagicMock()

    def tearDown(self):
        super(YarnCommandCase, self).tearDown()
        yarn_adapter.install = self._original_install
        yarn_adapter.call_yarn = self._orig_call

    def test_install_without_params(self):
        """Test that yarn install without param identical
        with yarn_install

        """
        call_command('yarn', 'install')
        yarn_adapter.install.assert_called_once_with(
            self.apps)

    def test_install_with_params(self):
        """Test yarn install <something>"""
        call_command('yarn', 'install', 'jquery')
        yarn_adapter.call_yarn.assert_called_once_with(
            ('install', 'jquery'))

    def test_call_to_yarn(self):
        """Test simple call to yarn"""
        call_command('yarn', 'update')
        yarn_adapter.call_yarn.assert_called_once_with(
            ('update',))
