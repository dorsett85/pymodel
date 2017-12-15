from __future__ import absolute_import
from braces import views
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone

from .models import Choice, Question
from .forms import LoginForm, RegistrationForm


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
    authenticated_redirect_url = '/'
    form_class = RegistrationForm
    model = User
    template_name = 'pythonmodels/registration/register.html'

    def form_valid(self, form):
        valid = super(Register, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid

    def get_success_url(self):
        login_message = self.object.username + ', you have successfully logged in!'
        messages.success(self.request, login_message, 'loginFlash')
        return reverse('pythonmodels:user_index', args=(self.object.username,))


class Login(views.AnonymousRequiredMixin, generic.FormView):
    authenticated_redirect_url = '/'
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


class Practice(generic.View):
    def get(self, request):
        # <view logic>
        return HttpResponse('noonin')
