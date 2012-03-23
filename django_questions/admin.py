# -*- coding: utf-8 -*-
from django.contrib import admin
from django_questions.models import *

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('author_email', 'master', 'date_created')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
