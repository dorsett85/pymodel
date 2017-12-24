from django.db.models import Q
from django.shortcuts import get_object_or_404
from pythonmodels.models import Dataset

import matplotlib.pyplot as plt
import os
import pandas as pd


def modelcreatecontext(ModelCreate, self, **kwargs):
    context = super(ModelCreate, self).get_context_data()

    # If url pk is 0, change it to 1
    self.kwargs['pk'] = 1 if self.kwargs['pk'] == 0 else self.kwargs['pk']

    # Get all user datasets, and all public datasets
    context['userDatasets'] = Dataset.objects.filter(user_id__id=self.request.user.id)
    context['publicDatasets'] = Dataset.objects.filter(user_id__isnull=True)

    # Check if the url pk parameter is not in user's or public datasets then get url dataset
    url_pk = Q(pk=self.kwargs['pk'])
    user_pk = Q(user_id__id=self.request.user.id)
    user_null = Q(user_id__isnull=True)
    context['urlDataset'] = get_object_or_404(Dataset, (url_pk & (user_pk | user_null)))

    return context


def pythonmodel(request):
    dataset = Dataset.objects.get(pk=request['dataID'])
    if dataset.name.endswith('.csv'):
        pd_dat = pd.read_csv(dataset.file.path)
    else:
        pd_dat = pd.read_excel(dataset.file.path)
    # print(pd_dat[request['responseVar']])



    return pd_dat
