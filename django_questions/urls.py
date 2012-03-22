# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',    
    url(r'^answers', answers, name='answers'),
    url(r'^$', questions, name='questions'),    
    )