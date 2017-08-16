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
def tag(request):
    """
    博主个人标签管理
    tag标签id具有唯一性
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    blog_id = request.session['user_info']['blog__nid']#int型
    #获取当前博客所有标签
    tag_obj = models.Tag.objects.filter(blog__nid=blog_id).order_by("-nid").values('nid', 'title')
    #获取当前博客所有文章
    article_obj = models.Article.objects.filter(blog_id=blog_id)
    #获取当前博客每个标签所拥有的文章数量
    for item in tag_obj:
        tag_id = item['nid']
        item['counts'] =models.Article2Tag.objects.filter(tag_id=tag_id).count()

    # 获取每页的结果和分页html
    page = Pagination(request.GET.get('p', 1), tag_obj.count())
    result = tag_obj[page.start:page.end]
    page_html = page.page_str(base_url=reverse('tag'))
    return render(request, 'backend_tag.html',{'user_info':user_info,
                                                    'result':result,
                                                    'page_html':page_html,
                                                    })

@check_login
def delete_tag(request):
    '''
    删除文章标签
    '''
    result = {'status':None,'Data':None,'message':None}
    blog_id = request.session['user_info']['blog__nid']
    nid = request.POST.get('nid')
    #删除标签表数据
    models.Tag.objects.filter(blog_id = blog_id,nid =nid).delete()
    #删除文章标签关系表数据
    models.Article2Tag.objects.filter(tag_id =nid).delete()
    result['status'] = True
    return HttpResponse(json.dumps(result))

@check_login
def change_tag(request):
    '''
    修改文章标签名称
    '''
    result = {'status': None, 'Data': None, 'message': None}
    blog_id = request.session['user_info']['blog__nid']
    nid = request.POST.get('nid')
    value = request.POST.get('value')
    try:
        models.Tag.objects.filter(blog_id=blog_id, nid=nid).update(title = value)
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))

@check_login
def add_tag(request):
    '''
    添加文章标签

    '''
    result = {'status': None, 'Data': {}, 'message': None}
    blog_id = request.session['user_info']['blog__nid']
    value = request.POST.get('data')
    try:
        obj=models.Tag.objects.create(title = value,blog_id=blog_id)
        result['Data']['nid'] =obj.nid
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))















