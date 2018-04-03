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
    df_paths = sample([x.file for x in non_user_datasets], 2)

    # Function to get category column
    def get_chart_data(file, scatter=True):
        """Get category column"""

        # Read in data
        df = pd.read_pickle(df_paths[file]).dropna()

        # Int and Character columns (change values if it's wine quality)
        non_num_cols = df.select_dtypes(include=['int64', 'object']).columns.tolist()
        if 'Cylinders' in non_num_cols:
            non_num_cols.remove('Cylinders')
        cat_cols = [col for col in non_num_cols if len(df[col].unique()) <= 6]
        cat_col = sample(cat_cols, 1)[0]
        df_cat = df[cat_col]
        if len(df_cat.unique()) == 6:
            df_cat = df_cat.apply(lambda x: 'poor' if x <= 4 else 'average' if x <= 6 else 'excellent')

        # Numeric columns
        num_cols = df.select_dtypes(include='float64').columns.tolist()
        if scatter:
            df_num = df[sample(num_cols, 2)]
        else:
            den_cols = ['MPG', 'free sulfur dioxide', 'Displacement', 'fixed acidity',
                        'total sulfur dioxide', 'alcohol', 'Sepal.Length']
            den_list = [col for col in num_cols if col in den_cols]
            den_col = sample(den_list, 1)[0]
            df_num = df[den_col]

        # Combine columns
        df = pd.concat((df_num, df_cat), axis=1)

        # Define column names
        x_var = df.columns.values[0]
        if scatter:
            y_var = df.columns.values[1]
            cat_var = df.columns.values[2]
        else:
            cat_var = df.columns.values[1]

        # Define unique categories and coloring
        cats = df_cat.unique()
        cat_colors = [
            'rgba(230, 255, 255, 0.75)',
            'rgba(26, 117, 255, 0.75)',
            'rgba(26, 255, 26, 0.75)',
            'rgba(255, 255, 26, 0.75)',
            'rgba(255, 117, 26, 0.75)',
            'rgba(210, 77, 255, 0.75)'
        ]
        cat_colors = cat_colors[:3] if scatter else cat_colors[3:]

        # Get chart series object data
        scat_series_list = []
        den_series_list = []
        for cat, color in zip(cats, cat_colors):

            # Subset dataframe
            df_cat = df[df[cat_col] == cat]

            if scatter:
                # Highcharts scatter plot data
                points = [(float(x), float(y)) for x, y in zip(df_cat[x_var], df_cat[y_var])]
                scat_series_list.append({'name': str(cat), 'color': color, 'data': points})

            else:
                # Highcharts density plot data
                kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
                kde.fit(df_cat[[x_var]].values)
                dist_space = linspace(min(df_cat[x_var].values), max(df_cat[x_var].values), len(df_cat[x_var].values))
                logprob = kde.score_samples(dist_space[:, None])
                points = [(float(s), float(exp(p))) for s, p in zip(dist_space, logprob)]
                den_series_list.append({'name': str(cat), 'color': color, 'data': points})

        if scatter:
            return {'x_var': x_var, 'y_var': y_var, 'cat_var': cat_var, 'points': scat_series_list}
        else:
            return {'x_var': x_var, 'cat_var': cat_var, 'points': den_series_list}

    # Define scatter and density objects for highcharts
    scatter = get_chart_data(0, scatter=True)
    print(scatter)
    density = get_chart_data(1, scatter=False)

    # Return Json
    return JsonResponse({
        'scatter': scatter,
        'density': density
    })


