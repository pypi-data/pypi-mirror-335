#-------------------------------------------------------------------------------
# Name:        diddata (diffindiff)
# Purpose:     Creating data for Difference-in-Differences Analysis
# Author:      Thomas Wieland (geowieland@googlemail.com)
# Version:     1.1.6
# Last update: 2025-03-18 16:48
# Copyright (c) 2025 Thomas Wieland
#-------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from diffindiff import didanalysis
from diffindiff import didtools

class did_groups:
    def __init__(
        self, 
        groups_data_df, 
        groups_config_dict
        ):

        self.data = [groups_data_df, groups_config_dict]

    def get_df (self):
        return self.data[0]

    def get_dict (self):
        return self.data[1]

    def summary(self):

        groups_config = self.data[1]

        print ("DiD Analysis Treatment and Control Group")
        print ("Units:                   " + str(groups_config["full_sample"]) + " (" + str(round(groups_config["full_sample"]/groups_config["full_sample"]*100,2)) + " %)")
        print ("Treatment Group:         " + str(groups_config["treatment_group"]) + " (" + str(round(groups_config["treatment_group"]/groups_config["full_sample"]*100,2)) + " %)")
        print ("Control Group:           " + str(groups_config["control_group"]) + " (" + str(round(groups_config["control_group"]/groups_config["full_sample"]*100,2)) + " %)")
        if groups_config["DDD"]:
            print ("Group segmentation:      YES")
        else:
            print ("Group segmentation:      NO")

    def add_segmentation(
        self,
        group_benefit: list        
        ):

        groups_data = self.data[0]
        groups_config = self.data[1]

        groups_data["group_benefit"] = 0
        groups_data.loc[groups_data["unit_UID"].astype(str).isin(group_benefit), "group_benefit"] = 1
        
        groups_config["DDD"] = True

        groups = did_groups(groups_data, groups_config)
        return groups

def create_groups(
    treatment_group,
    control_group
    ):

    treatment_group_unique = didtools.unique(treatment_group)
    control_group_unique = didtools.unique(control_group)

    treatment_group_N = len(treatment_group_unique)
    control_group_N = len(control_group_unique)

    TG_dummies = [1] * treatment_group_N
    CG_dummies = [0] * control_group_N

    TG_data = {
        "unit_UID": treatment_group_unique, 
        "TG": TG_dummies
        }
    CG_data = {
        "unit_UID": control_group_unique, 
        "TG": CG_dummies
        }

    groups_data = pd.concat ([pd.DataFrame(TG_data), pd.DataFrame(CG_data)], axis = 0)

    DDD = False

    groups_config = {
        "treatment_group": treatment_group_N, 
        "control_group": control_group_N, 
        "full_sample": treatment_group_N+control_group_N,
        "DDD": DDD
        }

    groups = did_groups(groups_data, groups_config)

    return groups

class did_treatment:
    def __init__(self, treatment_data_df, treatment_config_dict):
        self.data = [treatment_data_df, treatment_config_dict]

    def get_df (self):
        return self.data[0]

    def get_dict (self):
        return self.data[1]

    def summary(self):

        treatment_config = self.data[1]

        print ("DiD Analysis Treatment Configuration")

        if treatment_config["pre_post"] is True:
            print ("Study period (pre-post): " + str(treatment_config["treatment_period_start"]) + " vs. " + str(treatment_config["treatment_period_end"]))
        else:
            print ("Study period:            " + str(treatment_config["study_period_start"]) + " - " + str(treatment_config["study_period_end"]) + (" (") + str(treatment_config["study_period"]) + " " + treatment_config["frequency"] + ")")
            print ("Treatment Period:        " + str(treatment_config["treatment_period_start"]) + " - " + str(treatment_config["treatment_period_end"])+ (" (") + str(treatment_config["treatment_period"]) + " " + treatment_config["frequency"] + ")")

        if treatment_config["after_treatment_period"] is True:
            print ("After treatment period:  " + str(treatment_config["treatment_period_end"]) + " - " + str(treatment_config["study_period_end"]) + " (" + str(treatment_config["after_treatment_period_N"]) + " " + treatment_config["frequency"] + ")")

