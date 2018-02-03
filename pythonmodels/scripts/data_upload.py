from django.http import JsonResponse
from pythonmodels.models import Dataset, DatasetVariable
import csv
import io
import pandas as pd


def datasetcreate(self, form):
    file = form.cleaned_data['file']

    # Check if file is .csv or .xlsx and put file in Pandas df
    if file.name.endswith('.csv'):
        csv_file = io.TextIOWrapper(file)
        dialect = csv.Sniffer().sniff(csv_file.read(), delimiters=";,")
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect)
        data = []

        for row in reader:
            data.append(row)

        header = data[0]
        df = pd.DataFrame(data, columns=header)
    else:
        df = pd.read_excel(file)

    # Save dataset
    dataset = form.save(commit=False)
    dataset.user_id = self.request.user
    dataset.name = file
    dataset.vars = df.shape[1]
    dataset.observations = df.shape[0]
    dataset.save()

    # Reload dataset if it's a csv to get appropriate dtypes
    if file.name.endswith('.csv'):
        df = pd.read_csv(dataset.file.path)

    # Save variables from new dataset
    newdataset = Dataset.objects.get(id=dataset.id)
    for column in df:
        if df[column].dtype == 'O':
            var_type = 'chartacter'
        elif df[column].dtype in ['float64', 'int64']:
            var_type = 'numeric'
        elif df[column].dtype == 'datetime64[ns]':
            var_type = 'datetime'
        DatasetVariable.objects.create(dataset_id=newdataset, name=column, type=var_type)

    # Get dataset variable data
    df_vars = DatasetVariable.objects.filter(dataset_id=newdataset).values('id', 'name', 'type')
    var_info = {value['id']: {'name': value['name'], 'type': value['type']} for value in df_vars}

    return JsonResponse({
        'pk': newdataset.id,
        'name': newdataset.name,
        'vars': newdataset.vars,
        'observations': newdataset.observations,
        'var_info': var_info
    })
