from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'pythonmodels'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),

    # Authentication and registration
    path('login/', views.Login.as_view(), name='login'),
    # path('login/', auth_views.login, {'template_name': 'pythonmodels/registration/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('register/', views.register, name='register'),

    # Logged in user
    path('', views.UserIndex.as_view(), name='user_index'),

    # Practice View
    path('practice/', views.Practice.as_view())

]
