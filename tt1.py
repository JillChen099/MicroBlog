#-*- coding=utf-8 -*-
'''
Created on 

@author:Eden
'''

import re
regex ='^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$'
print re.match(regex,'Xs12#$kL').group()

result = {'status': 'hide', 'message': {}, 'form': {}}
result['message'] = 123
print result.values()