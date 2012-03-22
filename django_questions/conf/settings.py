# -*- coding: utf-8 -*-

from django.conf import settings

# Код разрешения для добаввения ответов на вопросы
CAN_ANSWER_PERM_CODENAME = getattr(settings, 'DJANGO_QUESTIONS_CAN_ANSWER_PERM_CODENAME', 'django_questions.add_answer')

# Пользователь, которому отсылается письмо о новом вопросе, если не выбран конкретный отвечающий 
DEFAULT_ANSWER_USERNAME = getattr(settings, 'DJANGO_QUESTIONS_CAN_ANSWER_PERM', None)
