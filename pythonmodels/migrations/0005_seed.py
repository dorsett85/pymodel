from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations
from pythonmodels.models import Dataset
from pythonmodels.scripts.helper_funs import new_dataset_variables

import os
import pandas as pd
import shutil


def forwards_func(apps, schema_editor):
    # Create Clayton superuser and Guest user
    User = apps.get_model('auth', 'User')
    User.objects.create(username='Clayton', password=make_password('Phillydor85!'), is_superuser=True, is_staff=True)
    User.objects.create(username='Guest', password=make_password('guest'))

    # Create public datasets
    pub_path = os.path.join(settings.MEDIA_ROOT, 'public')

    for file in os.listdir(pub_path):
        df = pd.read_pickle(os.path.join(pub_path, file))

        if file.startswith('cars'):
            description = '<span class="font-weight-bold">Mileage per gallon performances of various cars.</span> - ' \
                          '<a href="https://www.kaggle.com/uciml/autompg-dataset" ' \
                          'target="_blank">Kaggle</a></h4>'
        elif file.startswith('iris'):
            description = '<span class="font-weight-bold">Classify iris plants into three species in ' \
                          'this classic dataset.</span> - ' \
                          '<a href="https://www.kaggle.com/uciml/iris" target="_blank">Kaggle</a>'
        elif file.startswith('wine'):
            description = '<span class="font-weight-bold">Simple and clean practice dataset for ' \
                          'regression or classification modelling.</span> - ' \
                          '<a href="https://www.kaggle.com/uciml/' \
                          'red-wine-quality-cortez-et-al-2009" target="_blank">Kaggle</a>' \

        # Save dataset to database
        newdataset = Dataset.objects.create(
            name=os.path.splitext(file)[0],
            description=description,
            file=os.path.join(pub_path, file),
            vars=df.shape[1],
            observations=df.shape[0],
        )

        # Save variables from new dataset to database
        new_dataset_variables(df, newdataset)


def reverse_func(apps, schema_editor):
    # Remove users and associated storage
    User = apps.get_model('auth', 'User')
    User.objects.all().delete()

    for dir in os.listdir(settings.MEDIA_ROOT):
        if dir.startswith('user'):
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, dir))


class Migration(migrations.Migration):
    dependencies = [
        ('pythonmodels', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
