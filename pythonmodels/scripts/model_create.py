from collections import OrderedDict
from django.http import JsonResponse

from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
)
from sklearn.linear_model import LinearRegression, LogisticRegression, ElasticNet
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score, confusion_matrix
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

from .helper_funs import form_errors
from pythonmodels.models import Dataset

import numpy as np
import pandas as pd


def pythonmodel(request):
    # Load dataset, get predictor and response variables
    dataset = Dataset.objects.get(pk=request['model'])
    df = pd.read_pickle(dataset.file)

    pred_vars = request.getlist('predictorVars[]')
    resp_var = request['responseVar']

    # Return error if no predictor variables selected or response variable is in the predictor variables
    if not pred_vars:
        return form_errors('predictorVars', 'Select at least one predictor variable', 400)
    elif resp_var in pred_vars:
        return form_errors('predictorVars', 'Predictor variables cannot contain the response variable', 400)

    # Select columns based on user input and remove NaN's
    var_names = [resp_var] + pred_vars
    df_clean = df[var_names].dropna()

    # Return error if predictor and response variables have one value or are datetime
    for var in df_clean:
        col = df_clean[var]
        if col.nunique() == 1:
            if col.name == resp_var:
                return form_errors('responseVar', 'Variable must have more than one value, <b>' + col.name + '</b>',
                                   400)
            else:
                return form_errors('predictorVars', 'Variable must have more than one value, <b>' + col.name + '</b>',
                                   400)
        if col.dtype == 'datetime64[ns]':
            if col.name == resp_var:
                return form_errors('responseVar',
                                   'Datetime variables not supported with modeling, <b>' + col.name + '</b>',
                                   400)
            else:
                return form_errors('predictorVars',
                                   'Datetime variables not supported with modeling, <b>' + col.name + '</b>', 400)

    # Create design matrix and separate y variable
    df_x = pd.get_dummies(df_clean.drop(resp_var, axis=1), drop_first=True)
    df_y = df_clean[resp_var]

    # Create correlation matrix
    corr_df = df_clean.corr().round(2)
    corr_list = corr_df.values.tolist()

    corr_dict = OrderedDict()
    for col, value in zip(corr_df, corr_list):
        corr_dict[col] = value

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

        # Initialize predictions and true values (needed for shuffled cv)
        pred = []
        true = []

        # Run cross validation, catch cv errors
        try:
            for train_index, test_index in kf_splits:
                X_train, X_test = df_x.iloc[train_index], df_x.iloc[test_index]
                y_train, y_test = df_y.iloc[train_index], df_y.iloc[test_index]
                cv = GridSearchCV(pipeline, param_grid=parameters)
                cv.fit(X_test, y_test)
                y_pred = cv.predict(X_test)

                pred.extend(y_pred)
                true.extend(y_test)
        except ValueError as ve:
            return form_errors('responseVar',
                               'Not enough categories in each train / test split, <b>' + resp_var + '</b>',
                               400)

        # Create output table
        stats = OrderedDict()
        stats['Observations'] = df_x.shape[0]
        stats['Predictors (w/ dummies)'] = df_x.shape[1]

        if model_name in ['ols', 'rfr', 'en', 'gbr', 'svr']:
            stats['$r^2$'] = np.round(r2_score(true, pred), 3)
            stats['adj $r^2$'] = np.round(adj_r_square(stats['$r^2$'], pred, df_x.columns), 3)
            stats['rmse'] = np.round(np.sqrt(mean_squared_error(true, pred)), 3)

            # Create dictionary for predicted vs. actual plot
            pred_vs_true = pd.DataFrame({
                'pred': np.round(pred, 2),
                'true': np.round(true, 2)
            }).to_dict(orient='records')
            json_dict.update({
                'pred_vs_true': pred_vs_true,
                'min': round(min(min(pred), min(true))),
                'max': round(max(max(pred), max(true)))})

        elif model_name in ['log', 'rfc', 'knn', 'gbc', 'svc']:
            stats['Accuracy'] = '{:.2%}'.format(np.round(accuracy_score(true, pred), 4))

            # Create confusion matrix
            cf_matrix = pd.DataFrame(confusion_matrix(true, pred)).transpose()
            cf_list = cf_matrix.values.tolist()
            cf_dict = OrderedDict()
            for col, value in zip(list(set(true)), cf_list):
                cf_dict[col] = value

            json_dict.update({'cf_matrix': cf_dict})

        # Add final variables to json_dict
        json_dict.update({'stats': stats, 'corr_matrix': corr_dict, 'kfolds': kf.n_splits})

        # Return json from ajax request
        return JsonResponse(json_dict)

    """
    Return user selected model output
    """

    # Regression
    if request['modelType'] in ['ols', 'rfr', 'en', 'gbr', 'svr']:

        # Check for errors
        if df_y.dtype not in ['float64', 'int64']:
            return form_errors('responseVar', 'Response variable must be numeric for this model type', 400)

        # Create tuple of classification models
        regression_tuple = (
            ('ols', LinearRegression()),
            ('rfr', RandomForestRegressor()),
            ('en', ElasticNet()),
            ('gbr', GradientBoostingRegressor()),
            ('svr', SVR())
        )

        # Return requested model output
        for id, model in regression_tuple:
            if request['modelType'] == id:
                return model_output(id, model)

    # Classification
    elif request['modelType'] in ['log', 'rfc', 'knn', 'gbc', 'svc']:

        # Create tuple of classification models
        classification_tuple = (
            ('knn', KNeighborsClassifier()),
            ('log', LogisticRegression()),
            ('rfc', RandomForestClassifier()),
            ('gbc', GradientBoostingClassifier()),
            ('svc', SVC())
        )

        # Return requested model output
        for id, model in classification_tuple:
            if request['modelType'] == id:
                return model_output(id, model, stratified_kf=True)


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