def create_treatment (
    study_period,
    treatment_period,
    freq = "D",
    date_format = "%Y-%m-%d",
    pre_post: bool = False,
    after_treatment_period: bool = False
    ):

    if pre_post:

        after_treatment_period = False

        study_period_range = [study_period[0], study_period[1]]
        study_period_N = 2
        study_period_counter = [1, 2]

        treatment_period_range = [treatment_period[0], treatment_period[1]]
        treatment_period_N = 1
        TT_dummies = [0,1]

        study_period_range = pd.DataFrame (treatment_period_range, columns=["t"])
        study_period_range["t_counter"] = pd.DataFrame(study_period_counter)

        TT_data = {
            "t": treatment_period_range, 
            "TT": TT_dummies
            }
        
        TT_data = pd.DataFrame(TT_data)
        
        treatment_period_range = pd.DataFrame(
            study_period_range
            )

        treatment_data = treatment_period_range.merge(TT_data, how = "left")

    else:

        study_period_range = pd.date_range(
            start = study_period[0], 
            end = study_period[1], 
            freq = freq
            )

        study_period_N = len(study_period_range)
        study_period_counter = np.arange (1, study_period_N+1, 1)

        treatment_period_range = pd.date_range(
            start = treatment_period[0], 
            end = treatment_period[1],
            freq = freq
            )

        treatment_period_N = len(treatment_period_range)

        TT_dummies = [1] * treatment_period_N

        study_period_range = {"t": study_period_range}
        study_period_range = pd.DataFrame (study_period_range)
        study_period_range["t_counter"] = pd.DataFrame(study_period_counter)

        TT_data = {
            "t": treatment_period_range, 
            "TT": TT_dummies
            }
        TT_data = pd.DataFrame(TT_data)
    
        treatment_data = study_period_range.merge(
            TT_data, 
            how = "left"
            )

    treatment_data["TT"] = treatment_data["TT"].fillna(0)

    if after_treatment_period:
        
        treatment_period_last = datetime.strptime(
            treatment_period[1], 
            date_format
            )
        after_treatment_period_day1 = treatment_period_last + timedelta(days=1)
        
        after_treatment_period_range = pd.date_range(
            start = after_treatment_period_day1, 
            end = study_period[1],
            freq = freq
            )
        after_treatment_period_N = len(after_treatment_period_range)

        ATT_dummies = [1] * after_treatment_period_N

        ATT_data = {"t": after_treatment_period_range, "ATT": ATT_dummies}
        ATT_data = pd.DataFrame(ATT_data)

        after_treatment_data = study_period_range.merge(ATT_data, how = "left")
        after_treatment_data['ATT'] = after_treatment_data['ATT'].fillna(0)
        after_treatment_data = after_treatment_data.drop(columns=["t", "t_counter"])

        treatment_data = pd.concat([treatment_data, after_treatment_data], axis=1)

    else:
        after_treatment_period_N = 0

    treatment_config = {
        "study_period_start": study_period[0],
        "study_period_end": study_period[1],
        "study_period": study_period_N,
        "treatment_period_start": treatment_period[0],
        "treatment_period_end": treatment_period[1],
        "treatment_period": treatment_period_N,
        "frequency": freq,
        "date_format": date_format,
        "pre_post": pre_post,
        "after_treatment_period": after_treatment_period,
        "after_treatment_period_N": after_treatment_period_N
        }

    treatment = did_treatment(treatment_data, treatment_config)

    return treatment

