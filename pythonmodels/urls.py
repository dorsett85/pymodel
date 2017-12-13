from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views

app_name = 'pythonmodels'
urlpatterns = [

    # Landing pages
    path('', TemplateView.as_view(template_name='pythonmodels/landing_content/landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='pythonmodels/landing_content/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='pythonmodels/landing_content/contact.html'), name='contact'),

    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),

    path('polls/', views.IndexView.as_view(), name='polls'),
    path('polls/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('polls/<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('polls/<int:question_id>/vote/', views.vote, name='vote'),

    # Authentication and registration
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('register/', views.register, name='register'),

    # Logged in user
    path('home/<str:username>', views.UserIndex.as_view(), name='user_index'),

    # Practice View
    path('practice/', views.Practice.as_view())

]
