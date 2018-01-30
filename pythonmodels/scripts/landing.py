from django.http import JsonResponse, HttpResponse
from numpy.random import randint
from pythonmodels.models import Dataset
from random import sample

import pandas as pd


def landing_charts(first_chart):
    """
    Get random data to populate landing page charts
    :return:
    """
    def highcharts(cols):
        dataset_ids = Dataset.objects.filter(user_id=None).values_list('id', flat=True)
        rand_dataset = randint(1, max(dataset_ids) + 1)
        dataset = Dataset.objects.get(pk=rand_dataset)
        df = pd.read_csv(dataset.file).dropna()
        df = df.select_dtypes(exclude='object')
        rand_cols = sample(list(df.columns.values), cols)
        df = df[rand_cols]
        df = df.to_json(orient='records')
        return HttpResponse(df)

    if first_chart:
        return highcharts(2)
    else:
        return highcharts(1)

