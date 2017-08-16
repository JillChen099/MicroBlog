#!/usr/bin/env python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup


class XSSFilter(object):
    __instance = None

    def __init__(self):
        # XSS白名单
        self.valid_tags = {
            "font": ['color', 'size', 'face', 'style'],
            'b': [],
            'div': [],
            "span": [],
            "table": [
                'border', 'cellspacing', 'cellpadding'
            ],
            'th': [
                'colspan', 'rowspan'
            ],
            'td': [
                'colspan', 'rowspan'
            ],
            "a": ['href', 'target', 'name'],
            "img": ['src', 'alt', 'title'],
            'p': [
                'align'
            ],
            "pre": ['class'],
            "hr": ['class'],
            'strong': []
        }
        self.novaild_tags ={
            'script':[]

        }

    def __new__(cls, *args, **kwargs):
        """
        单例模式  #每次对html表单进行过滤，无需每次都创建新的对象，因为内部封装的值和方法都一样。
        :param cls:
        :param args:
        :param kwargs:
        :return:
        """
        if not cls.__instance:
            obj = object.__new__(cls, *args, **kwargs)
            cls.__instance = obj
        return cls.__instance

    def process(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        # 遍历所有HTML标签
        for tag in soup.find_all(recursive=True):
            # 判断标签名是否在白名单中
            if tag.name  in self.novaild_tags:
                tag.hidden = True
                if tag.name not in ['html', 'body']:
                    tag.hidden = True
                    tag.clear()
                continue
            # 当前标签的所有属性白名单
            # attr_rules = self.valid_tags[tag.name]
            # keys = list(tag.attrs.keys())  #为什么要转化成列表？
            # for key in keys:
            #     if key not in attr_rules:
            #         del tag[key]

        return soup.decode()


if __name__ == '__main__':
    html = """<p class="title">
                        <b>The Dormouse's story</b>
                    </p>
                    <p class="story">
                        <div name='root'>
                            Once upon a time there were three little sisters; and their names were
                            <a href="http://example.com/elsie" class="sister c1" style='color:red;background-color:green;' id="link1"><!-- Elsie --></a>
                            <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
                            <a href="http://example.com/tillie" class="sister" id="link3">Tilffffffffffffflie</a>;
                            and they lived at the bottom of a well.
                            <script>alert(123)</script>
                        </div>
                    </p>
                    <p class="story">...</p>"""

    obj = XSSFilter()
    v = obj.process(html)
    print(v)
