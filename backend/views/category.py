#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.urls import reverse
from backend.auth.auth import check_login
from repository import models
from utils.pagination import Pagination




@check_login
def category(request):
    """
    博主个人分类管理
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    blog_id = request.session['user_info']['blog__nid']
    #获取所有当前博客所有分类，及其每个分类所拥有的文章数
    obj =models.Category.objects.filter(blog__nid=blog_id).order_by("-nid").values('nid','title')
    for item in obj:
        category_id = item['nid']
        item['counts']=models.Article.objects.filter(category_id =category_id).count()
    # obj =<QuerySet [{'counts': 0, 'nid': 1, 'title': u'.NET'}, {'counts': 0, 'nid': 2, 'title': u'\u9886\u57df\u9a71\u52a8'},
    #获取每页的结果和分页html
    page = Pagination(request.GET.get('p', 1), obj.count())
    result = obj[page.start:page.end]
    page_html = page.page_str(base_url=reverse('category'))
    return render(request, 'backend_category.html',{'user_info':user_info,
                                                    'result':result,
                                                    'page_html':page_html,
                                                    })

@check_login
def delete_category(request):
    '''
    删除文章分类
    '''
    result = {'status':None,'Data':None,'message':None}
    blog_id = request.session['user_info']['blog__nid']
    nid = request.POST.get('nid')
    models.Category.objects.filter(blog_id = blog_id,nid =nid).delete()
    result['status'] = True
    return HttpResponse(json.dumps(result))

@check_login
def change_category(request):
    '''
    修改文章分类名称
    '''
    result = {'status': None, 'Data': None, 'message': None}
    blog_id = request.session['user_info']['blog__nid']
    nid = request.POST.get('nid')
    value = request.POST.get('value')
    try:
        models.Category.objects.filter(blog_id=blog_id, nid=nid).update(title = value)
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))

@check_login
def add_category(request):
    '''
    添加文章分类名称

    '''
    result = {'status': None, 'Data': {}, 'message': None}
    blog_id = request.session['user_info']['blog__nid']
    value = request.POST.get('data')
    try:
        obj=models.Category.objects.create(title = value,blog_id=blog_id)
        result['Data']['nid'] =obj.nid
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))




