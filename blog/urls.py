"""EdmureBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from blog.views import home

urlpatterns = [
    url(r'^article_updown/$', home.article_updown),
    url(r'^submit_comment/$', home.submit_comment),
    url(r'^delete_comment/$', home.delete_comment),
    url(r'^(?P<site>\w+).html$', home.home,name='article_home'),
    url(r'^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', home.filter,name='article_filter'),
    url(r'^(?P<site>\w+)/(?P<nid>\d+).html$', home.detail,name='article_detail'),
]
