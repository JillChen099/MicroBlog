#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json,os
from django.forms.utils import ErrorDict
from django.core.exceptions import ValidationError
from io import BytesIO
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from utils.check_code import create_validate_code
from repository import models
from ..forms.account import LoginForm,RegisterForm

def jsonp(request):
    func = request.GET.get('callback')
    content = '%s(100000)' %(func,)
    return HttpResponse(content)


def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO() #开辟内存空间
    img, code = create_validate_code()
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())


def login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        result = {'status': False, 'message': None, 'data': None}
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_info = models.UserInfo.objects. \
                filter(username=username, password=password). \
                values('nid', 'nickname',
                       'username', 'email',
                       'avatar',
                       'blog__nid',
                       'blog__site').first()
            #user_info 是一个字典
            if not user_info:
                # result['message'] = {'__all__': '用户名或密码错误'}
                result['message'] = '用户名或密码错误'
            else:
                result['status'] = True
                request.session['user_info'] = user_info
                if form.cleaned_data.get('rmb'):
                    request.session.set_expiry(60 * 60 * 24 * 7)
        else:
            print(form.errors)
            if 'check_code' in form.errors:
                result['message'] = '验证码错误或者过期'
            else:
                result['message'] = '用户名或密码错误'
        return HttpResponse(json.dumps(result))


def register(request):
    """
    注册
    :param request:
    :return:
    """
    form = RegisterForm(request=request)
    result = {'status': 'hide', 'message': {}, 'form': form}
    if request.method == 'POST':
        form = RegisterForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            nickname = form.cleaned_data.get('nickname')
            try:

                userinfo_obj =models.UserInfo.objects.create(
                                           username = username,
                                           password = password,
                                           email = email,
                                           avatar ='static/images/avatar/default.png',
                                           nickname = nickname,
                                           )
                blog_obj = models.Blog.objects.create(
                    title = (nickname + '博客乐园'),
                    site = username,
                    theme = 'default',
                    user = userinfo_obj
                )

                result['message']['username'] = username
                result['message']['password'] = password

                return render(request, 'success_register.html',result)
            except Exception as e:
                result['status'] = ''
                result['form'] = form
                if 'username' in e.message:
                    result['message'] = '该用户名已被使用，请更换用户名！'
                if 'email'  in e.message:
                    result['message'] = '该邮箱已被使用，请更换邮箱地址！'


        else:
            result['status'] = ''
            result['form'] = form
            result['message'] = form.errors.as_data().values()[0][0].message
    return render(request, 'register.html',result)


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    user_info = request.session.get('user_info')
    models.UserInfo.objects.filter(nid=user_info['nid']).update(line_status=False)
    request.session.clear()

    return redirect('/')

