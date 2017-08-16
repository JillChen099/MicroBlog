#-*- coding=utf-8 -*-
'''
Created on 

@author:Eden
'''
from django import template

register = template.Library()


@register.simple_tag
def get_number_index(son,father):
    d = {}
    i=1
    for item in father:
        d[item] = i
        i+=1
    return d[son]