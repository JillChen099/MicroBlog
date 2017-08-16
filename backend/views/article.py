#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import uuid
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.db import transaction
from django.urls import reverse
from backend.forms.article_form import ArticleForm
from backend.auth.auth import check_login
from repository import models
from utils.pagination import Pagination
from utils.xss import XSSFilter



#KindEditor 编辑器上传图片，falsh,等待处理函数
@check_login
def upload_images(request):
    file_type = request.GET.get('dir')  #确定上传属于哪种文件类型
    '''
    print request.GET #<QueryDict: {u'dir': [u'image']}>
    print request.FILES #<MultiValueDict: {u'imgFile': [<InMemoryUploadedFile: a1544708.jpg (image/jpeg)>]}>
    '''
    if file_type == "image":
        #获取图片文件
        imgFile = request.FILES.get("imgFile")
        #保存图片文件
        if not imgFile:
            result = {
                'error': 1, #状态 1表示出错
                'url': '/static/images/o_Warning.png',  # 上传图片的url
                'message': '上传错误'

            }
        else:
            file_name = str(uuid.uuid4()) #保存的图片文件名
            file_path = os.path.join('static/images/article_images/', file_name) #图片文件路径
            with open(file_path,'wb') as f:
                for chunk in imgFile.chunks():
                    f.write(chunk)
            result ={
                'error':0,    #0 表示上传成功
                'url':'/'+file_path, #上传图片的url
                'message':'上传成功'

            }
        return HttpResponse(json.dumps(result))
    else:
        result = {
            'error': 1,
            'url': '',
            'message': '上传错误!'

        }
        return HttpResponse(json.dumps(result))


@check_login
def article(request, *args, **kwargs):
    """
    博主个人文章管理
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()


    blog_id = request.session['user_info']['blog__nid']
    condition = {}
    for k, v in kwargs.items():
        if v == '0':
            pass
        else:
            condition[k] = v
    condition['blog_id'] = blog_id
    data_count = models.Article.objects.filter(**condition).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title','blog').select_related('blog')[page.start:page.end]
    page_str = page.page_str(reverse('article', kwargs=kwargs))
    category_list = models.Category.objects.filter(blog_id=blog_id).values('nid', 'title')
    type_list = map(lambda item: {'nid': item[0], 'title': item[1]}, models.Article.type_choices)
    kwargs['p'] = page.current_page
    return render(request,
                  'backend_article.html',
                  {'result': result,
                   'page_str': page_str,
                   'category_list': category_list,
                   'type_list': type_list,
                   'arg_dict': kwargs,
                   'data_count': data_count,
                   'user_info':user_info}
                  )

@check_login
def delete_article(request):
    result = {'status':None,'Data':None,'message':None}
    blog_id = request.session['user_info']['blog__nid']
    nid = request.POST.get('nid')
    try:
        obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
        '''
        删除文章所附标签
        '''
        models.Article2Tag.objects.filter(article=obj).delete()
        #删除文章详细内容
        models.ArticleDetail.objects.filter(article=obj).delete()
        #删除文章表
        obj.delete()
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))

@check_login
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()


    if request.method == 'GET':
        form = ArticleForm(request=request)
        return render(request, 'backend_add_article.html', {'form': form,
                                                            'user_info':user_info})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)

            return redirect('/backend/article-0-0.html',{'user_info':user_info})
        else:
            scrollTop = int(request.POST.get('scrollTop'))
            return render(request, 'backend_add_article.html', {'form': form,
                                                                'user_info':user_info,'scrollTop':scrollTop})
    else:
        return redirect('/')


@check_login
def edit_article(request, nid):
    """
    编辑文章
    :param request:
    :return:
    """
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
        if not obj:
            return render(request, 'backend_no_article.html')
        tags = obj.tags.values_list('nid') #<QuerySet [(1,),(2,)]>
        if tags:
            tags = list(zip(*tags))[0] #(1, 2)
        init_dict = { #初始化数据
            'nid': obj.nid,
            'title': obj.title,
            'summary': obj.summary,
            'category_id': obj.category_id,
            'article_type_id': obj.article_type_id,
            'content': obj.articledetail.content,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid,'user_info':user_info})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request, 'backend_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop('tags')
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            scrollTop = int(request.POST.get('scrollTop'))

            return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid,'user_info':user_info,'scrollTop':scrollTop})