class did_data:

    def __init__(
        self,
        did_modeldata,
        did_groups,
        did_treatment,
        outcome_col_original,
        unit_time_col_original,
        covariates
        ):

        self.data = [
            did_modeldata, 
            did_groups, 
            did_treatment, 
            outcome_col_original,
            unit_time_col_original,
            covariates
            ]

    def get_did_modeldata_df (self):
        return pd.DataFrame(self.data[0])

    def get_did_groups_dict (self):
        return self.data[1]

    def get_did_treatment_dict (self):
        return self.data[2]

    def get_unit_time_cols (self):
        return self.data[4]

    def get_covariates (self):
        return self.data[5]

    def add_covariates(
        self, 
        additional_df,
        variables,
        unit_col = None,
        time_col = None
        ):
        
        if unit_col is None and time_col is None:
            raise ValueError("unit_col and/or time_col must be stated")
        
        did_modeldata = self.data[0]
        
        if unit_col is not None and time_col is not None:

            if "unit_time" not in additional_df.columns:
                additional_df["unit_time"] = additional_df[unit_col]+"_"+additional_df[time_col]
            if variables is None:
                did_modeldata = pd.merge(
                    did_modeldata, 
                    additional_df, 
                    on = "unit_time", 
                    how = "inner"
                    )
            else:
                additional_df_cols = ["unit_time"] + [col for col in additional_df.columns if col in variables]
                did_modeldata = pd.merge(
                    did_modeldata, 
                    additional_df[additional_df_cols], 
                    on = "unit_time", 
                    how = "inner"
                    )

        if unit_col is not None and time_col is None:
            
            if variables is None:
                did_modeldata = pd.merge(
                    did_modeldata, 
                    additional_df, 
                    left_on = "unit_UID",
                    right_on = unit_col,
                    how = "inner"
                    )
            else:
                additional_df_cols = [unit_col] + [col for col in additional_df.columns if col in variables]
                did_modeldata = pd.merge(
                    did_modeldata, 
                    additional_df[additional_df_cols], 
                    left_on = "unit_UID", 
                    right_on = unit_col,
                    how = "inner"
                    ) 

        if time_col is not None and unit_col is None:
            additional_df_cols = [unit_col] + [col for col in additional_df.columns if col in variables]
            did_modeldata = pd.merge(
                did_modeldata, 
                additional_df[additional_df_cols], 
                left_on = "unit_UID",
                right_on = "t",
                how = "inner"
                )  
        
        self.data[0] = did_modeldata
        self.data[5] = variables

        return self

    def add_segmentation(
        self,
        group_benefit: list
        ):

        did_groups = self.data[1]
        did_modeldata = self.data[0]

        did_groups = did_groups.add_segmentation(group_benefit = group_benefit)

        did_modeldata["group_benefit"] = 0
        did_modeldata.loc[did_modeldata["unit_UID"].astype(str).isin(group_benefit), "group_benefit"] = 1

        self.data[1] = did_groups
        self.data[0] = did_modeldata

        return self

    def summary(self):

        did_modeldata = self.data[0]
       
        groups_config = self.data[1].get_dict()
        treatment_config = self.data[2].get_dict()
        outcome_col_original = self.data[3]

        print ("Difference-in-Differences Analysis")
        print ("---------------------------------------------------------------")

        print ("Treatment and Control Group")
        print ("Units:                   " + str(groups_config["full_sample"]) + " (" + str(round(groups_config["full_sample"]/groups_config["full_sample"]*100,2)) + " %)")
        print ("Treatment Group:         " + str(groups_config["treatment_group"]) + " (" + str(round(groups_config["treatment_group"]/groups_config["full_sample"]*100,2)) + " %)")
        print ("Control Group:           " + str(groups_config["control_group"]) + " (" + str(round(groups_config["control_group"]/groups_config["full_sample"]*100,2)) + " %)")
        if groups_config["DDD"]:
            print ("Group segmentation:      YES")
        else:
            print ("Group segmentation:      NO")

        print ("---------------------------------------------------------------")
        print ("Time Periods")

        if treatment_config["pre_post"] is True:
            print ("Study period (pre-post): " + str(treatment_config["treatment_period_start"]) + " vs. " + str(treatment_config["treatment_period_end"]))
        else:
            print ("Study period:            " + str(treatment_config["study_period_start"]) + " - " + str(treatment_config["study_period_end"]) + (" (") + str(treatment_config["study_period"]) + " " + treatment_config["frequency"] + ")")
            print ("Treatment Period:        " + str(treatment_config["treatment_period_start"]) + " - " + str(treatment_config["treatment_period_end"])+ (" (") + str(treatment_config["treatment_period"]) + " " + treatment_config["frequency"] + ")")

        print ("---------------------------------------------------------------")
        print ("Outcome '" + outcome_col_original + "'")
        print ("Mean:                    " + str(round(np.mean(did_modeldata[outcome_col_original]), 2)))
        print ("Standard deviation:      " + str(round(np.std(did_modeldata[outcome_col_original]), 2)))

    def analysis(
        self, 
        log_outcome: bool = False, 
        FE_unit: bool = False, 
        FE_time: bool = False, 
        ITE: bool = False,
        GTE: bool = False,
        ITT: bool = False,
        GTT: bool = False,
        group_by = None,        
        confint_alpha = 0.05,
        drop_missing: bool = True,
        missing_replace_by_zero: bool = False
        ):

        did_pd = self.data[0]
        groups_config = self.data[1].get_dict()
        treatment_config = self.data[2].get_dict()
        outcome_col_original = self.data[3]
        covariates = self.data[5]
        
        freq = treatment_config["frequency"]
        date_format = treatment_config["date_format"]

        if groups_config["DDD"]:
            group_benefit = did_pd.loc[did_pd["group_benefit"] == 1, "unit_UID"].unique()
        else:
            group_benefit = []

        did_results = didanalysis.did_analysis(
            data = did_pd,
            TG_col = "TG",
            TT_col = "TT",
            treatment_col = "TGxTT",
            unit_col = "unit_UID",
            time_col = "t",
            outcome_col = outcome_col_original,
            after_treatment_period = treatment_config["after_treatment_period"],
            after_treatment_col = "TGxATT",
            pre_post = treatment_config["pre_post"],
            log_outcome = log_outcome,
            FE_unit = FE_unit,
            FE_time = FE_time,
            ITE = ITE,
            GTE = GTE,
            ITT = ITT,
            GTT = GTT,
            group_by = group_by,
            covariates = covariates,
            group_benefit = group_benefit,
            confint_alpha = confint_alpha,
            freq = freq,
            date_format = date_format,
            drop_missing = drop_missing,
            missing_replace_by_zero = missing_replace_by_zero
            )

        return did_results

