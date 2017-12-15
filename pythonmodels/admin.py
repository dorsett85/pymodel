from django.contrib import admin

from .models import Question, Choice, Dataset, DatasetVariable, StatModel

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Dataset)
admin.site.register(DatasetVariable)
admin.site.register(StatModel)
