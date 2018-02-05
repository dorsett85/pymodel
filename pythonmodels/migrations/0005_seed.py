from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations
from pythonmodels.models import Dataset, DatasetVariable

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
        if file.endswith('csv'):
            df = pd.read_csv(os.path.join(pub_path, file))
        elif file.endswith('xlsx'):
            df = pd.read_excel(os.path.join(pub_path, file))

        # Save dataset to database
        newdataset = Dataset.objects.create(
            name=file,
            file=os.path.join(pub_path, file),
            vars=df.shape[1],
            observations=df.shape[0],
        )

        # Save variables from new dataset to database
        for column in df:
            col = df[column]
            col_info = col.describe()

            new_dataset_variable = DatasetVariable()
            new_dataset_variable.dataset_id = newdataset
            new_dataset_variable.name = col.name
            new_dataset_variable.count = col_info['count']
            new_dataset_variable.nan = col.isna().sum()

            if col.dtype in ['bool', 'O', 'datetime64[ns]']:
                if col.dtype == 'bool':
                    new_dataset_variable.type = 'boolean'
                if col.dtype == 'O':
                    new_dataset_variable.type = 'character'
                if col.dtype == 'datetime64[ns]':
                    new_dataset_variable.type = 'datetime'
                    new_dataset_variable.first_date = col_info['first']
                    new_dataset_variable.last_date = col_info['last']

                new_dataset_variable.unique = col_info['unique']
                new_dataset_variable.top = col_info['top']
                new_dataset_variable.freq = col_info['freq']

            elif col.dtype in ['float64', 'int64']:
                new_dataset_variable.type = 'numeric'
                new_dataset_variable.mean = col_info['mean']
                new_dataset_variable.std = col_info['std']
                new_dataset_variable.min = col_info['min']
                new_dataset_variable.Q1 = col_info['25%']
                new_dataset_variable.median = col_info['50%']
                new_dataset_variable.Q3 = col_info['75%']
                new_dataset_variable.max = col_info['max']

            new_dataset_variable.save()


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
