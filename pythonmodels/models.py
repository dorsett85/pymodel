from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import datetime


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user_id.id, filename)


# Dataset model
class Dataset(models.Model):
    user_id = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, help_text="What is the name of your dataset?")
    if user_id is not None:
        file = models.FileField(upload_to=user_directory_path)
    else:
        file = models.FileField(upload_to='public/')
    description = models.TextField(blank=True, null=True)
    vars = models.IntegerField()
    observations = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self. name


# DatasetVariable model
class DatasetVariable(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self. name


# StatModel model
class StatModel(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

