# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from repository import models
from django.shortcuts import render,HttpResponse
from django.shortcuts import redirect
from backend.auth.auth import check_login
import json,datetime

class CJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj,datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self,obj)


@check_login
def webchat_index(request):
    user_info = request.session.get('user_info')
    data = {'status':0,'user':user_info,'erro_message':''}
    models.UserInfo.objects.filter(nid=user_info['nid']).update(line_status=True)
    return render(request,'webchat_index.html',data)


@check_login
def summit_chat(request):
    ret={'status':0,'data':'','erro_message':''}
    if request.method =='POST':
        try:
            content = request.POST.get('data')
            user_info = request.session.get('user_info')
            user_obj = models.UserInfo.objects.get(nid=user_info['nid'])
            chat_obj=models.Chat.objects.create(content=content,user=user_obj)
            id = chat_obj.id
            ret['status']=1
            ret['data']={'id':id,
                        'user_info':user_info,
                         'content':content,
                         'create_date':chat_obj.creat_date.strftime('%Y-%m-%d %H:%M:%S')}
        except Exception,e:
            ret['erro_message']=e.message
        return HttpResponse(json.dumps(ret))
    else:
        return redirect('/')
@check_login
def get_chat_first(request):
    chat_objs = models.Chat.objects.all().order_by('-id')[0:10].values('id','content','user__nickname','user__avatar','creat_date')
    chat_lists =list(chat_objs)
    chat_lists = json.dumps(chat_lists,cls=CJsonEncoder)
    return HttpResponse(chat_lists)

@check_login
def get_chat(request):
    last_id = request.POST.get('last_id')
    chat_objs = models.Chat.objects.filter(id__gt=last_id).values('id','content','user__nickname','user__avatar','creat_date')
    chat_lists = list(chat_objs)
    chat_lists = json.dumps(chat_lists, cls=CJsonEncoder)
    return HttpResponse(chat_lists)
@check_login
def get_users_status(request):
    users_objs = models.UserInfo.objects.all().values('username','nickname','avatar','line_status')
    users_objs = list(users_objs)

    return HttpResponse(json.dumps(users_objs))
@check_login
def page_down(request):
    user_info = request.session.get('user_info')
    models.UserInfo.objects.filter(nid=user_info['nid']).update(line_status=False)
    return HttpResponse('')
