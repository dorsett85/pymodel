from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'pythonmodels'
urlpatterns = [

    # Landing pages
    path('', TemplateView.as_view(template_name='pythonmodels/landing_content/landing.html'), name='landing'),
    path('about/', TemplateView.as_view(template_name='pythonmodels/landing_content/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='pythonmodels/landing_content/contact.html'), name='contact'),

    path('polls/', views.IndexView.as_view(), name='polls'),
    path('polls/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('polls/<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('polls/<int:question_id>/vote/', views.vote, name='vote'),

    # Authentication and registration
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),

    # Logged in user
    path('home/<str:username>', views.UserIndex.as_view(), name='user_index'),

    path('home/<str:username>/upload/', views.DataUpload.as_view(), name='data_upload'),
    path('datasetdelete/<int:pk>', views.DatasetDelete.as_view(), name='dataset_delete'),

    path('home/<str:username>/create/', views.CreateModel.as_view(), name='model_create'),

    # Practice View
    path('practice/', views.Practice.as_view(), name='practice')

]
