from pprint import pformat
from django.core.management.base import BaseCommand
from django.conf import settings
from ..yarn import yarn_adapter
from ..exceptions import YarnNotInstalled


class BaseYarnCommand(BaseCommand):
    """Base management command with yarn support"""

    requires_system_checks = []

    # add fake .options_list for Django>=1.10
    if not hasattr(BaseCommand, 'option_list'):
        option_list = ()

    def handle(self, *args, **options):
        self._check_yarn_exists()
        yarn_adapter.create_node_modules_root()

    def _check_yarn_exists(self):
        """Check yarn exists or raise exception"""
        if not yarn_adapter.is_yarn_exists():
            raise YarnNotInstalled()

    def _install(self, args):
        return yarn_adapter.install(settings.YARN_INSTALLED_APPS, *args)
