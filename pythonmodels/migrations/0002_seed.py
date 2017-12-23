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
            data = pd.read_csv(os.path.join(pub_path, file))
        elif file.endswith('xlsx'):
            data = pd.read_excel(os.path.join(pub_path, file))

        # Save dataset to database
        dataset = Dataset.objects.create(
            name=file,
            file=os.path.join(pub_path, file),
            vars=data.shape[1],
            observations=data.shape[0],
        )

        # Save variables from new dataset to database
        newdataset = Dataset.objects.get(id=dataset.id)
        for column in data.columns.values:
            DatasetVariable.objects.create(dataset_id=newdataset, name=column)


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