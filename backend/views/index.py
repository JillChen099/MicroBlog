#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render
from backend.auth.auth import check_login
from repository import models




@check_login
def index(request):
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    return render(request, 'backend_index.html',{'user_info':user_info})
















