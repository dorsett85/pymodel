# Generated by Django 2.0 on 2017-12-12 03:03

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('pythonmodels', '0002_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=50)),
                ('path', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('vars', models.IntegerField()),
                ('observations', models.IntegerField()),
                ('created_date', models.DateTimeField(default=datetime.datetime(2017, 12, 12, 3, 3, 7, 762814, tzinfo=utc))),
                ('updated_date', models.DateTimeField()),
            ],
        ),
    ]
