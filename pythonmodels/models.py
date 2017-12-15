import datetime

from django.db import models
from django.utils import timezone


# Dataset model
class Dataset(models.Model):
    user_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=200)
    description = models.TextField()
    vars = models.IntegerField()
    observations = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now())
    updated_date = models.DateTimeField()

    def update(self):
        self.updated_date = timezone.now()
        self.save()


# DatasetVariable model
class DatasetVariable(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now())
    updated_date = models.DateTimeField()

    def update(self):
        self.updated_date = timezone.now()
        self.save()


# StatModel model
class StatModel(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now())
    updated_date = models.DateTimeField()

    def update(self):
        self.updated_date = timezone.now()
        self.save()


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

