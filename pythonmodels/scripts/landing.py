from django.http import JsonResponse
from numpy import histogram, linspace, round
from numpy.random import randint
from pythonmodels.models import Dataset
from random import sample

import pandas as pd


def landing_charts(first_chart):
    """
    Get random data to populate landing page charts
    :return: json of dataset variables data
    """
    def highcharts(cols):
        dataset_ids = Dataset.objects.filter(user_id=None).values_list('id', flat=True)
        rand_dataset = randint(1, max(dataset_ids) + 1)
        dataset = Dataset.objects.get(pk=rand_dataset)
        df = pd.read_pickle(dataset.file).dropna()
        df = df.select_dtypes(exclude='object')
        rand_cols = sample(list(df.columns.values), cols)
        df = df[rand_cols]

        # Initialize dictionary to return as JSON
        json_dict = {}

        # Add to json_dict depending on chart type
        if cols == 1:

            # Highcharts histogram data
            count, bins = histogram(df)
            space = linspace(min(bins), max(bins), len(count))
            bins = round(bins, 3)
            bins = ['{0} - {1}'.format(bins[x], bins[x + 1]) for x in range(len(bins)) if x < len(bins) - 1]
            df_hist = pd.DataFrame({'count': count, 'space': space, 'bins': bins})
            df_hist = df_hist.to_dict(orient='records')
            json_dict.update({'hist': df_hist, 'var': rand_cols})

        else:

            # Highcharts scatter plot data
            df = df.astype(float)
            df = df.to_dict(orient='records')
            json_dict.update({'scatter': df})

        return JsonResponse(json_dict)

    if first_chart:
        return highcharts(2)
    else:
        return highcharts(1)

