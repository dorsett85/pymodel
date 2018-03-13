from django.conf import settings
from django.http import JsonResponse
from pythonmodels.models import Dataset
from pythonmodels.scripts.helper_funs import new_dataset_variables
import csv
import io
import pandas as pd
import os

from copy import copy


def datasetcreate(self, form):
    file = form.cleaned_data['file']

    # Define path to save dataset as pkl
    # Create user directory if it doesn't exist
    user_path = os.path.join(settings.MEDIA_ROOT, 'user_{0}'.format(self.request.user.id))
    file_name = '{0}.pkl'.format(os.path.splitext(file.name)[0])
    file_path = os.path.join(user_path, file_name)
    if not os.path.exists(user_path):
        os.makedirs(user_path)

    # Check if file is .csv or .xlsx and read file into Pandas dataframe
    # Check for delimiter if file is csv and process
    if file.name.endswith('.csv'):
        csv_file = io.TextIOWrapper(copy(file))
        dialect = csv.Sniffer().sniff(csv_file.read(), delimiters=";,\t|")
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect)
        data = []

        for row in reader:
            data.append(row)

        header = data[0]
        df = pd.DataFrame(data[1:], columns=header)

        # Save and load csv to remove quotes when reading Pandas dataframe
        file_csv_path = os.path.join(user_path, file_name)
        df.to_csv(file_csv_path, index=False)
        df = pd.read_csv(file_csv_path)

        # Delete csv file as it will be saved as pkl
        os.remove(file_csv_path)

    else:
        df = pd.read_excel(file)

    # Save dataset to user directory
    df.to_pickle(file_path)

    # Save dataset to database
    newdataset = form.save(commit=False)
    newdataset.user_id = self.request.user
    newdataset.name = os.path.splitext(file.name)[0]
    newdataset.file = file_path
    newdataset.vars = df.shape[1]
    newdataset.observations = df.shape[0]
    newdataset.save()

    # Reload dataset if it's a csv to get appropriate dtypes
    if file.name.endswith('.csv'):
        df = pd.read_pickle(newdataset.file.path)

    # Save variables from new dataset
    new_dataset_variables(df, newdataset)

    # Get dataset variable data
    newdataset = Dataset.objects.get(id=newdataset.id)

    return JsonResponse({
        'pk': newdataset.id,
        'name': newdataset.name,
        'vars': newdataset.vars,
        'observations': newdataset.observations,
    })
