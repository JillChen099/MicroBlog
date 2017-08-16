#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django import template

from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def mark_safe_html(i):
    return mark_safe(i)