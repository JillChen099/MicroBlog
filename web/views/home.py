#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render,HttpResponse
from django.shortcuts import redirect
from repository import models
from utils.pagination import Pagination
from django.urls import reverse
import json
from django.http.request import QueryDict
def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    :param request:
    :return:
    """

    article_type_list = models.Article.type_choices
    # [
    #     (1, "Python"),
    #     (2, "Linux"),
    #     (3, "OpenStack"),
    #     (4, "GoLang"),
    # ]
    if kwargs:
        #kwargs ={'article_type_id':'xx'}
        article_type_id = int(kwargs['article_type_id'])
        base_url = reverse('index',kwargs=kwargs)
    else:
        article_type_id = None
        base_url = '/'

    data_count = models.Article.objects.filter(**kwargs).count()
    #获取所有文章数
    page_obj = Pagination(request.GET.get('p'),data_count)
    #实例化分页对象，request.GET.get('p') 获取当前连接的当前页码
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    #获取文章对象列表
    page_str = page_obj.page_str(base_url)
    #获取分页html

    #吐血推荐文章对象
    tuxue_articles = models.Article.objects.all().order_by("-up_count")[0:8]

    #评论最多文章对象
    comments_article = models.Article.objects.all().order_by("-comment_count")[0:8]


    return render(
        request,
        'index.html',
        {

            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'article_list': article_list,
            'page_str': page_str,
            'tuxue_articles':tuxue_articles,
            'comments_article':comments_article,
        }
    )





