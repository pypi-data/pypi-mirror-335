#-------------------------------------------------------------------------------
# Name:        didanalysis (diffindiff)
# Purpose:     Analysis functions for difference-in-differences analyses
# Author:      Thomas Wieland (geowieland@googlemail.com)
# Version:     1.1.8
# Last update: 2025-03-19 07:45
# Copyright (c) 2025 Thomas Wieland
#-------------------------------------------------------------------------------


import pandas as pd
from statsmodels.formula.api import ols
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from diffindiff import didtools


class did_model:

    def __init__(
        self,
        did_modelresults,
        did_modelconfig,
        did_modeldata,
        did_modelpredictions,
        did_fixed_effects,
        did_individual_effects,
        did_group_effects,
        did_model_statistics,
        did_olsmodel
        ):

        self.data = [
            did_modelresults, 
            did_modelconfig, 
            did_modeldata, 
            did_modelpredictions, 
            did_fixed_effects,
            did_individual_effects,
            did_group_effects, 
            did_model_statistics, 
            did_olsmodel
            ]

    def treatment_statistics(self):

        model_config = self.data[1]
        model_data = self.data[2]
        
        treatment_col = model_config["treatment_col"]
        unit_col = model_config["unit_col"]
        time_col = model_config["time_col"]        
        after_treatment_period = model_config["after_treatment_period"]        
        if after_treatment_period:
            after_treatment_col = model_config["after_treatment_col"]

        treatment_timepoints = model_data.groupby(unit_col)[treatment_col].sum()
        treatment_timepoints = pd.DataFrame(treatment_timepoints)
        treatment_timepoints = treatment_timepoints.reset_index()

        study_period_start = pd.to_datetime(min(model_data[time_col]))
        study_period_start = study_period_start.date()
        study_period_end = pd.to_datetime(max(model_data[time_col]))
        study_period_end = study_period_end.date()
        study_period_N = model_data[time_col].nunique()        
        treatment_period_start = pd.to_datetime(min(model_data[model_data[treatment_col] == 1][time_col]))
        treatment_period_end = pd.to_datetime(max(model_data[model_data[treatment_col] == 1][time_col]))
        treatment_period_N = model_data.loc[model_data[treatment_col] == 1, time_col].nunique()        
        after_treatment_period_start = None
        after_treatment_period_end = None
        after_treatment_period_N = None
        if after_treatment_period:
            after_treatment_period_start = treatment_period_end+pd.Timedelta(days=1)
            after_treatment_period_start = pd.to_datetime(after_treatment_period_start)
            after_treatment_period_end = pd.to_datetime(study_period_end)
            after_treatment_period_N = model_data.loc[model_data[after_treatment_col] == 1, time_col].nunique()            
            after_treatment_period_start = after_treatment_period_start.strftime(model_config["date_format"])
            after_treatment_period_end = after_treatment_period_end.strftime(model_config["date_format"])
        study_period_start = study_period_start.strftime(model_config["date_format"])
        study_period_end = study_period_end.strftime(model_config["date_format"])
        treatment_period_start = treatment_period_start.strftime(model_config["date_format"])
        treatment_period_end = treatment_period_end.strftime(model_config["date_format"])
        period_study = [study_period_start, study_period_end, study_period_N]
        period_treatment = [treatment_period_start, treatment_period_end, treatment_period_N]
        period_after_treatment = [after_treatment_period_start, after_treatment_period_end, after_treatment_period_N]
        time_periods = [period_study, period_treatment, period_after_treatment]

        treatment_group = np.array(treatment_timepoints[treatment_timepoints[treatment_col] > 0][unit_col])
        control_group = np.array(treatment_timepoints[treatment_timepoints[treatment_col] == 0][unit_col])
        groups = [treatment_group, control_group]

        treatment_group_size = len(treatment_group)
        control_group_size = len(control_group)
        all_units = treatment_group_size+control_group_size
        treatment_group_share = treatment_group_size/all_units
        control_group_share = control_group_size/all_units
        group_sizes = [treatment_group_size, control_group_size, all_units, treatment_group_share, control_group_share]

        average_treatment_time = treatment_timepoints[treatment_timepoints[unit_col].isin(treatment_group)][treatment_col].mean()

        return [
            group_sizes,
            average_treatment_time, 
            groups, 
            treatment_timepoints, 
            time_periods
            ]

    def summary(
        self,
        full = True
        ):
        
        model_results = self.data[0]
        model_config = self.data[1]
        model_data = self.data[2]
        outcome_col_original = model_config["outcome_col"]

        model_statistics = self.data[7]

        modeldata_isbalanced = didtools.is_balanced (
            data = model_data,
            unit_col = model_config["unit_col"],
            time_col = model_config["time_col"],
            outcome_col = model_config["outcome_col"]
            )
        
        modeldata_isbinary = didtools.is_binary(
            data = model_data,
            treatment_col = model_config["treatment_col"]
            )

        modeldata_isnotreatment = didtools.is_notreatment(
            data = model_data,
            unit_col = model_config["unit_col"],
            treatment_col = model_config["treatment_col"]
            )

        modeldata_issimultaneous = didtools.is_simultaneous(
            data = model_data,
            unit_col = model_config["unit_col"],
            time_col = model_config["time_col"],
            treatment_col = model_config["treatment_col"]
            )
        
        modeldata_isparallel = didtools.is_parallel(
            data = model_data,
            unit_col = model_config["unit_col"],
            time_col = model_config["time_col"],
            treatment_col = model_config["treatment_col"],
            outcome_col = model_config["outcome_col"],
            pre_post = model_config["pre_post"]
            )

        treatment_statistics = self.treatment_statistics()

        print (model_config["analysis_description"])
        print ("===============================================================")

        if not model_config["ITE"] and not model_config["GTE"]: 
            print ("Average treatment effect    " + str(round(model_results["ATE"]["ATE"], 3)) + "  SE=" + str(round(model_results["ATE"]["ATE_SE"], 3)) + "  t=" + str(round(model_results["ATE"]["ATE_t"], 3)) + "  p=" + str(round(model_results["ATE"]["ATE_p"], 3)))

        if model_config["DDD"]:
            print ("ATE for the treated (B)     " + str(round(model_results["ATET"]["ATET"], 3)) + "  SE=" + str(round(model_results["ATET"]["ATET_SE"], 3)) + "  t=" + str(round(model_results["ATET"]["ATET_t"], 3)) + "  p=" + str(round(model_results["ATET"]["ATET_p"], 3)))

        if model_config["ITE"]:
            individual_treatment_effects = self.data[5][1]
            print ("Individual treatment effects:")
            coef_min = min(individual_treatment_effects["coef"])
            coef_min_SE = individual_treatment_effects[individual_treatment_effects["coef"] == coef_min]["SE"].iloc[0]
            coef_min_t = individual_treatment_effects[individual_treatment_effects["coef"] == coef_min]["t"].iloc[0]
            coef_min_p = individual_treatment_effects[individual_treatment_effects["coef"] == coef_min]["p"].iloc[0]
            coef_min_unit = individual_treatment_effects[individual_treatment_effects["coef"] == coef_min][model_config["unit_col"]].iloc[0]
            coef_max = max(individual_treatment_effects["coef"])
            coef_max_SE = individual_treatment_effects[individual_treatment_effects["coef"] == coef_max]["SE"].iloc[0]
            coef_max_t = individual_treatment_effects[individual_treatment_effects["coef"] == coef_max]["t"].iloc[0]
            coef_max_p = individual_treatment_effects[individual_treatment_effects["coef"] == coef_max]["p"].iloc[0]
            coef_max_unit = individual_treatment_effects[individual_treatment_effects["coef"] == coef_max][model_config["unit_col"]].iloc[0]
            print ("Min. treatment effect(1)    " + str(round(coef_min, 3)) + " SE=" + str(round(coef_min_SE, 3)) + " t=" + str(round(coef_min_t, 3)) + " p="+ str(round(coef_min_p, 3)))
            print ("Max. treatment effect(2)    " + str(round(coef_max, 3)) + " SE=" + str(round(coef_max_SE, 3)) + " t=" + str(round(coef_max_t, 3)) + " p="+ str(round(coef_max_p, 3)))
            print ("(1) = unit '" + str(coef_min_unit) + "', (2) = unit '" + str(coef_max_unit) + "'")

        if model_config["GTE"]:
            group_treatment_effects = self.data[6][1]
            print ("Group-specific treatment effects:")
            coef_min = min(group_treatment_effects["coef"])
            coef_min_SE = group_treatment_effects[group_treatment_effects["coef"] == coef_min]["SE"].iloc[0]
            coef_min_t = group_treatment_effects[group_treatment_effects["coef"] == coef_min]["t"].iloc[0]
            coef_min_p = group_treatment_effects[group_treatment_effects["coef"] == coef_min]["p"].iloc[0]
            coef_min_unit = group_treatment_effects[group_treatment_effects["coef"] == coef_min][model_config["group_by"]].iloc[0]
            coef_max = max(group_treatment_effects["coef"])
            coef_max_SE = group_treatment_effects[group_treatment_effects["coef"] == coef_max]["SE"].iloc[0]
            coef_max_t = group_treatment_effects[group_treatment_effects["coef"] == coef_max]["t"].iloc[0]
            coef_max_p = group_treatment_effects[group_treatment_effects["coef"] == coef_max]["p"].iloc[0]
            coef_max_unit = group_treatment_effects[group_treatment_effects["coef"] == coef_max][model_config["group_by"]].iloc[0]
            print ("Min. treatment effect(1)    " + str(round(coef_min, 3)) + " SE=" + str(round(coef_min_SE, 3)) + " t=" + str(round(coef_min_t, 3)) + " p="+ str(round(coef_min_p, 3)))
            print ("Max. treatment effect(2)    " + str(round(coef_max, 3)) + " SE=" + str(round(coef_max_SE, 3)) + " t=" + str(round(coef_max_t, 3)) + " p="+ str(round(coef_max_p, 3)))
            print ("(1) = group '" + str(coef_min_unit) + "', (2) = group '" + str(coef_max_unit) + "'")

        if model_config["after_treatment_period"]:
            print ("Av. After Treatment Effect  " + str(round(model_results["AATE"]["AATE"], 3)) + "  SE=" + str(round(model_results["AATE"]["AATE_SE"], 3)) + "  t=" + str(round(model_results["AATE"]["AATE_t"], 3)) + "  p=" + str(round(model_results["AATE"]["AATE_p"], 3)))
        
        if not model_config["FE_unit"] and not model_config["FE_time"] and not model_config["GTE"] and not model_config["GTT"]:
            if model_config["DDD"]:
                print ("Control group A baseline    " + str(round(model_results["Intercept"]["Intercept"], 3)) + "  SE=" + str(round(model_results["Intercept"]["Intercept_SE"], 3)) + "  t=" + str(round(model_results["Intercept"]["Intercept_t"], 3)) + " p=" + str(round(model_results["Intercept"]["Intercept_p"], 3)))
            else:
                print ("Control group baseline      " + str(round(model_results["Intercept"]["Intercept"], 3)) + "  SE=" + str(round(model_results["Intercept"]["Intercept_SE"], 3)) + "  t=" + str(round(model_results["Intercept"]["Intercept_t"], 3)) + " p=" + str(round(model_results["Intercept"]["Intercept_p"], 3)))
        
        if not model_config["FE_unit"] and model_config["TG_col"] is not None and not model_config["GTE"] and not model_config["GTT"]:
            print ("Treatment group deviation   " + str(round(model_results["TG"]["TG"], 3)) + "  SE=" + str(round(model_results["TG"]["TG_SE"], 3)) + "  t=" + str(round(model_results["TG"]["TG_t"], 3)) + " p=" + str(round(model_results["TG"]["TG_p"], 3)))

        if not model_config["FE_time"] and model_config["TT_col"] is not None and not model_config["DDD"]:
            print ("Non-treatment time effect   " + str(round(model_results["TT"]["TT"], 3)) + "  SE=" + str(round(model_results["TT"]["TT_SE"], 3)) + "  t=" + str(round(model_results["TT"]["TT_t"], 3)) + " p=" + str(round(model_results["TT"]["TT_p"], 3)))
        
        if model_config["DDD"]:
            print ("Group B deviation           " + str(round(model_results["BG"]["BG"], 3)) + "  SE=" + str(round(model_results["BG"]["BG_SE"], 3)) + "  t=" + str(round(model_results["BG"]["BG_t"], 3)) + " p=" + str(round(model_results["BG"]["BG_p"], 3)))
            print ("Treatment Group B deviation " + str(round(model_results["TBG"]["TBG"], 3)) + "  SE=" + str(round(model_results["TBG"]["TBG_SE"], 3)) + "  t=" + str(round(model_results["TBG"]["TBG_t"], 3)) + " p=" + str(round(model_results["TBG"]["TBG_p"], 3)))
            print ("Non-treatment time effect A " + str(round(model_results["TT"]["TT"], 3)) + "  SE=" + str(round(model_results["TT"]["TT_SE"], 3)) + "  t=" + str(round(model_results["TT"]["TT_t"], 3)) + " p=" + str(round(model_results["TT"]["TT_p"], 3)))
            print ("Group B effect              " + str(round(model_results["TTB"]["TTB"], 3)) + "  SE=" + str(round(model_results["TTB"]["TTB_SE"], 3)) + "  t=" + str(round(model_results["TTB"]["TTB_t"], 3)) + " p=" + str(round(model_results["TTB"]["TTB_p"], 3)))
            print ("A = treatment non-benefit group, B = treatment benefit group")

        print ("---------------------------------------------------------------")
        print ("Fixed effects")
        if not model_config["FE_unit"]:
            print ("Observation units           NO")
        else:
            print ("Observation units           YES")

        if not model_config["FE_time"]:
            print ("Time periods                NO")
        else:
            print ("Time periods                YES")

        print ("---------------------------------------------------------------")
        print ("Control variables")
        if model_config["covariates"]:
            print ("Covariates                  YES")
        else:
            print ("Covariates                  NO")
        if model_config["ITT"]:
            print ("Individual time trends      YES")
        else:
            print ("Individual time trends      NO")
        if model_config["GTT"]:
            print ("Group-specific time trends  YES")
        else:
            print ("Group-specific time trends  NO")

        if full:
            print ("---------------------------------------------------------------")
            print ("Experimental conditions")
            if modeldata_issimultaneous:
                print ("Type of adoption            Simultaneous")
            else:
                print ("Type of adoption            Staggered")
            if modeldata_isnotreatment[0]:
                print ("No-treatment control group  YES")
            else:
                print ("No-treatment control group  NO")
            if modeldata_isparallel is not None:
                if modeldata_isparallel[0]:
                    print ("Parallel time trends (pre)  YES")
                else:
                    print ("Parallel time trends (pre)  NO")
            print ("Group sizes                 Treatment " + str(treatment_statistics[0][0]) + " (" + str(round(treatment_statistics[0][3]*100, 1)) + " %)")
            print ("                            Control " + str(treatment_statistics[0][1]) + " (" + str(round(treatment_statistics[0][4]*100, 1)) + " %)")
            if modeldata_issimultaneous:
                if model_config["pre_post"]:
                    print ("Treatment period            Pre-post")
                else:
                    print ("Treatment period            " + str(int(treatment_statistics[1])) + " of " + str(int(treatment_statistics[4][0][2])) + " time points")
            else:
                if model_config["pre_post"]:
                    print ("Treatment period            Pre-post")
                else:
                    print ("Average treatment period    " + str(int(treatment_statistics[1])) + " of " + str(int(treatment_statistics[4][0][2])) + " time points")        

            print ("---------------------------------------------------------------")
            print ("Input data")
            if modeldata_isbalanced:
                print ("Balanced panel data         YES")
            else:
                print ("Balanced panel data         NO")
            if modeldata_isbinary:
                print ("Binary treatment            YES")
            else:
                print ("Binary treatment            NO")
            print ("Outcome variable            " + outcome_col_original + " (Mean=" + str(round(np.mean(model_data[outcome_col_original]), 2)) + " SD=" + str(round(np.std(model_data[outcome_col_original]), 2)) + ")")
            print ("Number of observations      " + str(len(model_data)))

        print ("---------------------------------------------------------------")
        print ("R-Squared                   " + str(round(model_statistics["rsquared"], 3)))
        print ("Adj. R-Squared              " + str(round(model_statistics["rsquared_adj"], 3)))
        print ("===============================================================")

        if not modeldata_isnotreatment[0] and modeldata_issimultaneous:
            print ("WARNING: All analysis units received the treatment exactly")
            print ("at the same time. There are no control conditions.")
        if model_config["GTE"]:
            print ("NOTE: For a full list of group treatment effects, use")
            print ("did_model.groupef(), did_model.plot_group_treatment_effects().")
        if model_config["ITE"]:
            print ("NOTE: For a full list of individual treatment effects, use")
            print ("did_model.indef(), did_model.plot_individual_treatment_effects().")

        model_diagnosis = {
            "isnotreatment": modeldata_isnotreatment[0],
            "issimultaneous": modeldata_issimultaneous,
            "isbalanced": modeldata_isbalanced,
            "isbinary": modeldata_isbinary
            }
        if modeldata_isparallel is not None:
            model_diagnosis["isparallel"] = modeldata_isparallel[0]
        
        return [
            model_results, 
            model_config, 
            model_data, 
            model_statistics,
            model_diagnosis,
            treatment_statistics,
            modeldata_isparallel
            ]

    def is_parallel(self):

        model_data = self.data[2]
        model_config = self.data[1]

        modeldata_isparallel = didtools.is_parallel(
            data = model_data,
            unit_col = model_config["unit_col"],
            time_col = model_config["time_col"],
            treatment_col = model_config["treatment_col"],
            outcome_col = model_config["outcome_col"],
            pre_post = model_config["pre_post"]
            )
        
        if modeldata_isparallel is not None:
            return modeldata_isparallel[1]
        else:
            return None
    
    def predictions(self):

        model_predictions = self.data[3]
        return model_predictions
    
    def counterfactual(self):
        
        olsmodel = self.olsmodel()

        predictions = self.predictions()
        
        model_data = self.data[2]
        
        model_config = self.data[1]
        treatment_col = model_config["treatment_col"]
        after_treatment_period = model_config["after_treatment_period"]
        after_treatment_col = model_config["after_treatment_col"]
        outcome_col = model_config["outcome_col"]

        model_data_mod = model_data.copy()
        model_data_mod[treatment_col] = 0
        if after_treatment_period:
            model_data_mod[after_treatment_col] = 0

        predictions_counterfac = olsmodel.predict(model_data_mod) 

        model_data_mod[outcome_col+"_pred"] = predictions
        model_data_mod[outcome_col+"_pred_counterfac"] = predictions_counterfac

        return model_data_mod

    def effects(self):

        model_results = self.data[0]

        effects_df = pd.DataFrame (columns = ["effect_name", "coef", "SE", "t", "p", "CI_lower", "CI_upper"])

        if "ATE" in model_results:
            ATE = pd.DataFrame([{
                "effect_name": "ATE",
                "coef": model_results["ATE"]["ATE"],
                "SE": model_results["ATE"]["ATE_SE"],
                "t": model_results["ATE"]["ATE_t"],
                "p": model_results["ATE"]["ATE_p"],
                "CI_lower": model_results["ATE"]["ATE_CI_lower"],
                "CI_upper": model_results["ATE"]["ATE_CI_upper"]
                }])
            if len(effects_df) == 0:
                effects_df = pd.DataFrame ({
                    "effect_name": ATE["effect_name"],
                    "coef": ATE["coef"],
                    "SE": ATE["SE"],
                    "t": ATE["t"],
                    "p": ATE["p"],
                    "CI_lower": ATE["CI_lower"],
                    "CI_upper": ATE["CI_upper"]})
            else:
                effects_df = pd.concat([effects_df, ATE], ignore_index=True)
            
        if "AATE" in model_results:
            AATE = pd.DataFrame([{
                "effect_name": "AATE",
                "coef": model_results["AATE"]["AATE"],
                "SE": model_results["AATE"]["AATE_SE"],
                "t": model_results["AATE"]["AATE_t"],
                "p": model_results["AATE"]["AATE_p"],
                "CI_lower": model_results["AATE"]["AATE_CI_lower"],
                "CI_upper": model_results["AATE"]["AATE_CI_upper"]
                }])
            effects_df = pd.concat([effects_df, AATE], ignore_index=True)

        if "Intercept" in model_results:
            Intercept = pd.DataFrame([{
                "effect_name": "Intercept",
                "coef": model_results["Intercept"]["Intercept"],
                "SE": model_results["Intercept"]["Intercept_SE"],
                "t": model_results["Intercept"]["Intercept_t"],
                "p": model_results["Intercept"]["Intercept_p"],
                "CI_lower": model_results["Intercept"]["Intercept_CI_lower"],
                "CI_upper": model_results["Intercept"]["Intercept_CI_upper"]
                }])
            effects_df = pd.concat([effects_df, Intercept], ignore_index=True)

        if "TG" in model_results:
            TG = pd.DataFrame([{
                "effect_name": "TG",
                "coef": model_results["TG"]["TG"],
                "SE": model_results["TG"]["TG_SE"],
                "t": model_results["TG"]["TG_t"],
                "p": model_results["TG"]["TG_p"],
                "CI_lower": model_results["TG"]["TG_CI_lower"],
                "CI_upper": model_results["TG"]["TG_CI_upper"]
                }])
            effects_df = pd.concat([effects_df, TG], ignore_index=True)

        if "TT" in model_results:
            TT = pd.DataFrame([{
                "effect_name": "TT",
                "coef": model_results["TT"]["TT"],
                "SE": model_results["TT"]["TT_SE"],
                "t": model_results["TT"]["TT_t"],
                "p": model_results["TT"]["TT_p"],
                "CI_lower": model_results["TT"]["TT_CI_lower"],
                "CI_upper": model_results["TT"]["TT_CI_upper"]
                }])
            effects_df = pd.concat([effects_df, TT], ignore_index=True)

        return effects_df

    def fixef(self):

        fixed_effects = self.data[4]
        return fixed_effects

    def indef(self):

        individual_effects = self.data[5]
        return individual_effects

    def groupef(self):

        group_effects = self.data[6]
        return group_effects

    def olsmodel(self):

        ols_model = self.data[8]
        return ols_model
    
    def placebo(
            self,
            divide: float = 0.5,
            resample: float = 1.0,
            random_state = 71
            ):

        if divide <= 0 or divide > 1:
            raise ValueError("Parameter share must be > 0 and <= 1")
        if resample <= 0 or resample > 1:
            raise ValueError("Parameter resample must be > 0 and <= 1")
        
        treatment_statistics = self.treatment_statistics()
        groups = treatment_statistics[2]
        control_group = groups[1]
        control_group_N = len(control_group)

        time_periods = treatment_statistics[4]
        treatment_period_start = time_periods[1][0]
        treatment_period_end = time_periods[1][1]
        treatment_period_start = pd.to_datetime(treatment_period_start)
        treatment_period_end = pd.to_datetime(treatment_period_end)

        model_config = self.data[1]
        model_data = self.data[2]
        unit_col = model_config["unit_col"]
        time_col = model_config["time_col"]

        model_data_c = model_data[model_data[unit_col].isin(control_group)].copy()
        model_data_c[time_col] = pd.to_datetime(model_data_c[time_col])
        model_data_c[unit_col] = model_data_c[unit_col].astype(str)

        units_random_sample = model_data_c[unit_col].sample(
            n = int(round(divide*control_group_N*resample, 0)), 
            random_state = random_state
            ).astype(str).tolist()

        model_data_c["TGP"] = 0
        model_data_c.loc[(model_data_c[unit_col].isin(units_random_sample)), "TGP"] = 1
        model_data_c["TGPxTT"] = model_data_c["TGP"] * model_data_c["TT"]
        
        model_data_c_analysis = did_analysis(
            data = model_data_c,
            unit_col = unit_col,
            time_col = time_col,
            treatment_col = "TGPxTT",
            outcome_col = model_config["outcome_col"],
            TG_col = model_config["TG_col"],
            TT_col = model_config["TT_col"],
            after_treatment_period = model_config["after_treatment_period"],
            after_treatment_col = model_config["after_treatment_col"],
            pre_post = model_config["pre_post"],
            log_outcome = model_config["log_outcome"],
            FE_unit = model_config["FE_unit"],
            FE_time = model_config["FE_time"],
            ITE = model_config["ITE"],
            GTE = model_config["GTE"],
            ITT = model_config["ITT"],
            GTT = model_config["GTT"],
            group_by = model_config["group_by"],
            covariates = model_config["covariates"],
            confint_alpha = model_config["confint_alpha"],
            drop_missing = model_config["drop_missing"],
            placebo = True    
            )
            
        return model_data_c_analysis

    def plot_timeline(
        self,
        x_label = "Time",
        y_label = "Analysis units",
        plot_title = "Treatment time",
        plot_symbol = "o",
        treatment_group_only = True
        ):

        model_config = self.data[1]
        model_data = self.data[2]
                
        if treatment_group_only:
            model_data = model_data[model_data[model_config["TG_col"]] == 1]

        modeldata_pivot = model_data.pivot_table (
            index = model_config["time_col"],
            columns = model_config["unit_col"],
            values = model_config["treatment_col"]
            )

        fig, ax = plt.subplots(figsize=(12, len(modeldata_pivot.columns) * 0.5))

        modeldata_pivot.index = pd.to_datetime(modeldata_pivot.index)

        for i, col in enumerate(modeldata_pivot.columns):
            time_points = modeldata_pivot.index
            treatment_data = np.zeros(len(time_points))
            time_points_treatment = modeldata_pivot.index[modeldata_pivot[col] == 1]
            values = [i] * len(time_points_treatment)
            ax.plot(time_points_treatment, values, plot_symbol, label=col)

        ax.set_xlabel(x_label)
        ax.set_yticks(range(len(modeldata_pivot.columns)))
        ax.set_yticklabels(modeldata_pivot.columns)
        ax.set_ylabel(y_label)
        ax.set_title(plot_title)
        ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))
        
        plt.xticks(rotation=90)
        plt.tight_layout()

        start_date = min(modeldata_pivot.index)
        end_date = max(modeldata_pivot.index)
        ax.set_xlim(start_date, end_date)

        plt.show()

        return modeldata_pivot

    def plot(
        self,
        x_label: str = "Time",
        y_label: str = "Outcome",
        plot_title: str = "Treatment group vs. control group",
        lines_col: list = ["blue", "green", "red", "orange"],
        lines_style: list = ["solid", "solid", "dashed", "dashed"],
        lines_labels: list = ["TG observed", "CG observed", "TG fit", "CG fit"],
        plot_legend: bool = True,
        plot_grid: bool = True,
        plot_observed: bool = False,
        plot_size_auto: bool = True,
        plot_size: list = [12, 6],
        pre_post_ticks: list = ["Pre", "Post"],
        pre_post_barplot = False,
        pre_post_bar_width = 0.5      
        ):

        model_config = self.data[1]
        model_data = self.data[2]
        model_predictions = self.data[3]
        model_data = model_data.reset_index()
    
        model_predictions = pd.DataFrame(model_predictions)
        model_predictions = model_predictions.reset_index()
        model_predictions.rename(columns = {0: "outcome_predicted"}, inplace = True)
    
        model_data = pd.concat ([model_data, model_predictions], axis = 1)
    
        model_data_TG = model_data[model_data["TG"] == 1]
        model_data_CG = model_data[model_data["TG"] == 0]
    
        model_data_TG_mean = model_data_TG.groupby(model_config["time_col"])[model_config["outcome_col"]].mean()
        model_data_TG_mean = model_data_TG_mean.reset_index()
        model_data_CG_mean = model_data_CG.groupby(model_config["time_col"])[model_config["outcome_col"]].mean()
        model_data_CG_mean = model_data_CG_mean.reset_index()
    
        model_data_TG_mean_pred = model_data_TG.groupby(model_config["time_col"])["outcome_predicted"].mean()
        model_data_TG_mean_pred = model_data_TG_mean_pred.reset_index()
        model_data_CG_mean_pred = model_data_CG.groupby(model_config["time_col"])["outcome_predicted"].mean()
        model_data_CG_mean_pred = model_data_CG_mean_pred.reset_index()
    
        model_data_TG_CG = pd.concat ([
            model_data_TG_mean.reset_index(),
            model_data_CG_mean[model_config["outcome_col"]].reset_index(),
            model_data_TG_mean_pred["outcome_predicted"].reset_index(),
            model_data_CG_mean_pred["outcome_predicted"].reset_index()
            ],
            axis = 1)
    
        model_data_TG_CG.columns.values[1] = "t"
        model_data_TG_CG.columns.values[2] = model_config["outcome_col"] + "_observed_TG"
        model_data_TG_CG.columns.values[4] = model_config["outcome_col"] + "_observed_CG"
        model_data_TG_CG.columns.values[6] = model_config["outcome_col"] + "_expected_TG"
        model_data_TG_CG.columns.values[8] = model_config["outcome_col"] + "_expected_CG"
    
        if plot_size_auto:
            if model_config["pre_post"]:
                fig, ax = plt.subplots(figsize=(7, 6))
            else:
                fig, ax = plt.subplots(figsize=(12, 6))
        else:
            fig, ax = plt.subplots(figsize=(plot_size[0], plot_size[1]))       
    
        model_data_TG_CG["t"] = pd.to_datetime(model_data_TG_CG["t"])

        if not model_config["pre_post"]:
            pre_post_barplot = False

        if pre_post_barplot:

            x_pos_t1_TG = 0
            x_pos_t1_CG = x_pos_t1_TG + pre_post_bar_width  
            x_pos_t2_TG = 1.5  
            x_pos_t2_CG = x_pos_t2_TG + pre_post_bar_width  

            plt.bar(
                x = x_pos_t1_TG, 
                height = model_data_TG_CG[model_config["outcome_col"] + "_expected_TG"][0], 
                label = lines_labels[2], 
                color = lines_col[2], 
                width = pre_post_bar_width
                )   
            plt.bar(
                x = x_pos_t1_CG, 
                height = model_data_TG_CG[model_config["outcome_col"] + "_expected_CG"][0], 
                label = lines_labels[3], 
                color = lines_col[3], 
                width = pre_post_bar_width
                )            
            plt.bar(
                x = x_pos_t2_TG, 
                height = model_data_TG_CG[model_config["outcome_col"] + "_expected_TG"][1],                 
                color = lines_col[2], 
                width = pre_post_bar_width
                )            
            plt.bar(
                x = x_pos_t2_CG, 
                height = model_data_TG_CG[model_config["outcome_col"] + "_expected_CG"][1],                 
                color=lines_col[3], 
                width = pre_post_bar_width
                )

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(plot_title)
            
        else:

            if plot_observed:
                plt.plot(
                    model_data_TG_CG["t"], 
                    model_data_TG_CG[model_config["outcome_col"] + "_observed_TG"], 
                    label = lines_labels[0], 
                    color=lines_col[0], 
                    linestyle=lines_style[0]
                    )
                plt.plot(
                    model_data_TG_CG["t"], 
                    model_data_TG_CG[model_config["outcome_col"] + "_observed_CG"], 
                    label = lines_labels[1], 
                    color=lines_col[1], 
                    linestyle=lines_style[1]
                    )
            
            plt.plot(
                model_data_TG_CG["t"], 
                model_data_TG_CG[model_config["outcome_col"] + "_expected_TG"], 
                label=lines_labels[2], 
                color=lines_col[2], 
                linestyle=lines_style[2]
                )
            plt.plot(
                model_data_TG_CG["t"], 
                model_data_TG_CG[model_config["outcome_col"] + "_expected_CG"], 
                label=lines_labels[3], 
                color=lines_col[3], 
                linestyle=lines_style[3]
                )

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(plot_title)
            ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))

        if model_config["pre_post"]:
            if not pre_post_barplot:
                plt.xticks(
                    model_data_TG_CG["t"].unique(), 
                    labels = [pre_post_ticks[0], pre_post_ticks[1]]
                    )  
            else:
                plt.xticks(
                    [0.25, 1.75], 
                    labels = [pre_post_ticks[0], pre_post_ticks[1]]
                    )  
        else:
            plt.xticks(rotation=90)
        
        plt.tight_layout()

        if plot_legend:
            plt.legend()

        if plot_grid:
            if not model_config["pre_post"]:
                plt.grid(True)
            else:
                plt.grid(axis='y', linestyle='-', alpha=0.7)

        plt.show()

        return model_data_TG_CG    

    def plot_counterfactual(
            self,
            x_label: str = "Time",
            y_label: str = "Outcome",
            plot_title: str = "Treatment group Counterfactual",
            lines_col: list = ["blue", "green"],
            lines_style: list = ["solid", "dashed"],
            lines_labels: list = ["TG", "TG counterfactual"],
            plot_legend: bool = True,
            plot_grid: bool = True,
            plot_size: list = [12, 6]
            ):

        model_config = self.data[1]
        outcome_col = model_config["outcome_col"]
        outcome_col_pred = outcome_col+"_pred"
        outcome_col_pred_counterfac = outcome_col+"_pred_counterfac"
        TG_col = model_config["TG_col"]
        time_col = model_config["time_col"]

        model_data_mod = self.counterfactual()

        model_data_mod_TG = model_data_mod[model_data_mod[TG_col] == 1]    
        model_data_TG_mean_pred = model_data_mod_TG.groupby(time_col)[outcome_col_pred].mean()
        model_data_TG_mean_pred = model_data_TG_mean_pred.reset_index()
        
        model_data_TG_mean_pred_counterfac = model_data_mod_TG.groupby(time_col)[outcome_col_pred_counterfac].mean()
        model_data_TG_mean_pred_counterfac = model_data_TG_mean_pred_counterfac.reset_index()
        model_data_TG_mean_pred_counterfac = model_data_TG_mean_pred_counterfac.drop(columns=[time_col])

        model_data_TG_mean = pd.concat ([
            model_data_TG_mean_pred.reset_index(),
            model_data_TG_mean_pred_counterfac.reset_index()
            ],
            axis = 1)
        model_data_TG_mean[time_col] = pd.to_datetime(model_data_TG_mean[time_col])

        fig, ax = plt.subplots(figsize=(plot_size[0], plot_size[1]))   
        
        plt.plot(
            model_data_TG_mean[time_col], 
            model_data_TG_mean[outcome_col_pred_counterfac], 
            label = lines_labels[1], 
            color = lines_col[1], 
            linestyle=lines_style[1]
            )
        plt.plot(
            model_data_TG_mean[time_col], 
            model_data_TG_mean[outcome_col_pred], 
            label = lines_labels[0], 
            color = lines_col[0], 
            linestyle = lines_style[0]
            )
        
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))
        print("model_config['date_format']: ", model_config["date_format"]) # TODO ?? RAUS
        if plot_legend:
            plt.legend()

        if plot_grid:
            if not model_config["pre_post"]:
                plt.grid(True)
            else:
                plt.grid(axis='y', linestyle='-', alpha=0.7)
        
        plt.xticks(rotation=90)
        plt.tight_layout()
        
        plt.show()

        return model_data_TG_mean
    
    def plot_effects(
        self,
        colors = ["blue", "grey"],
        x_label = "Coefficients with confidence intervals",
        plot_title = "DiD effects",
        plot_grid: bool = True,
        sort_by = "name",
        sort_ascending: bool = True,
        plot_size: list = [7, 6],      
        scale_plot: bool = True
        ):
        
        effects = self.effects()

        if sort_by == "coef":
            effects = effects.sort_values(
                by = "coef", 
                ascending = not sort_ascending
                )
        else:
            effects = effects.sort_values(
                by = "effect_name", 
                ascending = not sort_ascending
                )

        plt.figure(figsize=(plot_size[0], plot_size[1]))
        
        plt.errorbar(
            x = effects["coef"], 
            y = effects["effect_name"],
            xerr = [effects["coef"] - effects["CI_lower"], effects["CI_upper"] - effects["coef"]], 
                    fmt='o', 
                    color=colors[0], 
                    ecolor=colors[1], 
                    elinewidth=2, 
                    capsize=4, 
                    label="")
    
        if scale_plot:
            maxval = effects[["coef", "CI_lower", "CI_upper"]].abs().max().max()
            maxval_plot = maxval*1.1
            plt.xlim(-maxval_plot, maxval_plot)

        plt.xlabel(x_label, fontsize=12)
        plt.title(plot_title, fontsize=14)
        
        if plot_grid:
            plt.grid(True)

        plt.show()

    def plot_group_treatment_effects (
            self,
            colors = ["blue", "grey"],
            x_label = "Treatment effect",
            y_label = "Groups",
            plot_title = "Group treatment effects",        
            treatment_group_only = False,
            sort_by = "group",
            sort_ascending = True,
            plot_size: list = [9, 6],
            show_central_tendency = False,
            central_tendency = "mean"
            ):

        model_config = self.data[1]
        if not model_config["GTE"]:
            raise ValueError ("Model does not include group treatment effects. Set GTE=True an define grouping variable using group_by.")
        group_by = model_config["group_by"]
        if group_by is None:
            raise ValueError ("Grouping variable is not defined. Define a grouping variable using group_by.")
        
        group_treatment_effects = self.data[6][1]
        if treatment_group_only:
            TG_col = model_config["TG_col"]
            model_data = self.data[2]
            treatment_group = model_data[model_data[TG_col] == 1].drop_duplicates(subset=[group_by])[group_by]
            group_treatment_effects = group_treatment_effects[group_treatment_effects[group_by].isin(treatment_group)]
        if sort_by == "coef":
            group_treatment_effects = group_treatment_effects.sort_values(
                by = "coef", 
                ascending = not sort_ascending
                )
        else:
            group_treatment_effects = group_treatment_effects.sort_values(
                by = group_by, 
                ascending = not sort_ascending
                )
        
        plt.figure(figsize=(plot_size[0], plot_size[1]))
        
        plt.errorbar(
            x = group_treatment_effects["coef"], 
            y = group_treatment_effects[group_by],
            xerr = [group_treatment_effects["coef"] - group_treatment_effects["lower"], group_treatment_effects["upper"] - group_treatment_effects["coef"]], 
                    fmt='o', 
                    color=colors[0], 
                    ecolor=colors[1], 
                    elinewidth=2, 
                    capsize=4, 
                    label="")

        if show_central_tendency:
            if central_tendency == "median":
                ITE_ct = np.median(group_treatment_effects["coef"])
            else:
                ITE_ct = np.mean(group_treatment_effects["coef"])
            plt.axvline(x = ITE_ct, color = "black")
        else:
            pass

        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(plot_title, fontsize=14)
        plt.grid(True)
        
        plt.show()

    def plot_individual_treatment_effects (
            self,
            colors = ["blue", "grey"],
            x_label = "Treatment effect",
            y_label = "Analysis units",
            plot_title = "Individual treatment effects",        
            treatment_group_only = False,
            sort_by = "unit",
            sort_ascending = True,
            plot_size: list = [9, 6],
            show_central_tendency = False,
            central_tendency = "mean"
            ):

        model_config = self.data[1]
        if not model_config["ITE"]:
            raise ValueError ("Model does not include individuel treatment effects. Set ITE=True for including.")        
        unit_col = model_config["unit_col"]
        
        individual_treatment_effects = self.data[5][1]
        if treatment_group_only:
            TG_col = model_config["TG_col"]
            model_data = self.data[2]
            treatment_group = model_data[model_data[TG_col] == 1].drop_duplicates(subset=[unit_col])[unit_col]
            individual_treatment_effects = individual_treatment_effects[individual_treatment_effects[unit_col].isin(treatment_group)]
        if sort_by == "coef":
            individual_treatment_effects = individual_treatment_effects.sort_values(
                by = "coef", 
                ascending = not sort_ascending
                )
        else:
            individual_treatment_effects = individual_treatment_effects.sort_values(
                by = unit_col, 
                ascending = not sort_ascending
                )
        
        plt.figure(figsize=(plot_size[0], plot_size[1]))
        
        plt.errorbar(
            x = individual_treatment_effects["coef"], 
            y = individual_treatment_effects[unit_col],
            xerr = [individual_treatment_effects["coef"] - individual_treatment_effects["lower"], individual_treatment_effects["upper"] - individual_treatment_effects["coef"]], 
                    fmt='o', 
                    color=colors[0], 
                    ecolor=colors[1], 
                    elinewidth=2, 
                    capsize=4, 
                    label="")

        if show_central_tendency:
            if central_tendency == "median":
                ITE_ct = np.median(individual_treatment_effects["coef"])
            else:
                ITE_ct = np.mean(individual_treatment_effects["coef"])
            plt.axvline(x = ITE_ct, color = "black")
        else:
            pass

        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(plot_title, fontsize=14)
        plt.grid(True)

        plt.show()

