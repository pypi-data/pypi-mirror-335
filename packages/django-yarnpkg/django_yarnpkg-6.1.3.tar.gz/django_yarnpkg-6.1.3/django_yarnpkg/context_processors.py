# -*- coding: utf-8 -*-
import os.path
import json
from django.conf import settings
from django.utils.datastructures import OrderedSet


def read_files():
    for component in settings.YARN_INSTALLED_APPS:
        component = component.split('#')[0]
        try:
            with open(os.path.join(
                    settings.NODE_MODULES_ROOT,
                    'node_modules',
                    component,
                    'package.json')) as package_json:
                files = json.load(bower_json).get('files')
                for f in files:
                    yield '%s/%s' % (component, f)
        except FileNotFoundError:
            continue


def node_modules(request):
    return {
        'node_modules': OrderedSet([f for f in read_files()]),
    }
