from django.urls import include, path
from django.contrib import admin

from pythonmodels.views import register

urlpatterns = [
    path('', include('pythonmodels.urls')),
    path('admin/', admin.site.urls),

    # Logged in views
    path('home/', include('pythonmodels.urls'))


]
