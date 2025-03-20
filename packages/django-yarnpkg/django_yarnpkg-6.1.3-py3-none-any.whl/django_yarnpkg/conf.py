# -*- coding: utf-8 -*-
from shutil import which
import os
import sys
from django.conf import settings

__all__ = ['NODE_MODULES_ROOT', 'YARN_PATH']

NODE_MODULES_ROOT = getattr(settings, 'NODE_MODULES_ROOT', os.path.abspath(os.path.dirname(__name__)))

default_yarn_path = which('yarnpkg') or which('yarn')

YARN_PATH = getattr(settings, 'YARN_PATH', default_yarn_path)
