from django.http import JsonResponse
from pythonmodels.models import Dataset
from pythonmodels.scripts.helper_funs import new_dataset_variables
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
    newdataset = form.save(commit=False)
    newdataset.user_id = self.request.user
    newdataset.name = file
    newdataset.vars = df.shape[1]
    newdataset.observations = df.shape[0]
    newdataset.save()

    # Reload dataset if it's a csv to get appropriate dtypes
    if file.name.endswith('.csv'):
        df = pd.read_csv(newdataset.file.path)

    # Save variables from new dataset
    new_dataset_variables(df, newdataset)

    # Get dataset variable data
    newdataset = Dataset.objects.get(id=newdataset.id)
    vars_query = newdataset.datasetvariable_set.all().values()
    var_info = {}
    for i in vars_query:
        var_info.update({i['id']: {key: value for (key, value) in i.items()}})
    print(var_info)

    return JsonResponse({
        'pk': newdataset.id,
        'name': newdataset.name,
        'vars': newdataset.vars,
        'observations': newdataset.observations,
        'var_info': var_info
    })
