from __future__ import absolute_import
from braces import views
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone

from .models import Choice, Question, Dataset
from .forms import LoginForm, RegistrationForm, DatasetForm

import os
from django.conf import settings


class IndexView(generic.ListView):
    template_name = 'pythonmodels/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'pythonmodels/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'pythonmodels/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'pythonmodels/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('pythonmodels:results', args=(question.id,)))


class Register(views.AnonymousRequiredMixin, generic.CreateView):
    form_class = RegistrationForm
    model = User
    template_name = 'pythonmodels/registration/register.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return super(Register, self).form_valid(form)

    def get_authenticated_redirect_url(self):
        return reverse('pythonmodels:user_index', args=(self.request.user.username,))

    def get_success_url(self):
        login_message = self.object.username + ', you have successfully logged in!'
        messages.success(self.request, login_message, 'loginFlash')
        return reverse('pythonmodels:user_index', args=(self.object.username,))


class Login(views.AnonymousRequiredMixin, generic.FormView):
    form_class = LoginForm
    template_name = 'pythonmodels/registration/login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super(Login, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def get_authenticated_redirect_url(self):
        return reverse('pythonmodels:user_index', args=(self.request.user.username,))

    def get_success_url(self):
        login_message = self.request.user.username + ', you have successfully logged in!'
        messages.success(self.request, login_message, 'loginFlash')
        return reverse('pythonmodels:user_index', args=(self.request.user.username,))


class Logout(LoginRequiredMixin, generic.RedirectView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    url = reverse_lazy('pythonmodels:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(self.request, 'You have successfully logged out!', 'logoutFlash')
        return super(Logout, self).get(request, *args, **kwargs)


class UserIndex(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = User
    template_name = 'pythonmodels/user_content/userIndex.html'


class DataUpload(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    form_class = DatasetForm
    model = Dataset
    template_name = 'pythonmodels/user_content/dataUpload.html'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(DataUpload, self).get_form_kwargs()
        kwargs['user'] = self.request.user.id
        return kwargs

    def form_invalid(self, form):
        response = super(DataUpload, self).form_invalid(form)
        if self.request.is_ajax():
            print(form.errors.as_data())
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        if self.request.is_ajax:
            file = form.cleaned_data['file']
            dataset = form.save(commit=False)
            dataset.user_id = self.request.user
            dataset.name = file
            dataset.vars = 12
            dataset.observations = 200
            dataset.save()
            return JsonResponse({'success': 'worked'})
        else:
            return super(DataUpload, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DataUpload, self).get_context_data()
        context['datasets'] = Dataset.objects.filter(user_id__id=self.request.user.id)
        context['public_datasets'] = Dataset.objects.filter(user_id__isnull=True)
        return context

    def get_success_url(self):
        return reverse('pythonmodels:data_upload', args=(self.request.user.username,))


class CreateModel(generic.View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({'Create': 'this will be the create page'})


class Practice(generic.View):

    def get(self, request, *args, **kwargs):
        os.makedirs('{0}/user_{1}'.format(settings.MEDIA_ROOT, self.request.user.id))
        return HttpResponse(self.request.user.username)
