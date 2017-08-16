#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import redirect


def check_login(func):
    def inner(request, *args, **kwargs):
        session_status = request.session.get('user_info')
        if session_status:
            return func(request, *args, **kwargs)
        else:
            return redirect('/login.html')
    return inner