from collections import OrderedDict
from django.http import JsonResponse
from pythonmodels.models import Dataset

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score, confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd


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
    df_y = df_clean[resp_var]

    # Create correlation matrix
    corr_df = df_clean.corr().round(2)
    corr_list = corr_df.values.tolist()

    corr_dict = OrderedDict()
    for cols, values in zip(corr_df, corr_list):
        corr_dict[cols] = values

    """
    Function to run model pipeline and output to json
    """
    def model_output(model_name, model_object, scale=True, stratified_kf=False):

        # Create dictionary to return as JsonResponse
        json_dict = {'model': model_name}

        # Setup pipeline with optional hyperparemeters, data scaled as default
        steps = [('scaler', StandardScaler()),
                 (model_name, model_object)]
        pipeline = Pipeline(steps)
        parameters = {}
        if not stratified_kf:
            kf = KFold(n_splits=10, shuffle=True)
            kf_splits = kf.split(df_x)
        else:
            kf = StratifiedKFold(n_splits=10, shuffle=True)
            kf_splits = kf.split(df_x, df_y)

        # Initialize predictions and true values (need for shuffled cv)
        pred = []
        true = []

        # Run cross validation with optional hyperparameter tuning
        try:
            for train_index, test_index in kf_splits:
                X_train, X_test = df_x.iloc[train_index], df_x.iloc[test_index]
                y_train, y_test = df_y.iloc[train_index], df_y.iloc[test_index]
                cv = GridSearchCV(pipeline, param_grid=parameters)
                cv.fit(X_test, y_test)
                y_pred = cv.predict(X_test)

                pred.extend(y_pred)
                true.extend(y_test)
        except ValueError:
            return JsonResponse(
                {'error': 'responseVar', 'message': 'Not enough response members in each train / test split'},
                status=400
            )

        # Create output table
        stats = OrderedDict()
        stats['Observations'] = df_x.shape[0]
        stats['Predictors (w/ dummies)'] = df_x.shape[1]

        if model_name in ['ols', 'rf_regressor']:
            stats['$r^2$'] = np.round(r2_score(true, pred), 3)
            stats['adj $r^2$'] = np.round(adj_r_square(stats['$r^2$'], pred, df_x.columns), 3)
            stats['rmse'] = np.round(np.sqrt(mean_squared_error(true, pred)), 3)

            # Create dictionary for fitted vs. residual plot
            fit_vs_resid = pd.DataFrame({
                'pred': pred,
                'resid': np.array(true) - np.array(pred)
            }).to_dict(orient='records')
            json_dict.update({'resid_vs_fit': fit_vs_resid})

        elif model_name in ['log', 'rf_classifier']:
            stats['Accuracy'] = '{:.2%}'.format(np.round(accuracy_score(true, pred), 4))

        # Add final variables to json_dict
        json_dict.update({'stats': stats, 'corr_matrix': corr_dict, 'kfolds': kf.n_splits})

        # Return json from ajax request
        return JsonResponse(json_dict)

    """
    Return model that user selected
    """

    # Regression
    if request['modelType'] in ['ols', 'rf_regressor']:

        # Check for errors
        if df_y.dtype not in ['float64', 'int64']:
            return JsonResponse(
                {'error': 'responseVar', 'message': 'Response variable must be numeric for this model type'},
                status=400
            )

        # Simple linear regression
        if request['modelType'] == 'ols':
            return model_output('ols', LinearRegression())

        # Random forest regression
        if request['modelType'] == 'rf_regressor':
            return model_output('rf_regressor', RandomForestRegressor())

    # Classification
    elif request['modelType'] in ['log', 'rf_classifier']:

        # Check for errors
        # if df_y.dtype not in ['object']:
        #     return JsonResponse(
        #         {'error': 'responseVar', 'message': 'Response variable must be categorical'},
        #         status=400
        #     )

        # Logistic Regression
        if request['modelType'] == 'log':
            return model_output('log', LogisticRegression(), stratified_kf=True)

        # Random Forest
        if request['modelType'] == 'rf_classifier':
            return model_output('rf_classifier', RandomForestClassifier(), stratified_kf=True)


"""
Helper functions
"""


def adj_r_square(r2, n, k):
    return 1 - ((1 - r2) * (len(n) - 1) / (len(n) - len(k) - 1))


"""
Sklearn testing
"""
# sk_x = pd.get_dummies(df_clean.drop(resp_var, axis=1), drop_first=True)
# sk_y = df_y

# Cross-validation pipeline for classification
# steps = [('scaler', StandardScaler()),
#          ('knn', KNeighborsClassifier())]
#
# pipeline = Pipeline(steps)
# parameters = {'knn__n_neighbors': np.arange(1, 50)}

# X_train, X_test, y_train, y_test = train_test_split(sk_x, sk_y, test_size=0.2, random_state=1, stratify=True)

# cv = GridSearchCV(pipeline, param_grid=parameters)
# cv.fit(X_train, y_train)
# y_pred = cv.predict(X_test)
# print(cv.score(X_test, y_test))
# print(classification_report(y_test, y_pred))
# print(cv.best_params_)
