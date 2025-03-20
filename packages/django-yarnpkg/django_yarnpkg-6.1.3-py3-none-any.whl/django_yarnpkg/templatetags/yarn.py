# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
from django import template
from django.templatetags import static


register = template.Library()


style_template = template.Template(
    """{% for filename in files %}
       <link href="{{filename}}" rel="stylesheet" type="text/css">
       {% endfor %}"""
)


script_template = template.Template(
    """{% for filename in files %}
       <script src="{{filename}}" type="text/javascript"></script>
       {% endfor %}"""
)


def tags(context, args, type):
    components = (
        [arg for arg in args if arg in context['node_modules']]
        if args else context['node_modules']
    )
    files = []
    for component in components:
        files.append(component)
        context['node_modules'].remove(component)
    return {'files': [
        static.static(f)
        for f in files
        if os.path.splitext(f)[1][1:] == type
    ]}


@register.inclusion_tag(style_template, takes_context=True)
def yarn_styles(context, *args):
    return tags(context, args, 'css')


@register.inclusion_tag(script_template, takes_context=True)
def yarn_scripts(context, *args):
    return tags(context, args, 'js')
