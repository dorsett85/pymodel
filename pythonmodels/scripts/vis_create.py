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

    x_df = df[[x_rq]]
    x_series = df[x_rq]
    x_dtype = df[x_rq].dtype

    # Check if variables are different
    if x_rq == request['yVar']:
        return form_errors('yVar', 'Variables must be different', 400)

    # Initialize dictionary to return as JSON
    json_dict = {}

    """
    Plots for numeric variables
    """
    if x_dtype in ['float64', 'int64']:

        # Highcharts density plot data
        kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
        kde.fit(x_df.values)
        dist_space = linspace(min(x_df.values), max(x_df.values), len(x_df.values))
        logprob = kde.score_samples(dist_space[:, None])
        x_den = pd.DataFrame({'space': dist_space, 'prob': exp(logprob)}).to_dict(orient='records')
        json_dict.update({'density': x_den})

        # Highcharts scatter and summary lines
        x_vals = pd.DataFrame({'space': x_df.index.values, 'value': x_df.iloc[:, 0]}).to_dict(orient='records')
        json_dict.update({
            'x_vals': x_vals, 'x_mean': x_db.mean, 'x_median': x_db.median, 'x_q1': x_db.Q1, 'x_q3': x_db.Q3
        })

    return JsonResponse(json_dict)


