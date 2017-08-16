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

from backend.forms.article_form import ArticleForm,Base_Info,Chpassword_Form
from backend.auth.auth import check_login
from repository import models
from utils.pagination import Pagination
from utils.xss import XSSFilter


@check_login
def index(request):
    user = request.session['user_info']
    user_info = models.UserInfo.objects.filter(username=user['username']).first()
    return render(request, 'backend_index.html',{'user_info':user_info})

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