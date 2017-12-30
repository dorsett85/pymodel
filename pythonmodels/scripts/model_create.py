from collections import OrderedDict
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from pythonmodels.models import Dataset
from sklearn.linear_model import LinearRegression

import numpy as np
import pandas as pd
import statsmodels.api as sm


def model_create_context(ModelCreate, self, **kwargs):
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

    # Load dataset to memory, get predictor and response variables
    dataset = Dataset.objects.get(pk=request['dataID'])
    if dataset.name.endswith('.csv'):
        pd_dat = pd.read_csv(dataset.file.path)
    else:
        pd_dat = pd.read_excel(dataset.file.path)

    pred_vars = request.getlist('predictorVars[]')
    resp_var = request['responseVar']

    # Return error if response variable is in the predictor variables
    if resp_var in pred_vars:
        return JsonResponse(
            {'predictor_error': 'Predictor variables cannot contain the response variable'},
            status=400
        )

    # Select columns based on user input, remove NaN's
    var_names = pred_vars + [resp_var]
    df_clean = pd.get_dummies(pd_dat[var_names].dropna())
    df_y = df_clean[resp_var]
    df_x = sm.add_constant(df_clean.drop(df_y.name, axis=1)).rename(columns={'const': '(Intercept)'})

    """
    Return model that user selected
    """

    # Simple linear regression
    if request['modelType'] == 'Simple Linear Regression':
        lm_fit = sm.OLS(df_y, df_x).fit()

        # Get table and plot output as dictionary
        coefs = pd.DataFrame(OrderedDict({
            '': lm_fit.params.index,
            'coef estimate': np.round(lm_fit.params, 3),
            'std error': np.round(lm_fit.bse, 3),
            't value': np.round(lm_fit.tvalues, 3),
            'p value': np.round(lm_fit.pvalues, 3)
        })).to_dict(orient='records')

        fit_vs_resid = pd.DataFrame({
            'pred': np.round(lm_fit.fittedvalues, 2),
            'resid': np.round(lm_fit.resid, 2)
        }).to_dict(orient='records')

        corr_matrix = df_clean.corr().to_dict(orient='records')

        return JsonResponse({'residual': fit_vs_resid, 'coefs': coefs, 'corr_matrix': corr_matrix})
