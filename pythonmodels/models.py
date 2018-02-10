from django.contrib.auth.models import User
from django.db import models


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user_id.id, filename)


# Dataset model
class Dataset(models.Model):
    user_id = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text="What is the name of your dataset?")
    if user_id is not None:
        file = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    else:
        file = models.FileField(upload_to='public/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    vars = models.IntegerField()
    observations = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# DatasetVariable model
class DatasetVariable(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20)
    count = models.IntegerField()
    nan = models.IntegerField()
    mean = models.FloatField(blank=True, null=True)
    std = models.FloatField(blank=True, null=True)
    min = models.FloatField(blank=True, null=True)
    Q1 = models.FloatField(blank=True, null=True)
    median = models.FloatField(blank=True, null=True)
    Q3 = models.FloatField(blank=True, null=True)
    max = models.FloatField(blank=True, null=True)
    unique = models.IntegerField(blank=True, null=True)
    top = models.TextField(blank=True, null=True)
    freq = models.IntegerField(blank=True, null=True)
    first_date = models.DateTimeField(blank=True, null=True)
    last_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# StatModel model
class StatModel(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
