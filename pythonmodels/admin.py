from django.contrib import admin

from .models import Dataset, DatasetVariable, StatModel

admin.site.register(Dataset)
admin.site.register(DatasetVariable)
admin.site.register(StatModel)
