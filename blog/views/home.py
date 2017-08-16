#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render,HttpResponse
from django.shortcuts import redirect
from repository import models
from utils.pagination import Pagination,Pagination2
from django.urls import reverse
import json
from django.http.request import QueryDict


def home(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/wupeiqi.html
    :return:
    """
    #获取博客对象
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    #获取该博客所有标签和分类
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    # date_format(create_time,"%Y-%m")
    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article WHERE blog_id = %s group by strftime("%%Y-%%m",create_time)'%blog.nid)
        #group by 分组,外键过滤
    #获取该博客当前页所有文章对象和分页html
    article_list_all = models.Article.objects.filter(blog=blog).order_by('-nid').all()
    p= Pagination2(request.GET.get('p',1),article_list_all.count())
    article_list=article_list_all[p.start:p.end]
    page_str = p.page_str(reverse('article_home',kwargs={'site':site}))

    #获取博客文章总数
    article_counts = article_list_all.count()




    #获取博客文章评论总数
    article_comment_counts=0
    for item in article_list:
        article_comment_counts += models.Comment.objects.filter(article=item).count()

    #获取最新评论
    recent_comments = models.Comment.objects.all().order_by("-nid")[0:5]



    return render(
        request,
        'home.html',
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list,
            'article_counts':article_counts,
            'article_comment_counts':article_comment_counts,
            'recent_comments':recent_comments,
            'page_str':page_str,
        }
    )


def filter(request, site, condition, val):
    """
    分类显示
    :param request:
    :param site:
    :param condition:
    :param val:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article WHERE blog_id = %s group by strftime("%%Y-%%m",create_time)'%blog.nid)

    template_name = "home_summary_list.html"
    if condition == 'tag':
        article_list_all = models.Article.objects.filter(tags=val, blog=blog).all()
    elif condition == 'category':
        article_list_all = models.Article.objects.filter(category_id=val, blog=blog).all()
    elif condition == 'date':
        # article_list = models.Article.objects.filter(blog=blog).extra(
        # where=['date_format(create_time,"%%Y-%%m")=%s'], params=[val, ]).all()

        article_list_all = models.Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).all()
        # select * from article where strftime("%Y-%m",create_time)=2017-02
    else:
        article_list_all = []

    p = Pagination2(request.GET.get('p', 1), article_list_all.count())
    article_list = article_list_all[p.start:p.end]
    page_str = p.page_str(reverse('article_filter', kwargs={'site': site,'condition':condition,'val':val}))

    # 获取博客文章总数
    article_counts = article_list_all.count()
    # 获取博客文章评论总数
    article_comment_counts = 0
    for item in article_list:
        article_comment_counts += models.Comment.objects.filter(article=item).count()

    #获取最新评论
    recent_comments = models.Comment.objects.all().order_by("-nid")[0:5]

    return render(
        request,
        template_name,
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list,
            'article_counts': article_counts,
            'article_comment_counts': article_comment_counts,
            'recent_comments': recent_comments,
            'page_str':page_str
        }
    )


def detail(request, site, nid):
    """
    博文详细页
    :param request:
    :param site:
    :param nid:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article WHERE blog_id = %s group by strftime("%%Y-%%m",create_time)'%blog.nid)


    comment_list = models.Comment.objects.filter(article_id=nid).select_related('reply')
    #文章阅读数加一
    obj =models.Article.objects.get(nid=nid)
    obj.read_count +=1
    obj.save()

    #获取文章列表
    article = models.Article.objects.filter(blog=blog, nid=nid).select_related('category', 'articledetail').first()

    #获取最新评论
    recent_comments = models.Comment.objects.all().order_by("-nid")[0:5]

    response = render(
        request,
        'home_detail.html',
        {
            'blog': blog,
            'article': article,
            'comment_list': comment_list,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'recent_comments': recent_comments,
        }

    )
    return response


def article_updown(request):
    result = {'status': False, 'message': None, 'data': {}}
    user_session_message = request.session.get("user_info")
    #用户已登录情况

    if user_session_message:
        result['status'] = True
        #获取提交的数据
        nid = request.POST.get('nid')
        message = request.POST.get('message')
        print nid,message
        #获取当前文章点赞数和踩数。
        article_obj = models.Article.objects.filter(nid=nid)
        up_count = article_obj.first().up_count
        down_count = article_obj.first().down_count
        #获取当前文章赞或踩表格对象。
        updown_obj =models.UpDown.objects.filter(article_id = nid,user_id = user_session_message["nid"]).first()
        #如果当前文章已被踩或赞
        if updown_obj:
            #如果文章是已被赞
            if updown_obj.up:
                article_obj.update(up_count =up_count-1)
                updown_obj.delete()
                if message == "down":
                    article_obj.update(down_count=down_count + 1)
                    models.UpDown.objects.create(article_id=nid, user_id=user_session_message["nid"], up=False)
            #文章已被踩
            else:
                article_obj.update(down_count=down_count-1)
                updown_obj.delete()
                if message == "up":
                    article_obj.update(up_count=up_count + 1)
                    models.UpDown.objects.create(article_id=nid, user_id=user_session_message["nid"], up=True)
        #文章没有被踩或赞
        else:
            #判断当前文章是赞还是踩
            if message == "up":
                article_obj.update(up_count=up_count+1)
                models.UpDown.objects.create(article_id =nid,user_id =user_session_message["nid"],up =True)
            else:
                article_obj.update(down_count=down_count+1)
                models.UpDown.objects.create(article_id = nid,user_id = user_session_message["nid"],up =False)
        #返回文章赞数和踩数
        result['data']["up_count"] = article_obj.first().up_count
        result['data']["down_count"] = article_obj.first().down_count
        print up_count,down_count
        return HttpResponse(json.dumps(result))
    else:
        return HttpResponse(json.dumps(result))


        #修改文章表点赞或点踩


def submit_comment(request):

    result = {'status': False, 'message': None, 'data': {}}
    user_session_message = request.session.get("user_info")
    # 获取文章nid,被回复的评论的nid,回复内容
    artcle_nid = request.POST.get("article_nid")
    reply_comment_nid =request.POST.get("reply_comment_nid")
    reply_comment = request.POST.get("reply_comment")
    comment_user =request.POST.get("comment_user")
    #将评论写进文章评论表

        #如果该条评论是回复他人的评论。
    if reply_comment_nid:
        comment_user='@'+comment_user #拼接字符串
        reply_comment =reply_comment.replace(comment_user,"")
        models.Comment.objects.create(content=reply_comment,
                                            article_id=artcle_nid,
                                            user_id=user_session_message["nid"],                                            reply_id=reply_comment_nid,)
    else:
        models.Comment.objects.create(content=reply_comment,
                                      article_id=artcle_nid,
                                      user_id=user_session_message["nid"],
                                      )
    #文章评论数自增一
    article_obj =models.Article.objects.get(nid=artcle_nid)
    article_obj.comment_count +=1
    article_obj.save()
    result["status"] = True
    return HttpResponse(json.dumps(result))


def delete_comment(request):
    result = {'status': False, 'message': None, 'data': {}}
    reply_comment_nid = request.POST.get("reply_comment_nid")
    artcle_nid = request.POST.get("article_nid")
    #删除评论
    try:
        models.Comment.objects.filter(nid =reply_comment_nid).delete()
        #文章表评论数自减一
        article_obj = models.Article.objects.get(nid=artcle_nid)
        article_obj.comment_count -= 1
        result['data']['comment_counts']=article_obj.comment_count
        article_obj.save()
        result['status'] = True
    except:
        result['status'] = False
    return HttpResponse(json.dumps(result))
