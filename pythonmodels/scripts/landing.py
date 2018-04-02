from django.http import JsonResponse
from numpy import histogram, linspace, round, exp
from random import sample
from sklearn.neighbors import KernelDensity

from pythonmodels.models import Dataset

import pandas as pd


def landing_charts():
    """
    Get random data to populate landing page charts
    :return: json of dataset variables data
    """
    # Get random non-user dataset
    non_user_datasets = Dataset.objects.raw('SELECT id, file FROM pythonmodels_dataset WHERE user_id_id IS NULL')
    df_path = sample([x.file for x in non_user_datasets], 1)[0]
    df = pd.read_pickle(df_path).dropna()

    # Numeric columns
    num_cols = df.select_dtypes(include='float64').columns.tolist()
    df_num = df[sample(num_cols, 2)]

    # Int and Character columns (change values if it's wine quality)
    non_num_cols = df.select_dtypes(include=['int64', 'object']).columns.tolist()
    cat_cols = [col for col in non_num_cols if len(df[col].unique()) <= 6]
    cat_col = sample(cat_cols, 1)[0]
    df_cat = df[cat_col]
    if len(df_cat.unique()) == 6:
        df_cat = df_cat.apply(lambda x: 'poor' if x <= 4 else 'average' if x <= 6 else 'excellent')

    # Combine columns
    df = pd.concat((df_num, df_cat), axis=1)

    # Define column names
    x_var = df.columns.values[0]
    y_var = df.columns.values[1]

    # Define unique categories and coloring
    cats = df[cat_col].unique()
    cat_colors = [
        'rgba(73, 191, 238, 0.75)',
        'rgba(0, 230, 0, 0.75)',
        'rgba(255, 51, 0, 0.75)',
        'rgba(228, 228, 51, 0.75)',
        'rgba(130, 5, 172, 0.75)'
    ]
    cat_colors = cat_colors[0:len(cats)]

    # Get chart data
    scat_series_list = []
    den_series_list = []
    for cat, color in zip(cats, cat_colors):

        # Subset dataframe
        df_cat = df[df[cat_col] == cat]

        # Highcharts scatter plot data
        points = [(float(x), float(y)) for x, y in zip(df_cat[x_var], df_cat[y_var])]
        scat_series_list.append({'name': str(cat), 'color': color, 'data': points})

        # Highcharts density plot data
        kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
        kde.fit(df_cat[[x_var]].values)
        dist_space = linspace(min(df_cat[x_var].values), max(df_cat[x_var].values), len(df_cat[x_var].values))
        logprob = kde.score_samples(dist_space[:, None])
        points = [(float(s), float(exp(p))) for s, p in zip(dist_space, logprob)]
        den_series_list.append({'name': str(cat), 'color': color, 'data': points})

    # Highcharts histogram data
    count, bins = histogram(df[x_var])
    space = linspace(min(bins), max(bins), len(count))
    bins = round(bins, 3)
    bins = ['{0} - {1}'.format(bins[x], bins[x + 1]) for x in range(len(bins)) if x < len(bins) - 1]
    hist = [{'x': float(s), 'y': float(c), 'range': b} for s, c, b in zip(space, count, bins)]

    # Return Json
    return JsonResponse({
        'x_var': x_var,
        'y_var': y_var,
        'cat_var': cat_col,
        'scatter': scat_series_list,
        'hist': hist,
        'den': den_series_list
    })