def merge_data(
    outcome_data,
    unit_id_col,
    time_col,
    outcome_col,
    did_groups,
    did_treatment,
    drop_missing: bool = True,
    missing_replace_by_zero: bool = False
    ):

    groups_data_df = did_groups.get_df()
    groups_dict = did_groups.get_dict()
    treatment_data_df = did_treatment.get_df()
    treatment_dict = did_treatment.get_dict()
   
    did_modeldata = groups_data_df.merge(treatment_data_df, how = "cross")
    
    if drop_missing or missing_replace_by_zero:
        modeldata_ismissing = didtools.is_missing(
            data = did_modeldata, 
            drop_missing = drop_missing,
            missing_replace_by_zero = missing_replace_by_zero
            )
        did_modeldata = modeldata_ismissing[2]

    did_modeldata["TGxTT"] = did_modeldata["TG"] * did_modeldata["TT"]

    if treatment_dict["after_treatment_period"] is True:
        did_modeldata["TGxATT"] = did_modeldata["TG"] * did_modeldata["ATT"]

    did_modeldata["unit_time"] = did_modeldata["unit_UID"].astype(str) + "_" + did_modeldata["t"].astype(str)

    outcome_data["unit_time"] = outcome_data[unit_id_col].astype(str) + "_" + outcome_data[time_col].astype(str)
    outcome_data_short = outcome_data[["unit_time", outcome_col]]

    did_modeldata = did_modeldata.merge(outcome_data_short, on="unit_time", how="left")

    outcome_col_original = outcome_col
    unit_time_col_original = [unit_id_col, time_col]

    did_data_all = did_data(
        did_modeldata, 
        did_groups, 
        did_treatment, 
        outcome_col_original,
        unit_time_col_original,
        None
        )

    return did_data_all

def create_data(
    outcome_data,
    unit_id_col,
    time_col,
    outcome_col,
    treatment_group,
    control_group,
    study_period,
    treatment_period,
    freq = "D",
    date_format = "%Y-%m-%d",
    pre_post: bool = False,
    after_treatment_period: bool = False,
    drop_missing: bool = True,
    missing_replace_by_zero: bool = False
    ):

    groups = create_groups(
        treatment_group, 
        control_group
        )
    
    treatment = create_treatment(
        study_period = study_period, 
        treatment_period = treatment_period, 
        freq = freq,
        date_format = date_format,
        pre_post = pre_post, 
        after_treatment_period = after_treatment_period
        )    
    
    did_data_all = merge_data(
        outcome_data = outcome_data,
        unit_id_col = unit_id_col,
        time_col = time_col,
        outcome_col = outcome_col,
        did_groups = groups,
        did_treatment = treatment,
        drop_missing = drop_missing,
        missing_replace_by_zero = missing_replace_by_zero
        )

    return did_data_all