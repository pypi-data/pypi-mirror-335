#-------------------------------------------------------------------------------
# Name:        test_diddata (diffindiff)
# Purpose:     Tests for functions in the diddata module
# Author:      Thomas Wieland (geowieland@googlemail.com)
# Version:     1.1.7
# Last update: 2025-03-18 18:32
# Copyright (c) 2025 Thomas Wieland
#-------------------------------------------------------------------------------


# 4.1
# Example 1: Effect of a curfew in German counties in the first
# wave of the COVID-19 pandemic (DiD pre-post analysis)

# 4.1.1

import pandas as pd
from diffindiff.diddata import did_groups, create_groups, did_treatment, create_treatment, did_data, merge_data, create_data


curfew_DE=pd.read_csv("data/curfew_DE.csv", sep=";", decimal=",")
# Dataset with daily and cumulative SARS-CoV-2 infections of German counties
# Data source: Wieland (2020) https://doi.org/10.18335/region.v7i2.324


# 4.1.2

curfew_groups=create_groups(
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"]
    )
# Creating treatment and control group
# "Bundesland" (=federal state): 9 = Bavaria, 10 = Saarland, 14 = Saxony

curfew_groups.summary()
# Groups summary

# 4.1.3

curfew_treatment_prepost=create_treatment(
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq = "D",
    pre_post = True
    )
# Creating treatment
# Curfew from March 21, 2020, to May, 5, 2020

curfew_treatment_prepost.summary()
# Treatment summary

# 4.1.4

curfew_data_prepost_merge=merge_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    did_groups=curfew_groups,
    did_treatment=curfew_treatment_prepost
    )

curfew_data_prepost_merge.summary()
# Summary of created data

# 4.1.5

curfew_data_prepost=create_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq="D",
    pre_post=True
    )
# Creating DiD treatement dataset by defining groups and
# treatment time at once

curfew_data_prepost.summary()
# Summary of created data

# 4.1.6

curfew_model_prepost = curfew_data_prepost.analysis()
# Model analysis of created data

curfew_model_prepost.summary()
# Model summary

print(curfew_model_prepost.effects())
# Show effects

# 4.1.7

curfew_model_prepost.plot(
    x_label="Timepoint",
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness pre-post - Groups over time",
    plot_observed=False,
    lines_col=[None,None,"blue","orange"],
    lines_labels=[None,None,"Treatment group","Control group"],
    lines_style=[None,None,"solid","solid"]
    )
# Plot DiD pre vs. post results
# with user-determined style

curfew_model_prepost.plot(
    x_label="Timepoint",
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness pre-post - Groups over time",
    lines_col=[None,None,"blue","orange"],
    lines_labels=[None,None,"Treatment group","Control group"],
    pre_post_barplot=True
    )
# Plot DiD pre vs. post results
# with user-determined style

curfew_model_prepost.plot_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness pre-post - DiD effects"
    )
# plot effects

curfew_model_prepost.plot_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness pre-post - DiD effects",
    scale_plot=False
    )
# plot effects

# 4.1.8

counties_DE=pd.read_csv("data/counties_DE.csv", sep=";", decimal=",", encoding='latin1')
# Dataset with German county data

curfew_data_prepost_withcov = curfew_data_prepost.add_covariates(
    additional_df=counties_DE, 
    unit_col="county",
    time_col=None, 
    variables=["comm_index", "TourPer1000"])

curfew_data_prepost_withcov.summary()
# Summary of created data

curfew_model_prepost_withcov = curfew_data_prepost_withcov.analysis()
# Model analysis of created data

curfew_model_prepost_withcov.summary()
# Model summary


# 4.2
# DiD with a simultaneous intervention and multi-period panel
# data: German counties during the first Corona wave

# 4.2.1

curfew_data=create_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq="D"
    )
# Creating DiD dataset by defining groups and
# treatment time at once

curfew_data.summary()
# # Summary of created treatment data

# 4.2.2

curfew_model = curfew_data.analysis()
# Model analysis of created data

curfew_placebo = curfew_model.placebo()
# Placebo test with default parameters

curfew_placebo.summary()
# Summary of placebo DiD analysis

print(curfew_model.effects())
# Print effects

curfew_model.summary()
# Model summary

curfew_model.plot(
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness - Groups over time",
    plot_observed=True
    )
# Plot observed vs. predicted (means) separated by group (treatment and control)

curfew_model.plot_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness - DiD effects"
    )
# plot effects


# 4.2.3

# Two-way-fixed-effects model:

curfew_model_FE=curfew_data.analysis(
    FE_unit=True, 
    FE_time=True
    )
# Model analysis of created data with fixed effects for 
# units (FE_unit=True) and time (FE_time=True)

curfew_model_FE_summary = curfew_model_FE.summary()
# Model summary

print(curfew_model_FE.treatment_statistics())
# Print treatment statistics

print(curfew_model_FE_summary[4]["isnotreatment"])
# Result of "No-treatment control group" test

curfew_model_FE.plot(
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness (Two-way FE model) - Groups over time",
    plot_observed=True
    )
# Plot of treatment and control group

fixed_effects = curfew_model_FE.fixef()
# Fixed effects of CHBW_data_model_FE
print(fixed_effects[0].head())
# Unit fixed effects
print(fixed_effects[1].head())
# Time fixed effects

# 4.2.4

# Model with after treatment period:

curfew_data_AT = create_data(
    outcome_data = curfew_DE,
    unit_id_col="county",
    time_col = "infection_date",
    outcome_col = "infections_cum_per100000",
    treatment_group = 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group = 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    study_period = ["2020-03-01", "2020-05-15"],
    treatment_period = ["2020-03-21", "2020-05-05"],
    freq = "D",
    after_treatment_period = True
    )
# Creating DiD treatment dataset and including
# after-treatment period (after_treatment_period=True)

curfew_data_AT.summary()
# Summary of created data

curfew_model_AT = curfew_data_AT.analysis(
    FE_unit = True,
    FE_time = True,
    )
# Model analysis of created data with fixed effects for 
# units (FE_unit=True) and time (FE_time=True)

curfew_model_AT.summary()
# Model summary

curfew_model_AT.plot(    
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness (Two-way FE model with after-treatment period) - Groups over time",
    plot_observed=True
)
# Plot observed vs. predicted (means) separated by group (treatment and control)


# 4.2.5

# Model with group-specific treatment effects:

curfew_data_withgroups = curfew_data.add_covariates(
    additional_df=counties_DE, 
    unit_col="county",
    time_col=None, 
    variables=["BL"])
# Adding federal state column as covariate

curfew_model_withgroups = curfew_data_withgroups.analysis(
    GTE=True,
    group_by="BL")
# Model analysis of created data

curfew_model_withgroups.summary()
# Model summary

curfew_model_withgroups.plot_group_treatment_effects(
    treatment_group_only=True
    )
# Plot of group-specific treatment effects