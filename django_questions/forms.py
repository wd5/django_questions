# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup, Comment

from django.contrib.auth.models import User, Permission
from django.forms import *
from django.db.models import Q

from django_questions.models import Question, Answer
from django_questions.conf import settings

def sanitizeHTML(value, mode='none'):
    """ Удаляет из value html-теги. 
        Если mode==none - все теги
        Если mode==strict - все теги кроме разрешенных
    """
    if mode == 'strict':
        valid_tags = 'p i strong b u a h1 h2 h3 pre br div span img blockquote glader youtube cut blue object param embed'.split()
    else:
        valid_tags = []
    valid_attrs = 'href src pic user page class text title alt'.split()
    # параметры видеороликов
    valid_attrs += 'width height classid codebase id name value flashvars allowfullscreen allowscriptaccess quality src type bgcolor base seamlesstabbing swLiveConnect pluginspage'.split()

    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                     if attr in valid_attrs]
    result = soup.renderContents().decode('utf8')
    return result


def get_answerer_list():
    try:
        perm = Permission.objects.get(codename=settings.CAN_ANSWER_PERM_CODENAME.split('.')[1])
        return User.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm) ).distinct()
    except Permission.DoesNotExist:
        raise ValueError("Permission with codename '%s' does not exist. Check %s in your settings file." % (settings.CAN_ANSWER_PERM_CODENAME, settings.CAN_ANSWER_PERM_CODENAME) )

class QuestionForm(Form):
    master = IntegerField(label=u"Кому", help_text=u"От кого бы вы хотели услышать ответ на вопрос",
                          error_messages={'required': u'Вы воспользовались неверной ссылкой. Вернитесь на предыдущую страницу и попробуйте еще раз.'},
                          widget=Select(),
                          initial=0
                          )
    content = CharField(label=u"Вопрос", error_messages={'required': u'Введите текст вопроса.'},
                        widget=TextInput()) 
    
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = [(0, u"неважно")] + [ (u.pk, u.get_full_name()) for u in get_answerer_list() ] 
        self.fields['master'].widget.choices = choices
    
    def clean_master(self):
        if self.cleaned_data['master']:
            try:
                return User.objects.get(pk=self.cleaned_data['master'])
            except User.DoesNotExist:
                raise ValidationError(u"Выбран отвечающий, неизвестный сайту")
        return None
    
    def clean_content(self):
        return sanitizeHTML(self.cleaned_data['content'])
    
    def save(self, user):
        return Question.objects.create(author=user, 
                                       master=self.cleaned_data['master'], 
                                       content=self.cleaned_data['content'])


class AnswerForm(Form):
    question = IntegerField(label=u"Вопрос", widget=HiddenInput())
    content = CharField(label=u"Ответ", error_messages={'required': u'Введите текст ответа.'},
                        widget=Textarea(attrs={'cols':60, 'rows':5})) 
    
    def clean_question(self):
        try:
            return Question.objects.get(pk=self.cleaned_data['question'])
        except Question.DoesNotExist:
            raise ValidationError(u"Неизвестный код вопроса")

    def save(self, user):
        return Answer.objects.create(author=user, 
                                     question=self.cleaned_data['question'], 
                                     content=self.cleaned_data['content'])