def did_analysis(
    data,
    unit_col,
    time_col,
    treatment_col,
    outcome_col,
    TG_col = None,
    TT_col = None,
    after_treatment_period: bool = False,
    after_treatment_col = None,
    pre_post = False,
    log_outcome: bool = False,
    log_outcome_add = 0.01,
    FE_unit: bool = False,
    FE_time: bool = False,
    ITE: bool = False,
    GTE: bool = False,
    ITT: bool = False,
    GTT: bool = False,
    group_by = None,
    covariates = None,
    group_benefit: list = [],
    placebo = False,
    confint_alpha = 0.05,
    freq = "D",
    date_format = "%Y-%m-%d",
    drop_missing: bool = True,
    missing_replace_by_zero: bool = False
    ):
    
    if ITE:
        GTE = False
    if ITT:
        GTT = False
    
    cols_relevant = [
        unit_col,
        time_col,
        treatment_col,
        outcome_col]
    
    groups = didtools.is_notreatment(
            data = data,
            unit_col = unit_col,
            treatment_col = treatment_col
            )
    treatment_group = groups[1]

    if after_treatment_period:
        cols_relevant = cols_relevant + [after_treatment_col]

    if TG_col is not None:
        cols_relevant.append(TG_col)
    else:
        FE_unit = True
        
        data["TG"] = 0
        data.loc[data[unit_col].isin(treatment_group), "TG"] = 1

        TG_col = "TG"

        cols_relevant = [
        unit_col,
        time_col,
        treatment_col,
        TG_col,
        outcome_col
        ]

    if TT_col is not None:
        cols_relevant.append(TT_col)
    else:
        FE_time = True

    if covariates is not None:
        cols_relevant.extend(covariates)

    data = data[cols_relevant].copy()

    if "date_counter" not in data.columns:
        data = didtools.date_counter(
            data,
            time_col,
            new_col = "date_counter"
            )

    modeldata_ismissing = didtools.is_missing(
        data, 
        drop_missing = drop_missing,
        missing_replace_by_zero = missing_replace_by_zero
        )

    if modeldata_ismissing[0]:
        print("Variables contain NA values: "+'+'.join(modeldata_ismissing[1]), end = ". ")

        if drop_missing or missing_replace_by_zero:
            data = modeldata_ismissing[2]
                
        if drop_missing:
            print ("Rows with missing values are skipped.")
        elif missing_replace_by_zero:
            print ("Missing values are replaced by 0.")
        else:
            print ("Missing values are not cleaned. Model may crash.")
        
    if log_outcome:
        if missing_replace_by_zero:
            data["log_"+f'{outcome_col}'] = np.log(data[outcome_col]+log_outcome_add)
        else:
            data["log_"+f'{outcome_col}'] = np.log(data[outcome_col])
        outcome_col = "log_"+f'{outcome_col}'

    did_formula = f'{outcome_col} ~ {treatment_col}'

    if TG_col is not None and not ITE and not GTE:
        did_formula = did_formula + f'+ {TG_col}'
    if TT_col is not None:
        did_formula = did_formula + f'+ {TT_col}'
   
    if ITT:
        FE_unit = True
        FE_time = False

    if ITE:
        FE_unit = True

    if after_treatment_period:
        did_formula = did_formula + f'+ {after_treatment_col}'
    
    if FE_unit:
        data[unit_col] = data[unit_col].astype(str)
        did_formula = did_formula + f'+ {unit_col}'

    if FE_time:
        data[time_col] = data[time_col].astype(str)
        did_formula = did_formula + f'+ {time_col}'
    
    if GTE or GTT:
    
        if group_by is None:
            print ("Grouping variable is not defined. Define a grouping variable using group_by.")
        else:
            group_dummies = pd.DataFrame(pd.get_dummies(data[group_by].astype(str), dtype = int, prefix = "group"))
            group_names = group_dummies.columns
            group_names = list(map(lambda name: name[6:], group_names))
            group_dummies.columns = group_dummies.columns.str.replace(r'[^A-Za-z0-9_]', '', regex=True)
            data = pd.concat([data, group_dummies], axis = 1)
            GTE_columns_group = '+'.join(group_dummies.columns)
        
    if ITT or ITE:

        unit_dummies = pd.DataFrame(pd.get_dummies(data[unit_col].astype(str), dtype = int, prefix = "unit"))
        unit_names = unit_dummies.columns
        unit_names = list(map(lambda name: name[5:], unit_names))
        unit_dummies.columns = unit_dummies.columns.str.replace(r'[^A-Za-z0-9_]', '', regex=True)
        data = pd.concat([data, unit_dummies], axis = 1)
        ITT_columns_unit = '+'.join(unit_dummies.columns)

    if GTT:
        
        if group_by is None:
            print ("Group time trends are desired, but no grouping variable (group_by) was stated. No group time trends are estimated.")
        else:           
            group_x_time = pd.DataFrame()
            for col in group_dummies.columns:
                group_x_time[col] = group_dummies[col] * data["date_counter"]
                new_col_name = f"{col}_x_time"
                group_x_time = group_x_time.rename(columns={col: new_col_name})

            data = pd.concat([data, group_x_time], axis = 1)

            GTT_columns_groupxtime = '+'.join(group_x_time.columns)
            did_formula = did_formula + f'+{GTE_columns_group}+{GTT_columns_groupxtime}'
            did_formula = did_formula.replace(group_by, '').strip()
             

    if ITT:
        
        if "date_counter" not in data.columns:
            data = didtools.date_counter(
                data,
                time_col,
                new_col="date_counter"
                )
        
        unit_x_time = pd.DataFrame()
        for col in unit_dummies.columns:
            unit_x_time[col] = unit_dummies[col] * data["date_counter"]
            new_col_name = f"{col}_x_time"
            unit_x_time = unit_x_time.rename(columns={col: new_col_name})

        data = pd.concat([data, unit_x_time], axis = 1)

        ITT_columns_unitxtime = '+'.join(unit_x_time.columns)
        did_formula = did_formula + f'+{ITT_columns_unit}+{ITT_columns_unitxtime}'
        did_formula = did_formula.replace(unit_col, '').strip()
    
    if GTE:

        if group_by is None:
            pass
        else:
            group_x_treatment = pd.DataFrame()
            for col in group_dummies.columns:
                group_x_treatment[col] = group_dummies[col] * data[treatment_col]
                new_col_name = f"{col}_x_treatment"
                group_x_treatment = group_x_treatment.rename(columns={col: new_col_name})

            data = pd.concat([data, group_x_treatment], axis = 1)

            GTE_columns_groupxtreatment = '+'.join(group_x_treatment.columns)
            did_formula = did_formula + f'+{GTE_columns_group}+{GTE_columns_groupxtreatment}'
            did_formula = did_formula.replace(group_by, '').strip()

            did_formula = did_formula.replace(f'{treatment_col}+', "")

    if ITE:

        unit_x_treatment = pd.DataFrame()
        for col in unit_dummies.columns:
            unit_x_treatment[col] = unit_dummies[col] * data[treatment_col]
            new_col_name = f"{col}_x_treatment"
            unit_x_treatment = unit_x_treatment.rename(columns={col: new_col_name})

        data = pd.concat([data, unit_x_treatment], axis = 1)

        ITE_columns_unitxtreatment = '+'.join(unit_x_treatment.columns)
        did_formula = did_formula + f'+{ITT_columns_unit}+{ITE_columns_unitxtreatment}'
        did_formula = did_formula.replace(unit_col, '').strip()

        did_formula = did_formula.replace(f'{treatment_col}+', "")
    
    if FE_time or FE_unit or GTT or GTE:
        did_formula = did_formula + f' -1'

    if covariates is not None:
        covariates_columns = '+'.join(covariates)
        did_formula = did_formula + f'+{covariates_columns}'

    if len(group_benefit) > 0:

        DDD = True

        if "TG" not in data.columns:
            data["TG"] = 0
            data.loc[data[unit_col].isin(treatment_group), "TG"] = 1

            TG_col = "TG"
        
        data["group_benefit"] = 0
        data.loc[data[unit_col].astype(str).isin(group_benefit.astype(str)), "group_benefit"] = 1
        
        data["TG_x_groupbenefit"] = data["TG"] * data["group_benefit"]
        data["groupbenefit_x_treatment"] = data["group_benefit"] * data[treatment_col]
        data["TG_x_groupbenefit_x_treatment"] = data["TG"] * data["group_benefit"] * data[treatment_col]

        did_formula = did_formula + f'+ group_benefit + TG_x_groupbenefit + groupbenefit_x_treatment + TG_x_groupbenefit_x_treatment'
        
    else:
        DDD = False
    
    analysis_description = "Difference in Differences (DiD) Analysis"
    if DDD:
        analysis_description = "Difference in Difference in Differences (DDD) Analysis"
    if placebo:
        analysis_description = "Placebo Difference in Differences (DiD) Analysis"

    model_config = {
        "TG_col": TG_col,
        "TT_col": TT_col,
        "treatment_col": treatment_col,
        "unit_col": unit_col,
        "time_col": time_col,
        "outcome_col": outcome_col,
        "log_outcome": log_outcome,
        "freq": freq,
        "date_format": date_format,
        "after_treatment_period": after_treatment_period,
        "after_treatment_col": after_treatment_col,
        "pre_post": pre_post,
        "FE_unit": FE_unit,
        "FE_time": FE_time,
        "ITT": ITT,
        "GTT": GTT,
        "ITE": ITE,
        "GTE": GTE,
        "group_by": group_by,
        "covariates": covariates,
        "DDD": DDD,
        "placebo": placebo,
        "confint_alpha": confint_alpha,
        "drop_missing": drop_missing,
        "did_formula": did_formula,
        "analysis_description": analysis_description
        }

    ols_model = ols(did_formula, data = data).fit()

    ols_coefficients = ols_model.params
    coef_conf_standarderrors = ols_model.bse
    coef_conf_t = ols_model.tvalues
    coef_conf_p = ols_model.pvalues
    coef_conf_intervals = ols_model.conf_int(alpha = confint_alpha)

    if not ITE and not GTE:
        
        ATE = ols_coefficients[treatment_col]
        ATE_SE = round(coef_conf_standarderrors[treatment_col], 3)
        ATE_t = round(coef_conf_t[treatment_col], 3)
        ATE_p = round(coef_conf_p[treatment_col], 3)
        ATE_CI_lower = coef_conf_intervals.loc[treatment_col, 0]
        ATE_CI_upper = coef_conf_intervals.loc[treatment_col, 1]

        ATE = {
            "ATE": ATE, 
            "ATE_SE": ATE_SE, 
            "ATE_t": ATE_t, 
            "ATE_p": ATE_p, 
            "ATE_CI_lower": ATE_CI_lower,
            "ATE_CI_upper": ATE_CI_upper
            }

        model_results = {"ATE": ATE}
    
    else:
        model_results = {"ATE": None}

    if GTE:

        if group_by is None:

            print ("Group treatment effects are desired, but no grouping variable (group_by) was stated. Calculating effects for treatment group only.")

            ATE = ols_coefficients[treatment_col]
            ATE_SE = round(coef_conf_standarderrors[treatment_col], 3)
            ATE_t = round(coef_conf_t[treatment_col], 3)
            ATE_p = round(coef_conf_p[treatment_col], 3)
            ATE_CI_lower = coef_conf_intervals.loc[treatment_col, 0]
            ATE_CI_upper = coef_conf_intervals.loc[treatment_col, 1]

            ATE = {
                "ATE": ATE, 
                "ATE_SE": ATE_SE, 
                "ATE_t": ATE_t, 
                "ATE_p": ATE_p, 
                "ATE_CI_lower": ATE_CI_lower,
                "ATE_CI_upper": ATE_CI_upper
                }

            model_results = {"ATE": ATE}

        else:
            model_results = {"ATE": None}

    if not FE_time and not FE_unit and not GTE and not GTT:

        TG = ols_coefficients[TG_col]
        TG_SE = round(coef_conf_standarderrors[TG_col], 3)
        TG_t = round(coef_conf_t[TG_col], 3)
        TG_p = round(coef_conf_p[TG_col], 3)
        TG_CI_lower = coef_conf_intervals.loc[TG_col, 0]
        TG_CI_upper = coef_conf_intervals.loc[TG_col, 1]

        TG = {
            "TG": TG, 
            "TG_SE": TG_SE, 
            "TG_t": TG_t, 
            "TG_p": TG_p,
            "TG_CI_lower": TG_CI_lower,
            "TG_CI_upper": TG_CI_upper
            }

        model_results["TG"] = TG

        TT = ols_coefficients[TT_col]
        TT_SE = round(coef_conf_standarderrors[TT_col], 3)
        TT_t = round(coef_conf_t[TT_col], 3)
        TT_p = round(coef_conf_p[TT_col], 3)
        TT_CI_lower = coef_conf_intervals.loc[TT_col, 0]
        TT_CI_upper = coef_conf_intervals.loc[TT_col, 1]

        TT = {
            "TT": TT, 
            "TT_SE": TT_SE, 
            "TT_t": TT_t, 
            "TT_p": TT_p,
            "TT_CI_lower": TT_CI_lower,
            "TT_CI_upper": TT_CI_upper
            }

        model_results["TT"] = TT

        Intercept = ols_coefficients["Intercept"]
        Intercept_SE = round(coef_conf_standarderrors["Intercept"], 3)
        Intercept_t = round(coef_conf_t["Intercept"], 3)
        Intercept_p = round(coef_conf_p["Intercept"], 3)
        Intercept_CI_lower = coef_conf_intervals.loc["Intercept", 0]
        Intercept_CI_upper = coef_conf_intervals.loc["Intercept", 1]

        Intercept = {
            "Intercept": Intercept, 
            "Intercept_SE": Intercept_SE, 
            "Intercept_t": Intercept_t, 
            "Intercept_p": Intercept_p,
            "Intercept_CI_lower": Intercept_CI_lower,
            "Intercept_CI_upper": Intercept_CI_upper
            }

        model_results["Intercept"] = Intercept

    else:

        if TG_col is not None and not ITE and not GTE and not GTT:

            TG = ols_coefficients[TG_col]
            TG_SE = round(coef_conf_standarderrors[TG_col], 3)
            TG_t = round(coef_conf_t[TG_col], 3)
            TG_p = round(coef_conf_p[TG_col], 3)
            TG_CI_lower = coef_conf_intervals.loc[TG_col, 0]
            TG_CI_upper = coef_conf_intervals.loc[TG_col, 1]

            TG = {
                "TG": TG, 
                "TG_SE": TG_SE, 
                "TG_t": TG_t, 
                "TG_p": TG_p,
                "TG_CI_lower": TG_CI_lower,
                "TG_CI_upper": TG_CI_upper
                }

            model_results["TG"] = TG

        if TT_col is not None:

            TT = ols_coefficients[TT_col]
            TT_SE = round(coef_conf_standarderrors[TT_col], 3)
            TT_t = round(coef_conf_t[TT_col], 3)
            TT_p = round(coef_conf_p[TT_col], 3)
            TT_CI_lower = coef_conf_intervals.loc[TT_col, 0]
            TT_CI_upper = coef_conf_intervals.loc[TT_col, 1]

            TT = {
                "TT": TT, 
                "TT_SE": TT_SE, 
                "TT_t": TT_t, 
                "TT_p": TT_p,
                "TT_CI_lower": TT_CI_lower,
                "TT_CI_upper": TT_CI_upper
                }

            model_results["TT"] = TT

    if after_treatment_period:

        AATE = ols_coefficients[after_treatment_col]
        AATE_SE = round(coef_conf_standarderrors[after_treatment_col], 3)
        AATE_t = round(coef_conf_t[after_treatment_col], 3)
        AATE_p = round(coef_conf_p[after_treatment_col], 3)
        AATE_CI_lower = coef_conf_intervals.loc[after_treatment_col, 0]
        AATE_CI_upper = coef_conf_intervals.loc[after_treatment_col, 1]

        AATE = {
            "AATE": AATE, 
            "AATE_SE": AATE_SE, 
            "AATE_t": AATE_t, 
            "AATE_p": AATE_p,
            "AATE_CI_lower": AATE_CI_lower,
            "AATE_CI_upper": AATE_CI_upper
            }

        model_results["AATE"] = AATE

    if DDD:
        
        ATET = ols_coefficients["TG_x_groupbenefit_x_treatment"]
        ATET_SE = round(coef_conf_standarderrors["TG_x_groupbenefit_x_treatment"], 3)
        ATET_t = round(coef_conf_t["TG_x_groupbenefit_x_treatment"], 3)
        ATET_p = round(coef_conf_p["TG_x_groupbenefit_x_treatment"], 3)
        ATET_CI_lower = coef_conf_intervals.loc["TG_x_groupbenefit_x_treatment", 0]
        ATET_CI_upper = coef_conf_intervals.loc["TG_x_groupbenefit_x_treatment", 1]
        ATET = {
            "ATET": ATET, 
            "ATET_SE": ATET_SE, 
            "ATET_t": ATET_t, 
            "ATET_p": ATET_p,
            "ATET_CI_lower": ATET_CI_lower,
            "ATET_CI_upper": ATET_CI_upper
            }
        model_results["ATET"] = ATET

        BG = ols_coefficients["group_benefit"]
        BG_SE = round(coef_conf_standarderrors["group_benefit"], 3)
        BG_t = round(coef_conf_t["group_benefit"], 3)
        BG_p = round(coef_conf_p["group_benefit"], 3)
        BG_CI_lower = coef_conf_intervals.loc["group_benefit", 0]
        BG_CI_upper = coef_conf_intervals.loc["group_benefit", 1]
        BG = {
            "BG": BG, 
            "BG_SE": BG_SE, 
            "BG_t": BG_t, 
            "BG_p": BG_p,
            "BG_CI_lower": BG_CI_lower,
            "BG_CI_upper": BG_CI_upper
            }
        model_results["BG"] = BG

        TBG = ols_coefficients["TG_x_groupbenefit"]
        TBG_SE = round(coef_conf_standarderrors["TG_x_groupbenefit"], 3)
        TBG_t = round(coef_conf_t["TG_x_groupbenefit"], 3)
        TBG_p = round(coef_conf_p["TG_x_groupbenefit"], 3)
        TBG_CI_lower = coef_conf_intervals.loc["TG_x_groupbenefit", 0]
        TBG_CI_upper = coef_conf_intervals.loc["TG_x_groupbenefit", 1]
        TBG = {
            "TBG": TBG, 
            "TBG_SE": TBG_SE, 
            "TBG_t": TBG_t, 
            "TBG_p": TBG_p,
            "TBG_CI_lower": TBG_CI_lower,
            "TBG_CI_upper": TBG_CI_upper
            }
        model_results["TBG"] = TBG

        TTB = ols_coefficients["groupbenefit_x_treatment"]
        TTB_SE = round(coef_conf_standarderrors["groupbenefit_x_treatment"], 3)
        TTB_t = round(coef_conf_t["groupbenefit_x_treatment"], 3)
        TTB_p = round(coef_conf_p["groupbenefit_x_treatment"], 3)
        TTB_CI_lower = coef_conf_intervals.loc["groupbenefit_x_treatment", 0]
        TTB_CI_upper = coef_conf_intervals.loc["groupbenefit_x_treatment", 1]
        TTB = {
            "TTB": TTB, 
            "TTB_SE": TTB_SE, 
            "TTB_t": TTB_t, 
            "TTB_p": TTB_p,
            "TTB_CI_lower": TTB_CI_lower,
            "TTB_CI_upper": TTB_CI_upper
            }
        model_results["TTB"] = TTB

    model_predictions = ols_model.predict()

    model_statistics = {
        "rsquared": ols_model.rsquared,
        "rsquared_adj": ols_model.rsquared_adj,
        }

    fixed_effects = [None, None]

    if FE_unit:

        FE_unit_coef = {var: coef for var, coef in ols_coefficients.items() if var.startswith(unit_col)}
        FE_unit_coef_df = pd.DataFrame(list(FE_unit_coef.items()), columns = [unit_col, "coef"])
        FE_unit_coef_df.set_index(unit_col, inplace = True)

        fixed_effects[0] = FE_unit_coef_df

    if FE_time:

        FE_time_coef = {var: coef for var, coef in ols_coefficients.items() if var.startswith(time_col)}

        FE_time_coef_df = pd.DataFrame(list(FE_time_coef.items()), columns = [time_col, "coef"])
        FE_time_coef_df.set_index(time_col, inplace = True)

        fixed_effects[1] = FE_time_coef_df

    individual_effects = [None, None]

    if ITT:
        
        ITT_coef = {var: coef for var, coef in ols_coefficients.items() if var.endswith("_x_time")}
        ITT_coef_df = pd.DataFrame(ITT_coef.items(), columns = ["unit_x_time", "coef"])
        ITT_coef_df.set_index("unit_x_time", inplace = True)
        
        ITT_coef_confint = coef_conf_intervals[coef_conf_intervals.index.str.endswith('_x_time')]
        ITT_coef_df["lower"] = ITT_coef_confint[0]
        ITT_coef_df["upper"] = ITT_coef_confint[1]       
        ITT_coef_df[unit_col] = unit_names
        
        individual_effects[0] = ITT_coef_df

    if ITE:
        
        ITE_coef = {var: coef for var, coef in ols_coefficients.items() if var.endswith("_x_treatment")}
        ITE_coef_df = pd.DataFrame(ITE_coef.items(), columns = ["unit_x_treatment", "coef"])
        ITE_coef_df.set_index("unit_x_treatment", inplace = True)
        ITE_coef_df["SE"] = {var: SE for var, SE in coef_conf_standarderrors.items() if var.endswith("_x_treatment")}
        ITE_coef_df["t"] = {var: tval for var, tval in coef_conf_t.items() if var.endswith("_x_treatment")}
        ITE_coef_df["p"] = {var: pval for var, pval in coef_conf_p.items() if var.endswith("_x_treatment")}
            
        ITE_coef_confint = coef_conf_intervals[coef_conf_intervals.index.str.endswith('_x_treatment')]
        ITE_coef_df["lower"] = ITE_coef_confint[0]
        ITE_coef_df["upper"] = ITE_coef_confint[1]
        
        ITE_coef_df[unit_col] = unit_names

        individual_effects[1] = ITE_coef_df

    group_effects = [None, None]

    if GTT:

        GTT_coef = {var: coef for var, coef in ols_coefficients.items() if var.endswith("_x_time")}
        GTT_coef_df = pd.DataFrame(GTT_coef.items(), columns = ["group_x_time", "coef"])
        GTT_coef_df.set_index("group_x_time", inplace = True)
        
        GTT_coef_confint = coef_conf_intervals[coef_conf_intervals.index.str.endswith('_x_time')]
        GTT_coef_df["lower"] = GTT_coef_confint[0]
        GTT_coef_df["upper"] = GTT_coef_confint[1]
        
        GTT_coef_df[unit_col] = group_names
        
        group_effects[0] = GTT_coef_df

    if GTE:

        if group_by is None:
            pass
        else:
            GTE_coef = {var: coef for var, coef in ols_coefficients.items() if var.endswith("_x_treatment")}
            GTE_coef_df = pd.DataFrame(GTE_coef.items(), columns = ["group_x_treatment", "coef"])
            GTE_coef_df.set_index("group_x_treatment", inplace = True)
            GTE_coef_df["SE"] = {var: SE for var, SE in coef_conf_standarderrors.items() if var.endswith("_x_treatment")}
            GTE_coef_df["t"] = {var: tval for var, tval in coef_conf_t.items() if var.endswith("_x_treatment")}
            GTE_coef_df["p"] = {var: pval for var, pval in coef_conf_p.items() if var.endswith("_x_treatment")}
            
            GTE_coef_confint = coef_conf_intervals[coef_conf_intervals.index.str.endswith('_x_treatment')]
            GTE_coef_df["lower"] = GTE_coef_confint[0]
            GTE_coef_df["upper"] = GTE_coef_confint[1]          
            GTE_coef_df[group_by] = group_names

            group_effects[1] = GTE_coef_df

    did_model_output = did_model(
        model_results,
        model_config,
        data,
        model_predictions,
        fixed_effects,
        individual_effects,
        group_effects,
        model_statistics,
        ols_model
        ) 

    return did_model_output