#-*- coding=utf-8 -*-
'''
Created on 

@author:Eden
'''

from django.conf.urls import url
from webchat  import views


urlpatterns = [
                  url(r'^page_down/', views.page_down),
                  url(r'^summit_chat/', views.summit_chat),
                  url(r'^get_chat_first/', views.get_chat_first),
                  url(r'^get_chat/', views.get_chat),
                  url(r'^get_users_status/', views.get_users_status),
                  url(r'^', views.webchat_index),

]
