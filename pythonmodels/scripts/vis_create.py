from django.http import JsonResponse
from numpy import linspace, exp, round
from sklearn.neighbors import KernelDensity

from .helper_funs import form_errors
from pythonmodels.models import Dataset, DatasetVariable

import pandas as pd


def vis_create(request):

    # Get dataset
    dataset = Dataset.objects.get(pk=request['vis'])
    df = pd.read_pickle(dataset.file)

    # Define variable 1 objects
    x_rq = request['xVar']
    x_db = DatasetVariable.objects.filter(dataset_id=dataset).get(name=x_rq)
    x_df = df[[x_rq]].dropna()
    x_series = x_df[x_rq]
    x_dtype = x_series.dtype

    # Initialize dictionary to return as JSON
    json_dict = {}

    """
    Plots for numeric variables
    """
    if x_dtype in ['float64', 'int64']:

        if x_series.nunique() == 1:
            return form_errors('xVars', 'Select a variable with more than one value', status=400)

        # Highcharts density plot data
        space = linspace(min(x_series), max(x_series), len(x_series))
        kde = KernelDensity(bandwidth=1.0)
        kde.fit(x_df.values)
        prob = exp(kde.score_samples(space[:, None]))
        x_den = [(s, p) for s, p in zip(space, prob)]

        # Highcharts boxplot
        IQR = x_db.Q3 - x_db.Q1
        upper = max(x_series[x_series <= x_db.Q3 + (1.5 * IQR)])
        lower = min(x_series[x_series >= x_db.Q1 - (1.5 * IQR)])
        outliers = x_series[(x_series > upper) | (x_series < lower)]
        x_outliers = [[0, x] for x in outliers]
        boxplot = {
            'box': [[lower, x_db.Q1, x_db.median, x_db.Q3, upper]],
            'out': x_outliers
        }

        # Update json_dict
        json_dict.update({
            'x_den': x_den, 'x_box': boxplot
        })
        
    else:
        return form_errors('xVar', 'Currently supports numeric variables only', 400)

    """
    Plots for categorical variables
    """

    return JsonResponse(json_dict)


