# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext, Context, loader

from django_questions.conf import settings
from django_questions.models import *
from django_questions.forms import *

def render_to_response(request, template_name, context_dict={}, cookies={}):
    context = RequestContext(request, context_dict)
    t = loader.get_template(template_name)
    response = HttpResponse(t.render(context))
    for k, v in cookies.items():
        response.set_cookie(k, v)
    return response


def questions(request, form_class=QuestionForm, template='templates/questions.html'):
    if request.POST.get('action'):
        form = form_class(request.POST)
        if form.is_valid():
            question = form.save()
            question.notify_master()
            return HttpResponseRedirect(reverse('questions')+"?save=ok")
    else:
        form = form_class()

    context = {'questions': Question.with_answer.all(),
               'save': request.GET.get('save'),
               'form': form
               }
    return render_to_response(request, 'questions.html', context)


def master_login_required(func):
    """ Проверяет, что текущий пользователь имеет право отвечать на вопросы """
    def wrapper(request, *args, **kwargs):
        if request.user.has_perm(settings.CAN_ANSWER_PERM_CODENAME):
            return func(request, *args, **kwargs)
        else:
            raise Http404()
    return wrapper

@master_login_required
def answers(request, form_class=AnswerForm, template='templates/answers.html'):
    if request.POST.get('action'):
        form = form_class(request.POST)
        if form.is_valid():
            form.save(request.user)
            form.cleaned_data['question'].notify_author()
            return HttpResponseRedirect(reverse('answers')+"?save=ok")

    else:
        form = form_class()

    context = {'questions': Question.without_answers.all(),
               'save': request.GET.get('save'),
               'form': form
               }
    for q in context['questions']:
        if str(q.id) == request.POST.get('question'):
            q.answer_form = form
        else:
            q.answer_form = form_class(initial={'question': q.id})
    return render_to_response(request, 'answers.html', context)
