# -*- coding: utf-8 -*-：
import pandas as pd

from Tool.functions.get_effective_data import get_effective_data
from Tool.functions.read.get_something import get_ins, get_para, get_id, get_hypothesis_re, get_ipo
from Tool.functions import indus_code_forA as indc
from Tool.functions.read.read_data_for_light_val import read_df
from Config.mongodb import read_mongo_limit


def get_data_for_real_estate(VID):
    bal_list, flow_list, indus, hy_id, bm_id, market = get_id(VID)
    bal_df = read_df("rdt_fintech", "NewBal", bal_list)
    flow_df = read_df("rdt_fintech", "NewFlow", flow_list)
    income_business_income_taxes = read_mongo_limit("rdt_fintech", "Hypo", {"_id": hy_id}, None)["tr"].values[0]
    indus_code, code_list = get_ins(indus)
    shorttermborrowings, shorttermdebenturespayable, currentportionofnoncurrentliabilitiy, longtermborrowings, \
    debenturespayable, totalasset, totalliabilities, constructioninprogress, sc, \
    financial_year = get_bal_data(bal_list, bal_df)
    netprofit, totaloperatingrevenue = get_flow_data(flow_list, flow_df)
    building_construction_area, cpi_reside_rent_y, land_transaction_price_m, land_acquisition_area_m, \
    real_estate_development_enterprises_funds_m, per_consumption_expenditure_reside, \
    per_capita_disposable_income_reside = read_mongo_real()
    [pc_A, pc_3, pc_pbp] = get_para(VID)[:3]
    pc = {'pc_A': pc_A, 'pc_3': pc_3, 'pc_pbp': pc_pbp}
    new_code = indc.retrack_Ainsudcode("indus_gr_decision_tree", indus_code)
    cs, re, riskfree_rate = get_hypothesis_re(new_code)
    ipo = get_ipo(VID)

    return [indus_code, shorttermborrowings, shorttermdebenturespayable, currentportionofnoncurrentliabilitiy,
            longtermborrowings, debenturespayable, income_business_income_taxes, netprofit, totalasset,
            totalliabilities,
            totaloperatingrevenue, constructioninprogress, sc, building_construction_area, cpi_reside_rent_y,
            land_transaction_price_m, land_acquisition_area_m,
            real_estate_development_enterprises_funds_m, per_consumption_expenditure_reside,
            per_capita_disposable_income_reside, pc, financial_year, cs, re, riskfree_rate, market, ipo]


def read_mongo_real():
    valuation_china_realestate_year = get_effective_data("AM_origin", "valuation_china_realestate_year")
    valuation_china_realestate_month = get_effective_data("AM_origin", "valuation_china_realestate_month")
    valuation_china_citizen_expense_season = get_effective_data("AM_origin", "valuation_china_citizen_expense_season")
    [building_construction_area, cpi_reside_rent_y] = valuation_china_realestate_year.values.tolist()
    [land_acquisition_area_m, land_transaction_price_m, real_estate_development_enterprises_funds_m] = \
        valuation_china_realestate_month.values.tolist()
    [per_capita_disposable_income_reside, per_consumption_expenditure_reside] = \
        valuation_china_citizen_expense_season.values.tolist()

    return building_construction_area, cpi_reside_rent_y, land_transaction_price_m, land_acquisition_area_m, real_estate_development_enterprises_funds_m, \
           per_consumption_expenditure_reside, per_capita_disposable_income_reside


def get_bal_data(bal_list, bal_df):
    # bal_dict = {}
    # for i in bal_list:
    #     bal_dict[i] = {}
    demo = bal_df[bal_df["_id"] == bal_list[0]]
    shorttermborrowings = demo["e1001"].values[0]
    shorttermdebenturespayable = demo["e1002"].values[0]
    currentportionofnoncurrentliabilitiy = demo["e1041"].values[0]
    longtermborrowings = demo["e1101"].values[0]
    debenturespayable = demo["e1102"].values[0]
    totalasset = demo["e0s"].values[0]
    totalliabilities = demo["e1s"].values[0]
    constructioninprogress = demo["e0113"].values[0]
    sc = demo["e2001"].values[0]
    #     bal_dict[i]["Dr"] = demo["e9900"]
    #     bal_dict[i]["Ap"] = demo["e9900"]
    #     bal_dict[i]["debt"] = demo["e1001"]
    #     bal_dict[i]["Cash"] = demo["e000101"]
    #     bal_dict[i]["Inv"] = demo["e0031"]
    #     bal_dict[i]["AR"] = demo["e0022"]
    #     bal_dict[i]["TA"] = demo["e0s"]
    #     bal_dict[i]["L"] = demo["e1s"]
    #     bal_dict[i]["SC"] = demo["e2001"]
    financialreport_year = demo["date"].values[0]
    financial_year = str(financialreport_year)[:4]
    return shorttermborrowings, shorttermdebenturespayable, currentportionofnoncurrentliabilitiy, longtermborrowings, \
           debenturespayable, totalasset, totalliabilities, constructioninprogress, sc, financial_year


def get_flow_data(flow_list, flow_df):
    # bal_dict = {}
    # for i in bal_list:
    #     bal_dict[i] = {}
    demo = flow_df[flow_df["_id"] == flow_list[0]]
    netprofit = demo["e35s1"].values[0]
    totaloperatingrevenue = demo["e31"].values[0]
    #     bal_dict[i]["NI"] = demo["e35s1"]
    #     bal_dict[i]["EBIT"] = demo["e33s1"]
    #     bal_dict[i]["EBT"] = demo["e34s1"]
    #     bal_dict[i]["REV"] = [demo["e3101"], demo["e8011"], demo["e8012"]]
    return netprofit, totaloperatingrevenue
