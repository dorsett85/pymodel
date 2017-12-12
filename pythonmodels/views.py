from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Choice, Question, Post
from .forms import SignUpForm


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


class PostListView(generic.ListView):
    template_name = 'pythonmodels/landing_content/post_list.html'
    context_object_name = 'latest_post_list'

    def get_queryset(self):
        return Post.objects.filter(
            published_date__lte=timezone.now()
        ).order_by('-published_date')


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'pythonmodels/landing_content/post_detail.html'

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['user_list'] = User.objects.all()
        return context


class Login(generic.TemplateView):
    template_name = 'pythonmodels/registration/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        login(request, user)
        return HttpResponseRedirect(reverse('pythonmodels:home'))


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'pythonmodels/registration/registration.html', {'form': form})


class UserIndex(generic.ListView):
    model = User
    template_name = 'pythonmodels/user_content/userIndex.html'


class Practice(generic.View):
    def get(self, request):
        # <view logic>
        return HttpResponse('result')
