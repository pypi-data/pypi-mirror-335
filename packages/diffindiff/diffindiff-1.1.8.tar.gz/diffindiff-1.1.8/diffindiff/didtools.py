# -------------------------------------------------------------------------------
# Name:        didtools (diffindiff)
# Purpose:     Creating data for Difference-in-Differences Analysis
# Author:      Thomas Wieland (geowieland@googlemail.com)
# Version:     1.1.6
# Last update: 2025-03-18 16:48
# Copyright (c) 2025 Thomas Wieland
#-------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols

def is_balanced(
    data,
    unit_col,
    time_col,
    outcome_col,
    other_cols = None
    ):

    unit_freq = data[unit_col].nunique()
    time_freq = data[time_col].nunique()
    unitxtime = unit_freq*time_freq

    if other_cols is None:
        cols_relevant = [unit_col, time_col, outcome_col]
    else:
        cols_relevant = [unit_col, time_col, outcome_col] + other_cols

    data_relevant = data[cols_relevant]

    if unitxtime != len(data_relevant.notna()):
        return False
    else:
        return True

def is_binary(
    data,
    treatment_col
    ):
    
    if data[treatment_col].nunique() == 2:
        if data[treatment_col].isin([0, 1]).all():
            return True
        else:
            return False
    else:
        return False

def is_missing(
    data,
    drop_missing: bool = True,
    missing_replace_by_zero: bool = False
    ):

    missing_outcome = data.isnull().any()
    missing_outcome_var = any(missing_outcome == True)

    if missing_outcome_var:
        missing_true_vars = [name for name, value in missing_outcome.items() if value]
    else:
        missing_true_vars = []

    if drop_missing and not missing_replace_by_zero:
        data = data.dropna(subset = missing_true_vars)
        
    if missing_replace_by_zero:
        data[missing_true_vars] = data[missing_true_vars].fillna(0)

    return [
        missing_outcome_var, 
        missing_true_vars, 
        data
        ]

def is_simultaneous(
    data,
    unit_col,
    time_col,
    treatment_col
    ):

    data_isnotreatment = is_notreatment(data, unit_col, treatment_col)
    treatment_group = data_isnotreatment[1]
    data_TG = data[data[unit_col].isin(treatment_group)]

    data_TG_pivot = data_TG.pivot_table (index = time_col, columns = unit_col, values = treatment_col)

    col_identical = (data_TG_pivot.nunique(axis=1) == 1).all()

    return col_identical

def is_notreatment(
    data,
    unit_col,
    treatment_col
    ):

    data_relevant = data[[unit_col, treatment_col]]

    treatment_timepoints = data_relevant.groupby(unit_col).sum(treatment_col)
    treatment_timepoints = treatment_timepoints.reset_index()

    no_treatment = (treatment_timepoints[treatment_col] == 0).any()

    treatment_group = treatment_timepoints.loc[treatment_timepoints[treatment_col] > 0, unit_col]
    control_group = treatment_timepoints.loc[treatment_timepoints[treatment_col] == 0, unit_col]

    return [
        no_treatment, 
        treatment_group, 
        control_group
        ]

def is_parallel(
    data,
    unit_col,
    time_col,
    treatment_col,
    outcome_col,
    pre_post = False,
    alpha = 0.05
    ):

    if pre_post:
        return None
    
    modeldata_isnotreatment = is_notreatment(
        data = data,
        unit_col = unit_col,
        treatment_col = treatment_col
        )    
    if not modeldata_isnotreatment:
        return None
    
    treatment_group = modeldata_isnotreatment[1]
    first_day_of_treatment = min(data[(data[unit_col].isin(treatment_group)) & (data[treatment_col] == 1)][time_col])

    data_test = data[data[time_col] < first_day_of_treatment].copy()
    data_test["TG"] = 0
    data_test.loc[data_test[unit_col].isin(treatment_group), "TG"] = 1
    
    if "date_counter" not in data_test.columns:
        data_test = date_counter(
            df = data_test,
            date_col = time_col, 
            new_col = "date_counter"
            )
    data_test["TG_x_t"] = data_test["TG"]*data_test["date_counter"]

    test_ols_model = ols(f'{outcome_col} ~ TG + date_counter + TG_x_t', data = data_test).fit()
    coef_TG_x_t_p = test_ols_model.pvalues["TG_x_t"]

    if coef_TG_x_t_p < alpha:
        parallel = False
    else:
        parallel = True

    return [
        parallel, 
        test_ols_model
        ]

def date_counter(
        df,
        date_col, 
        new_col = "date_counter"
        ):
    
    dates = df[date_col].unique()

    date_counter = pd.DataFrame({
       'date': dates,
        new_col: range(1, len(dates) + 1)
        })

    df = df.merge(
        date_counter,
        left_on = date_col,
        right_on = "date")
    
    return df

def unique(data):
    if data is None or (isinstance(data, (list, np.ndarray, pd.Series, pd.DataFrame)) and len(data) == 0):
        return []
    
    if isinstance(data, pd.DataFrame):
        values = data.values.ravel()

    elif isinstance(data, pd.Series):
        values = data.values.ravel()

    elif isinstance(data, np.ndarray):
        values = data.ravel()

    elif isinstance(data, list):
        values = data

    elif isinstance(data, set):
        values = list(data)

    else:
        raise TypeError(f"Unsupported data type: {type(data)}")
    
    unique_values = list(np.unique(values))
    return unique_values