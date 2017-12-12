from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib import admin

from pythonmodels.views import register

urlpatterns = [
    path('', include('pythonmodels.urls')),
    path('admin/', admin.site.urls),

    # Authentication and registration
    path('login/', auth_views.login, {'template_name': 'pythonmodels/registration/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('register/', register, name='register'),

    # Logged in views
    path('home/', include('pythonmodels.urls'))


]
