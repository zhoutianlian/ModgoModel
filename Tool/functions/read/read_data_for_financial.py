# -*- coding: utf-8 -*-：
import pandas as pd

from Tool.functions.read.get_something import get_ins, get_para, get_fin_id, get_market_id, get_ipo
from Tool.functions.read.read_data_for_light_val import read_df


def get_data_for_financial(VID):
    bal_list, indus = get_fin_id(VID)
    bal_df = read_df("rdt_fintech", "NewBal", bal_list)
    # if flow_list:
    #     flow_df = read_df("rdt_fintech", "Flow", flow_list)
    indus_code, code_list = get_ins(indus)
    pre_1year_asset, pre_2year_asset, pre_3year_asset, liability, sc, financial_year, intangibleasset, minority_interest, lt_equity_investment2 = get_bal_data(
        bal_list, bal_df)
    [pc_A, pc_3, pc_pbp] = get_para(VID)[:3]
    pc = {'pc_A': pc_A, 'pc_3': pc_3, 'pc_pbp': pc_pbp}
    market = get_market_id(VID)
    ipo = get_ipo(VID)

    return [indus_code, pre_1year_asset, pre_2year_asset, pre_3year_asset, liability, sc, pc, financial_year,
            intangibleasset, minority_interest, lt_equity_investment2, code_list, market, ipo]


def get_bal_data(bal_list, bal_df):
    # bal_dict = {}
    # for i in bal_list:
    #     bal_dict[i] = {}
    demo = bal_df[bal_df["_id"] == bal_list[0]]
    pre_1year_asset = demo["f0s"].values[0]
    pre_2year_asset = pre_1year_asset / 1.5
    pre_3year_asset = pre_2year_asset / 1.8
    liability = demo["f1s"].values[0]
    sc = demo["f2001"].values[0]
    intangibleasset = demo["f0121"].values[0]
    minority_interest = demo["f2101"].values[0]
    lt_equity_investment2 = demo["f0106"].values[0]
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
    return pre_1year_asset, pre_2year_asset, pre_3year_asset, liability, sc, financial_year, intangibleasset, minority_interest, lt_equity_investment2
