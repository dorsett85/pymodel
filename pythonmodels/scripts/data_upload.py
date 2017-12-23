from django.core import serializers
from django.http import HttpResponse
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
        doc = pd.DataFrame(data, columns=header)
    else:
        doc = pd.read_excel(file)

    # Save dataset
    dataset = form.save(commit=False)
    dataset.user_id = self.request.user
    dataset.name = file
    dataset.vars = doc.shape[1]
    dataset.observations = doc.shape[0]
    dataset.save()

    # Save variables from new dataset
    newdataset = Dataset.objects.get(id=dataset.id)
    for column in doc.columns.values:
        DatasetVariable.objects.create(dataset_id=newdataset, name=column)

    return HttpResponse(serializers.serialize('json', [newdataset,]), content_type='application/json')


