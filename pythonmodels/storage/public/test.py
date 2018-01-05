# Setup
from pymodel import settings
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import statsmodels.api as sm
import warnings

# Import diamonds to pandas
diamonds = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'public/diamonds.csv'))
dmds_clean = diamonds.dropna()


#####
# Summary info
#####

# All columns
print(diamonds.info())
print(diamonds.describe())
print(diamonds.dtypes)  # column types

# Individual columns
print(diamonds['clarity'].describe())
print(diamonds['clarity'].unique())


#####
# Selecting columns and/or rows
#####

# Selecting by rows or columns
print(diamonds[:100])  # first 100 rows
print(diamonds['price'].__class__)  # price column as time series
print(diamonds[['price']].__class__)  # price column as dataframe
print(diamonds[['carat', 'clarity']])  # multiple column selection

# Select columns and rows
print(diamonds.iloc[:20, 2:3])  # columns and rows by index
print(diamonds.loc[:, ['carat', 'clarity']])  # columns and rows by name
print(diamonds.ix[500:, ['cut', 'color']])  # columns and rows by index or name


#####
# Linear model example
#####
diamonds_dummy = pd.get_dummies(diamonds.dropna())

diamonds_x = diamonds_dummy.drop('price', axis=1)
diamonds_y = diamonds_dummy['price']

# statsmodels module
lm_fit = sm.OLS(diamonds_y, sm.add_constant(diamonds_x)).fit()
plt.scatter(lm_fit.fittedvalues, lm_fit.resid)
plt.ylim(0.0000000001, -0.0000000001)
plt.show()

# sklearn module
lm = LinearRegression().fit(diamonds_x, diamonds_y)
pred = lm.predict(diamonds_x)
diamonds_x['pred'] = pred
diamonds_x['resid'] = diamonds_y.values - pred

diamonds_x.plot()
plt.show()


#####
# Multinomial logistic regression example with dummy encoding
#####
iris = pd.DataFrame(sm.datasets.get_rdataset('iris').data)

with warnings.catch_warnings():
    warnings.simplefilter("error")

    errs = []
    for i in ['newton', 'nm', 'bfgs', 'lbfgs', 'powell', 'cg', 'ncg']:
        try:
            logit_fit = sm.MNLogit(dmds_clean['cut'], sm.add_constant(pd.get_dummies(dmds_clean.loc[:, ['depth', 'clarity']]))).fit(method=i)
        except Warning as w:
            continue
        else:
            break




logit_fit = sm.MNLogit(diamonds['cut'], pd.get_dummies(diamonds['color'])).fit()