from __future__ import absolute_import
from braces import views
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic, View

from .models import Dataset, DatasetVariable
from .forms import LoginForm, RegistrationForm, DatasetUploadForm
from pythonmodels.Controllers.data_upload import datasetcreate

import os


class Register(views.AnonymousRequiredMixin, generic.CreateView):
    form_class = RegistrationForm
    model = User
    template_name = 'pythonmodels/registration/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super(Register, self).form_valid(form)

    def get_authenticated_redirect_url(self):
        return reverse('pythonmodels:user_index', args=(self.request.user.username,))

    def get_success_url(self):
        login_message = self.object.username + ', you have successfully logged in!'
        messages.success(self.request, login_message, 'loginFlash')
        return reverse('pythonmodels:user_index', args=(self.object.username,))


class Guest(View):
    def get(self, request):
        user = authenticate(username='Guest', password='guest')
        login(self.request, user)
        login_message = self.request.user.username + ', you have successfully logged in!'
        messages.success(self.request, login_message, 'loginFlash')
        return HttpResponseRedirect(reverse('pythonmodels:user_index', args=['Guest']))


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
        user = self.request.user.username
        logout(request)
        messages.info(self.request, user + ', you have successfully logged out!', 'logoutFlash')
        return super(Logout, self).get(request, *args, **kwargs)


class UserIndex(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = User
    template_name = 'pythonmodels/user_content/userIndex.html'

    def get_context_data(self, **kwargs):
        context = super(UserIndex, self).get_context_data()
        context['datasets'] = Dataset.objects.filter(user_id__id=self.request.user.id)
        context['public_datasets'] = Dataset.objects.filter(user_id__isnull=True)
        return context

    def get_success_url(self):
        return reverse('pythonmodels:data_upload', args=(self.request.user.username,))


class DataUpload(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    form_class = DatasetUploadForm
    template_name = 'pythonmodels/user_content/dataUpload.html'

    def get_form_kwargs(self):
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
            return datasetcreate(self, form)
        else:
            return super(DataUpload, self).form_valid(form)

    def get_success_url(self):
        return reverse('pythonmodels:data_upload', args=(self.request.user.username,))


class DatasetDelete(LoginRequiredMixin, generic.DeleteView):
    model = Dataset

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        dataset_id = self.object.pk
        self.object.delete()
        return JsonResponse({'id': dataset_id})


class CreateModel(generic.DetailView):
    template_name = 'pythonmodels/user_content/modelCreate.html'
    model = Dataset

    def get_context_data(self, **kwargs):
        context = super(CreateModel, self).get_context_data()
        context['urlDataset'] = get_object_or_404(Dataset, pk=self.kwargs['pk'])
        context['userDatasets'] = Dataset.objects.filter(user_id__id=self.request.user.id)
        context['publicDatasets'] = Dataset.objects.filter(user_id__isnull=True)
        print(context['urlDataset'])

        return context

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            variables_query = DatasetVariable.objects.filter(dataset_id__exact=self.kwargs['pk']).values_list('name')
            variables = [dat for dat in variables_query]
            print(variables)
            return JsonResponse(variables, safe=False)



class Practice(generic.View):

    def get(self, request, *args, **kwargs):
        os.makedirs('{0}/user_{1}'.format(settings.MEDIA_ROOT, self.request.user.id))
        return HttpResponse(self.request.user.username)
