#-*- coding=utf-8 -*-
from django.db import models


class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    avatar = models.ImageField(verbose_name='头像')
    line_status = models.BooleanField(verbose_name="是否在线",default=False)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo',
                                  through='UserFans',#自定义联系表
                                  related_name='f',
                                  through_fields=('user', 'follower'))

class UserFans(models.Model):
    """
    互粉关系表
    """
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users')
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers')

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]



class Blog(models.Model):
    """
    博客信息表
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    subtitle = models.CharField(verbose_name='个人博客副标题',max_length=64,default="Just do it")
    ad = models.CharField(verbose_name="个人博客公告",max_length=64,default= u"公告内容")
    site = models.CharField(verbose_name='个人博客前缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field='nid')

class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

class Tag(models.Model):
    '''
    博主个人文章标签
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')


class Article(models.Model):
    '''
    文章表
    '''
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(verbose_name="阅读数",default=0)
    comment_count = models.IntegerField(verbose_name="评论数",default=0)
    up_count = models.IntegerField(verbose_name="点赞数",default=0)
    down_count = models.IntegerField(verbose_name="点踩数",default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')
    category = models.ForeignKey(verbose_name='文章所属分类', to='Category', to_field='nid', null=True)

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "计算机和网络基础"),
        (4, "网络安全"),
        (5, "其他")
    ]

    article_type_id = models.IntegerField(verbose_name="文章类型表",choices=type_choices, default=None)

    tags = models.ManyToManyField(verbose_name="文章所附标签",
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')
class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid')
    up = models.BooleanField(verbose_name='是否赞')

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]

class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', null=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')


class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]



class Chat(models.Model):
    content = models.TextField(verbose_name="聊天内容")
    user = models.ForeignKey(verbose_name="用户",to='UserInfo',to_field='nid')
    creat_date = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

