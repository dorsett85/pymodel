from django.http import JsonResponse
from numpy import round
from pythonmodels.models import Dataset, DatasetVariable


def new_dataset_variables(df, newdataset):

    # Loop over columns to get summary metrics
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
            if col_info['count'] != 0:
                new_dataset_variable.mean = round(col_info['mean'], 3)
                new_dataset_variable.std = round(col_info['std'], 3)
                new_dataset_variable.min = round(col_info['min'], 3)
                new_dataset_variable.Q1 = round(col_info['25%'], 3)
                new_dataset_variable.median = round(col_info['50%'], 3)
                new_dataset_variable.Q3 = round(col_info['75%'], 3)
                new_dataset_variable.max = round(col_info['max'], 3)

        new_dataset_variable.save()


def dataset_description(dataset_id, description):
    data = Dataset.objects.get(pk=dataset_id)
    data.description = description
    data.save()

    return JsonResponse({
        'datasetFormID': 'dataset_' + str(dataset_id),
        'datasetDescrip': description
    })
