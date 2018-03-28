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
        kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
        kde.fit(x_df.values)
        logprob = kde.score_samples(space[:, None])
        x_den = [(s, p) for s, p in zip(space, exp(logprob))]

        # Highcharts scatter and summary lines
        x_vals = [(s, v) for s, v in zip(range(x_series.size), x_series)]

        # Update json_dict
        json_dict.update({
            'x_den': x_den, 'x_vals': x_vals
        })
    else:
        return form_errors('xVar', 'Currently supports numeric variables only', 400)

    """
    Plots for categorical variables
    """

    return JsonResponse(json_dict)


