from collections import OrderedDict
from django.http import JsonResponse
from pythonmodels.models import Dataset

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, classification_report
from sklearn.model_selection import cross_val_score, cross_validate, cross_val_predict, GridSearchCV, train_test_split, KFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import scale, StandardScaler

import numpy as np
import pandas as pd
import statsmodels.api as sm
import warnings


def pythonmodel(request):
    # Load dataset to memory, get predictor and response variables
    dataset = Dataset.objects.get(pk=request['model'])
    df = pd.read_pickle(dataset.file)

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

    # Select columns based on user input and remove NaN's
    var_names = pred_vars + [resp_var]
    df_clean = df[var_names].dropna()

    # Return error if predictor and response variables are datetime or have too many categories
    for var in df_clean.drop(resp_var, axis=1):
        col = df_clean[var]
        if col.dtype in ['O', 'datetime64[ns]']:
            if col.dtype == 'datetime64[ns]':
                return JsonResponse(
                    {'error': 'predictorVars',
                     'message': 'Datetime variables not supported with modeling, <b>' + col.name + '</b>'},
                    status=400
                )
            if col.nunique() > col.shape[0] / 2:
                return JsonResponse(
                    {'error': 'predictorVars', 'message': '<b>' + col.name + '</b>' + ' has too many categories'},
                    status=400
                )
    if df_clean[resp_var].dtype == 'datetime64[ns]':
        return JsonResponse(
            {'error': 'responseVar',
             'message': 'Datetime variables not supported with modeling, <b>' + df_clean[resp_var].name + '</b>'},
            status=400
        )

    # Create design matrix and add constant to predictor variables
    df_x = pd.get_dummies(df_clean.drop(resp_var, axis=1), drop_first=True)
    df_x = sm.add_constant(df_x).rename(columns={'const': '(Intercept)'})
    df_y = df_clean[resp_var]

    # Create correlation matrix
    corr_df = df_clean.corr().round(2)
    corr_list = corr_df.values.tolist()

    corr_dict = OrderedDict()
    for cols, values in zip(corr_df, corr_list):
        corr_dict[cols] = values

    """
    Sklearn testing
    """
    sk_x = pd.get_dummies(df_clean.drop(resp_var, axis=1), drop_first=True)
    sk_y = df_y

    # Cross-validation pipeline for classification
    steps = [('scaler', StandardScaler()),
             ('knn', KNeighborsClassifier())]

    pipeline = Pipeline(steps)
    parameters = {'knn__n_neighbors': np.arange(1, 50)}

    # X_train, X_test, y_train, y_test = train_test_split(sk_x, sk_y, test_size=0.2, random_state=1, stratify=True)

    cv = GridSearchCV(pipeline, param_grid=parameters)
    # cv.fit(X_train, y_train)
    # y_pred = cv.predict(X_test)
    # print(cv.score(X_test, y_test))
    # print(classification_report(y_test, y_pred))
    # print(cv.best_params_)

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

        # Linear regression
        steps = [('scaler', StandardScaler()),
                 ('lm', LinearRegression())]

        pipeline = Pipeline(steps)
        parameters = {}

        kf = KFold(n_splits=5)

        pred = []
        resid = []
        mse_mean = []
        r_square_mean = []
        for train_index, test_index in kf.split(df_x):
            X_train, X_test = df_x.iloc[train_index], df_x.iloc[test_index]
            y_train, y_test = df_y.iloc[train_index], df_y.iloc[test_index]
            cv = GridSearchCV(pipeline, param_grid=parameters)
            cv.fit(X_test, y_test)
            y_pred = cv.predict(X_test)
            print(y_test.head(), y_pred[:10])
            mse = mean_squared_error(y_test, y_pred)

            print(mse)


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
            'corr_matrix': corr_dict
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
            'corr_matrix': corr_dict
        })
