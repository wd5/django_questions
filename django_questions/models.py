# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.template import Context, loader
from django.core.mail import send_mail

from django_questions.conf import settings


class GenericManager( models.Manager ):
    """
    Filters query set with given selectors
    """
    def __init__(self, **kwargs):
        super(GenericManager, self).__init__()
        self.selectors = kwargs

    def get_query_set(self):
        return super(GenericManager, self).get_query_set().filter( **self.selectors )


class Question(models.Model):
    """ Вопросы """
    author_email = models.CharField(verbose_name=u"Email автора", max_length=100)
    master = models.ForeignKey(User, null=True, blank=True, verbose_name=u"Кому задан вопрос", related_name="answered")
    content = models.TextField(verbose_name=u"Содержание")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=u"Дата создания")
    answer_count = models.IntegerField(default=0, verbose_name=u"Количество ответов", editable=False)

    objects = models.Manager()
    with_answer = GenericManager(answer_count__gt=0)
    without_answers = GenericManager(answer_count=0)

    def __unicode__(self): return self.content[:40]

    class Meta:
        verbose_name = u"вопрос"
        verbose_name_plural = u"вопросы"
        ordering = ['-date_created']

    def notify_master(self, template='email/new_question.html', from_email=None):
        if self.master:
            master = self.master
        elif settings.DEFAULT_ANSWER_USERNAME:
            master = User.objects.get(username=settings.DEFAULT_ANSWER_USERNAME)
        else:
            master = None

        if master:
            t = loader.get_template(template)
            subject, message = t.render(Context({})).split("\n", 1)
            master.email_user(subject, message, from_email)

    def notify_author(self, template='email/new_answer.html', from_email=None):
        t = loader.get_template(template)
        subject, message = t.render(Context({})).split("\n", 1)
        send_mail(subject, message, from_email, [self.author_email])


class Answer(models.Model):
    """ Ответы """
    author = models.ForeignKey(User, verbose_name=u"Автор")
    question = models.ForeignKey(Question, verbose_name=u"Вопрос")
    content = models.TextField(verbose_name=u"Содержание")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=u"Дата создания")
    last_modified = models.DateTimeField(auto_now=True, verbose_name=u"Дата последнего изменения")

    def __unicode__(self): return self.question.__unicode__() + ": " + self.content[:40]

    def save(self, *args, **kwargs):
        try:
            a = Answer.objects.get(pk=self.id)
        except Answer.DoesNotExist:
            self.question.answer_count += 1
            self.question.save()
        super(Answer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.question.answer_count -= 1
        self.question.save()
        super(Answer, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = u"Ответ"
        verbose_name_plural = u"Ответы"
        ordering = ['date_created']