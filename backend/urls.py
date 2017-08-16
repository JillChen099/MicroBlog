from django.conf.urls import url
from django.conf.urls import include
from views import category,index,article,base_info,tags

urlpatterns = [
    url(r'^index.html$', index.index),
    url(r'^base-info.html$', base_info.base_info),
    url(r'^change-password.html$', base_info.change_password),

    url(r'^tag.html$', tags.tag, name='tag'),
    url(r'^change-tag.html$', tags.change_tag),
    url(r'^delete-tag.html$', tags.delete_tag),
    url(r'^add-tag.html$', tags.add_tag),

    url(r'^category.html$', category.category, name='category'),
    url(r'^change-category.html$', category.change_category),
    url(r'^delete-category.html$', category.delete_category),
    url(r'^add-category.html$', category.add_category),

    url(r'^article-(?P<article_type_id>\d+)-(?P<category_id>\d+).html$', article.article, name='article'),
    url(r'^add-article.html$', article.add_article),
    url(r'^delete-article.html$', article.delete_article),
    url(r'^edit-article-(?P<nid>\d+).html$', article.edit_article),
    url(r'^upload-avatar.html$', base_info.upload_avatar),
    url(r'^upload_images/$', article.upload_images),

]
