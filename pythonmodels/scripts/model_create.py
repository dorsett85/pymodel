from collections import OrderedDict
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from pythonmodels.models import Dataset
from sklearn.linear_model import LinearRegression

import numpy as np
import pandas as pd
import statsmodels.api as sm
import warnings


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

    # Return error if no predictor variables selected or response variable is in the predictor variables
    if not pred_vars:
        return JsonResponse(
            {'error': 'predictorVars', 'message': 'Select at least one predictor variable'},
            status=400
        )
    elif resp_var in pred_vars:
        return JsonResponse(
            {'error': 'predictorVars', 'message': 'Predictor variables cannot contain the response variable'},
            status=400
        )

    # Select columns based on user input, remove NaN's, create design matrix and add constant to predictor variables
    var_names = pred_vars + [resp_var]
    df_clean = pd_dat[var_names].dropna()
    df_x = pd.get_dummies(df_clean.drop(resp_var, axis=1))
    df_x = sm.add_constant(df_x).rename(columns={'const': '(Intercept)'})
    df_y = df_clean[resp_var]

    # Create correlation matrix
    corr_df = df_clean.corr().round(2)
    corr_matrix = corr_df.to_dict(orient='records')
    import json
    corr_matrix = json.loads(corr_df.to_json(orient='records'))
    print(df_clean.corr().to_json(orient='records'))
    print(corr_matrix)

    """
    Return model that user selected
    """

    # Simple linear regression
    if request['modelType'] == 'Simple Linear Regression':

        # Check for errors
        if df_y.dtype not in ['float64', 'int64']:
            return JsonResponse(
                {'error': 'responseVar', 'message': 'Response variable must be numeric for this model type'},
                status=400
            )

        # Fit model and get statistics output as dictionary
        lm_fit = sm.OLS(df_y, df_x).fit()

        stats = OrderedDict()
        stats['Observations'] = lm_fit.nobs
        stats['$r^2$'] = np.round(lm_fit.rsquared, 3)
        stats['adj $r^2$'] = np.round(lm_fit.rsquared_adj, 3)
        stats['mse'] = np.round(lm_fit.mse_model, 3)
        stats['aic'] = np.round(lm_fit.aic, 3)
        stats['bic'] = np.round(lm_fit.bic, 3)

        fit_vs_resid = pd.DataFrame({
            'pred': np.round(lm_fit.fittedvalues, 2),
            'resid': np.round(lm_fit.resid, 2)
        }).to_dict(orient='records')

        return JsonResponse({
            'model': 'ols',
            'stats': stats,
            'residual': fit_vs_resid,
            'corr_matrix': corr_matrix
        })

    # Multinomial logistic
    elif request['modelType'] == 'Multinomial Logistic':

        # Check for errors
        if df_y.dtype not in ['object']:
            return JsonResponse(
                {'error': 'responseVar', 'message': 'Response variable must be categorical'},
                status=400
            )

        # Loop through all fit methods until one doesn't cause a warning.  If none work, return an error message.
        with warnings.catch_warnings():
            warnings.simplefilter("error")

            for i in ['newton', 'nm', 'bfgs', 'lbfgs', 'powell', 'cg', 'ncg']:
                try:
                    mnlogit_fit = sm.MNLogit(df_y, df_x).fit(method=i)
                    np.round(mnlogit_fit.bse, 3)
                except Warning:
                    continue
                else:
                    break

            try:
                mnlogit_fit
                np.round(mnlogit_fit.bse, 3)
            except (NameError, Warning):
                return JsonResponse(
                    {'error': 'predictorVars',
                     'message': '8 algorithms tried and all contained warnings.  Try choosing variables with '
                                'fewer categorical levels, more numerical variables or another model type.'},
                    status=400
                )

        stats = OrderedDict()
        stats['Observations'] = mnlogit_fit.nobs
        stats['pseudo $r^2$'] = np.round(mnlogit_fit.prsquared, 3)
        stats['classification error'] = '{:.2%}'.format(np.round(np.mean(mnlogit_fit.resid_misclassified), 4))
        stats['aic'] = np.round(mnlogit_fit.aic, 3)
        stats['bic'] = np.round(mnlogit_fit.bic, 3)

        # fit_vs_resid = pd.DataFrame({
        #     'pred': np.round(mnlogit_fit.fittedvalues, 2),
        #     'resid': np.round(mnlogit_fit.resid, 2)
        # }).to_dict(orient='records')

        return JsonResponse({
            'model': 'mnlogit',
            'stats': stats,
            'residual': 1,
            'corr_matrix': corr_matrix
        })
