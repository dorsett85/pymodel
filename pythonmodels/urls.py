from django.urls import path
from django.conf.urls import url

from . import views


app_name = 'pythonmodels'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/', views.PostView.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
