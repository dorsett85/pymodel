from django.contrib import admin

from .models import Question, Choice, Post

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Post)

