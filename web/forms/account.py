#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.exceptions import ValidationError
from django import forms
from django.forms import widgets
from django.forms import  fields
from repository import models

from .base import BaseForm


class LoginForm(BaseForm, forms.Form):
    username = forms.CharField(
        min_length=6,
        max_length=20,
        error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符", 'max_length': "用户名长度不能大于32个字符"}
    )


    password = forms.RegexField(
        regex='^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
        min_length=8,
        max_length=32,
        error_messages={'required': '密码不能为空.',
                        'invalid': '密码必须包含数字，字母、特殊字符',
                        'min_length': "密码长度不能小于8个字符",
                        'max_length': "密码长度不能大于32个字符"}
    )
    rmb = forms.IntegerField(required=False)

    check_code = forms.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')

class RegisterForm(BaseForm,forms.Form):
    username = forms.CharField(
        min_length=6,
        max_length=12,
        error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符", 'max_length': "用户名长度不能大于12个字符"},
        widget = widgets.TextInput(attrs={'class':'form-control','placeholder':"请输入用户名"},)
    )
    nickname = forms.CharField(
        min_length=3,
        max_length=8,
        error_messages={'required': '昵称不能为空.', 'min_length': "昵称长度不能小于3个字符", 'max_length': "昵称长度不能大于8个字符"},
        widget = widgets.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入昵称"}, )
    )
    password = forms.RegexField(
        regex='^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
        min_length=8,
        max_length=32,
        error_messages={'required': '密码不能为空.',
                        'invalid': '密码必须包含数字，字母、特殊字符',
                        'min_length': "密码长度不能小于8个字符",
                        'max_length': "密码长度不能大于32个字符"},
        widget = widgets.PasswordInput(attrs={'class':'form-control','placeholder':"请输入密码"},)
    )

    password2 = forms.CharField(widget =widgets.PasswordInput(attrs={'class':'form-control','placeholder':"请重新输入密码"},) )

    email = forms.EmailField(error_messages={'required':'邮箱不能为空','invalid':'邮箱格式错误！'},
                             widget=widgets.EmailInput(attrs={'class':'form-control','placeholder':"请输入邮箱"},)
                             )

    check_code = forms.CharField(
        error_messages={'required': '验证码不能为空.'},
        widget =widgets.TextInput(attrs={'class':'form-control','placeholder':"请输入验证码"},)
    )

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误或过期', code='invalid')

    def clean(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise ValidationError(u"两次密码必须一致")