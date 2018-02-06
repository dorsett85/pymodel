from pythonmodels.models import DatasetVariable


def new_dataset_variables(df, newdataset):
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
            new_dataset_variable.mean = col_info['mean']
            new_dataset_variable.std = col_info['std']
            new_dataset_variable.min = col_info['min']
            new_dataset_variable.Q1 = col_info['25%']
            new_dataset_variable.median = col_info['50%']
            new_dataset_variable.Q3 = col_info['75%']
            new_dataset_variable.max = col_info['max']

        new_dataset_variable.save()
