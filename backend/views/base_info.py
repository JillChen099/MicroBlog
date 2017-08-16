#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import uuid
from django.shortcuts import render
from django.shortcuts import HttpResponse

from backend.forms.article_form import Base_Info,Chpassword_Form
from backend.auth.auth import check_login
from repository import models



@check_login
def change_password(request):
    """
    修改用户密码
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_nid =user['nid']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    result = {'erro_class': "hide", 'message': "", 'form': None, 'user_info': user_info}
    form = Chpassword_Form(request=request)
    result['form'] = form
    if request.method=="POST":
        form = Chpassword_Form(request=request,data=request.POST)
        print form.is_valid()
        if form.is_valid():
            newpassword = form.cleaned_data['newpassword']
            models.UserInfo.objects.filter(nid=user_nid).update(password=newpassword)
            result['message']="修改密码成功！"

        else:
            result['erro_class']=""
            result['form']=form
            result['message'] = "修改密码失败！"
            print form.errors['oldpassword']
    return render(request, 'change_password.html',result)

@check_login
def base_info(request):
    """
    博主个人信息
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_id =user['nid']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    result = {'status': False, 'message': "",'user_info':user_info}
    if request.method=="POST":
        baseinfo_form = Base_Info(request.POST)
        if baseinfo_form.is_valid():
            nickname = baseinfo_form.cleaned_data.get('nickname')
            blog_ad = baseinfo_form.cleaned_data.get('blog_ad')
            blog_title = baseinfo_form.cleaned_data.get('blog_title')
            blog_subtitle = baseinfo_form.cleaned_data.get('blog_subtitle')
            models.Blog.objects.filter(user_id=user_id).update(ad=blog_ad,title=blog_title,subtitle=blog_subtitle)
            models.UserInfo.objects.filter(nid=user_id).update(nickname=nickname)
            result["status"] = True
            result['message'] = "个人信息修改成功！"
        else:
            result['status'] = False
            result['message'] = baseinfo_form.errors.as_data().values()[0][0].message
        return render(request, 'backend_base_info.html',result)
    else:
        return render(request, 'backend_base_info.html',result)


@check_login
def upload_avatar(request):
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        print(file_obj)
        if not file_obj:
            pass
        else:

            file_name = str(uuid.uuid4())
            file_path = os.path.join('static/images/avatar/', file_name)
            '''
            删除旧头像文件，把新头像文件的地址写入数据库中
            '''
            user_info = request.session['user_info']
            obj = models.UserInfo.objects.filter(username=user_info['username'])
            last_avater_add =  str(obj.first().avatar)
            os.remove(last_avater_add)
            obj.update(avatar=file_path)
            '''
            把新头像文件放置到头像文件中。
            '''

            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path

    return HttpResponse(json.dumps(ret))



































