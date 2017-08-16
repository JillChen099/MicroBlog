#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets

from repository import models


class ArticleForm(django_forms.Form):
    title = django_fields.CharField(
        widget=django_widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '文章标题'}),
        error_messages = {'required': '文章标题1不能为空！'}
    )
    summary = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class': 'form-control', 'placeholder': '文章简介', 'rows': '3'}),
        error_messages = {'required': '文章简介不能为空！'}
    )
    content = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class': 'kind-content'}),
        error_messages = {'required': '文章内容不能为空！'}
    )
    article_type_id = django_fields.IntegerField(
        widget=django_widgets.RadioSelect(choices=models.Article.type_choices),
        error_messages = {'required': '请勾选文章类型！'}
    )
    category_id = django_fields.ChoiceField(
        choices=[],
        widget=django_widgets.RadioSelect,
        error_messages={'required':'请勾选文章分类，如果没有分类，请先添加分类！'}
    )

    tags = django_fields.MultipleChoiceField(
        choices=[],
        widget=django_widgets.CheckboxSelectMultiple,
        error_messages={'required':'请勾选标签，如果没有标签，请先添加标签！'}

    )

    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        blog_id = request.session['user_info']['blog__nid']
        self.fields['category_id'].choices = models.Category.objects.filter(blog_id=blog_id).values_list('nid',
                                                                                                         'title')
        self.fields['tags'].choices = models.Tag.objects.filter(blog_id=blog_id).values_list('nid', 'title')


class Base_Info(django_forms.Form):
    nickname = django_forms.CharField(
        min_length=3,
        max_length=12,
        error_messages={'required': '昵称不能为空.', 'min_length': "昵称长度不能小于3个字符", 'max_length': "昵称长度不能大于12个字符"},
    )
    blog_ad = django_forms.CharField(
        required=False,
        max_length=25,
        error_messages={'max_length': "公告长度不能大于25个字符"},
    )
    blog_title = django_forms.CharField(
        max_length=10,
        error_messages={'required': '博客标题不能为空.', 'max_length': "博客长度不能大于10个字符"},
    )

    blog_subtitle = django_forms.CharField(
        required=False,
    )



class Chpassword_Form(django_forms.Form):
    oldpassword=django_forms.CharField(widget=django_widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入原密码"},))

    newpassword = django_forms.RegexField(
        regex='^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
        min_length=8,
        max_length=32,
        error_messages={'required': '密码不能为空!',
                        'invalid': '密码必须包含数字，字母、特殊字符',
                        'min_length': "密码长度不能小于8个字符",
                        'max_length': "密码长度不能大于32个字符"},
        widget=django_widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请输入新密码",})

    )

    newpassword2 = django_forms.CharField(widget=django_widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': "请再一次输入新密码",}))

    def clean_newpassword2(self):
        newpassword = self.cleaned_data.get("newpassword")
        newpassword2 = self.cleaned_data.get("newpassword2")

        if newpassword != newpassword2:
            raise ValidationError(u"两次密码必须一致","not_samepassword")

    def clean_oldpassword(self):

        user_nid=self.request.session['user_info']['nid']
        oldpassword2 =models.UserInfo.objects.get(nid=user_nid).password
        oldpassword = self.cleaned_data.get("oldpassword")
        if oldpassword !=oldpassword2:
            raise ValidationError(u'旧密码错误，请重新输入！','oldpasswordright')
    def __init__(self, request, *args, **kwargs):
        super(Chpassword_Form, self).__init__(*args, **kwargs)
        self.request = request

