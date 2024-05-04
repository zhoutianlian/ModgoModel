# -*- coding: utf-8 -*-：
# ZXW
import numpy as np
import pandas as pd
import datetime

from Config.mongodb import read_mongo_limit
from Tool.functions.indus_code_forA import retrack_Ainsudcode
from Tool.functions.read.read_data_for_light_val import read_df
from Tool.functions.semi_std import semi_std
from Tool.functions.read.get_something import get_ins, get_indus_turnover, get_indus_dtol, get_vc_id, get_hypothesis_re, \
    get_market_id, get_ipo
from Report.Log import logger


# finance_plan={'now_round':3,'Exit_year':4,'Amount':500000}       ###################融资计划：当前融资轮次，预计融资年限，预计仍需融资金额
# predict={'EY_WM':900000000000,'EY_MA':0.12,'EY_GRM':0.44,'EY_NIM':0.7,'EY_TaxR':0.2}   ######预计退出时的市场容量,市场占有率，毛利率水平，净利率水平，公司所得税税率
# Campany_Scal={'TA':78980980,'L':568566,'Contributed_Capital':123123,'Employee_number':234}
# Indus_code={'201010':1.0}


def get_data(VID):
    vc_id, indus, staff, fin_round = get_vc_id(VID)
    vc_list = [vc_id]
    vc_df = read_df("rdt_fintech", "NewVc", vc_list)
    [finance_plan, predict, company_scal, financialreport_year] = get_fs_data(vc_list, vc_df)
    company_scal["Employee_number"] = staff
    finance_plan['now_round'] = fin_round
    indus_code, code_list = get_ins(indus)
    [market_valueA, roe] = get_Indus_VM(indus_code)
    cs, re, riskfree_rate = get_hypothesis_re(indus_code)
    indus_turnover = get_indus_turnover(indus_code)
    indus_dtol = get_indus_dtol(indus_code)
    market = get_market_id(VID)
    ipo = get_ipo(VID)
    return [finance_plan, predict, company_scal, market_valueA, cs, roe, re, indus_dtol,
            indus_turnover, indus_code, financialreport_year, market, ipo]


def get_fs_data(vc_list, vc_df):
    demo = vc_df[vc_df["_id"] == vc_list[0]]
    prediction_liquidation_year = demo["v1001"].values[0]
    accumulation_finance_requirement = demo["v1101"].values[0]
    prediction_market_capacity_liquidation = demo["v2001"].values[0]
    prediction_market_share_liquidation = demo["v2101"].values[0]
    prediction_grossprofitmargin_liquidation = demo["v2201"].values[0]
    prediction_netprofitmargin_liquidation = demo["v2207"].values[0]
    prediction_incometax_rate_liquidation = demo["v2206"].values[0]
    current_totalasset = demo["v3001"].values[0]
    current_totalliabilities = demo["v3002"].values[0]
    current_paidincapital = demo["v3003"].values[0]
    #     bal_dict[i]["Dr"] = demo["e9900"]
    #     bal_dict[i]["Ap"] = demo["e9900"]
    #     bal_dict[i]["debt"] = demo["e1001"]
    #     bal_dict[i]["Cash"] = demo["e000101"]
    #        current_paidincapital = demo["v3003"].values[0] bal_dict[i]["Inv"] = demo["e0031"]
    #     bal_dict[i]["AR"] = demo["e0022"]
    #     bal_dict[i]["TA"] = demo["e0s"]
    #     bal_dict[i]["L"] = demo["e1s"]
    #     bal_dict[i]["SC"] = demo["e2001"]
    financialreport_year = demo["date"].values[0]
    financial_year = str(financialreport_year)[:4]
    finance_plan = {'Exit_year': prediction_liquidation_year, 'Amount': accumulation_finance_requirement}
    predict = {'EY_WM': prediction_market_capacity_liquidation, 'EY_MA': prediction_market_share_liquidation,
               'EY_GRM': prediction_grossprofitmargin_liquidation, 'EY_NIM': prediction_netprofitmargin_liquidation,
               'EY_TaxR': prediction_incometax_rate_liquidation}
    company_scal = {'TA': current_totalasset, 'L': current_totalliabilities,
                    'Contributed_Capital': current_paidincapital}
    return finance_plan, predict, company_scal, financial_year


def get_Indus_VM(indus_code):
    new_code = retrack_Ainsudcode("indus_gr_decision_tree", indus_code)
    market_value_A = {}
    market_value_3 = {}
    roe = []

    ##############################################A股市场行情_A############
    for key in new_code.keys():
        market_value_A[key] = {}

        ########日更数据
        mkt_A_df = read_mongo_limit("AM_hypothesis", "Mkt_A", {"GICS3_code": key}, {"_id": 0})
        name1 = ['PE', 'PS', 'EV_SALE', 'EV_EBIT']
        for e in name1:
            market_value_A[key][e] = mkt_A_df[e]
        ########季更数据
        mkt_AA_df = read_mongo_limit("AM_hypothesis", "Mkt_AA", {"GICS3_code": key}, {"_id": 0})
        name2 = ['NIM']
        for e in name2:
            market_value_A[key][e] = mkt_AA_df[e]
        # ########年更数据
        mkt_AAA_df = read_mongo_limit("AM_hypothesis", "Mkt_AAA", {"GICS3_code": key}, {"_id": 0})
        roe = mkt_AAA_df["ROE"]

    ##############################################三板股市场行情_3############
    # for key in indus_code.keys():
    #     market_value_3[key] = {}
    #     ########日更数据
    #     mkt_3_df = read_mongo_limit("AM_hypothesis", "Mkt_3", {"GICS3_code": int(key)}, {"_id": 0})
    #     name1 = ['PE', 'PS', 'EV_SALE', 'EV_EBIT']
    #     for e in name1:
    #         market_value_3[key][e] = mkt_3_df[e]
    #
    #     ########季更数据
    #
    #     ########年更数据
    #     mkt_333_df = read_mongo_limit("AM_hypothesis", "Mkt_333", {"GICS3_code": int(key)}, {"_id": 0})
    #     name3 = ['NIM']
    #     for e in name3:
    #         market_value_3[key][e] = mkt_333_df[e]

    ###############处理ROE
    ROE = []
    for e in roe:
        if float(e) > 0 or float(e) < 0:
            ROE.append(float(e))
    if ROE != []:
        roe = np.average(ROE)
        if roe < 0:
            roe = 0.12
    else:
        roe = 0.12

    name = ['PE', 'PS', 'EV_SALE', 'EV_EBIT']
    #############处理A股数据
    var_mulpA = {}
    for key in new_code.keys():
        var_mulpA[key] = {}
        var_mulpA[key]['percent'] = new_code[key]
        for ele in name:
            if not market_value_A[key][ele].empty:
                temp_data = []
                for count in range(len(market_value_A[key][ele])):
                    if float(market_value_A[key][ele][count]) > 0:
                        temp_data.append(float(market_value_A[key][ele][count]))
                if temp_data == []:
                    var_mulpA[key][ele] = False
                    logger(2, "ERRor in market_data _A " + ele)
                    break
                data1 = np.array(temp_data)
                mark1 = np.percentile(data1, 90)
                mark2 = np.percentile(data1, 10)
                data2 = []
                for e in data1:
                    if e > mark1 or e < mark2:
                        continue
                    else:
                        data2.append(e)
                if data2 != []:
                    [a, b] = semi_std(data2, np.average(data2))
                    var_mulpA[key][ele] = [np.average(data2), a, b]
                else:
                    var_mulpA[key][ele] = False
                    logger(2, "ERRor in market_data _A " + ele)
                    break
                # [a,b]=semi_std(temp_data,np.average(temp_data))
                # var_mulpA[key][ele]=[np.average(temp_data),a,b]
            else:
                var_mulpA[key][ele] = False
                logger(2, "ERRor in market_data _A " + ele)
                break

    #############处理3板数据
    # var_mulp3 = {}
    # for key in indus_code.keys():
    #     var_mulp3[key] = {}
    #     var_mulp3[key]['percent'] = indus_code[key]
    #     for ele in name:
    #         if not market_value_3[key][ele].empty:
    #             temp_data = []
    #             for count in range(len(market_value_3[key][ele])):
    #                 if float(market_value_3[key][ele][count]) > 0:
    #                     temp_data.append(float(market_value_3[key][ele][count]))
    #             if temp_data==[]:
    #                 var_mulp3[key][ele] = False
    #                 logger("ERRor in market_data _3 " + ele)
    #                 continue
    #
    #             data1 = np.array(temp_data)
    #             mark1 = np.percentile(data1, 90)
    #             mark2 = np.percentile(data1, 10)
    #             data2 = []
    #             for e in data1:
    #                 if e > mark1 or e < mark2:
    #                     continue
    #                 else:
    #                     data2.append(e)
    #             if len(data2)>2:
    #                 [a, b] = semi_std(data2, np.average(data2))
    #                 var_mulp3[key][ele] = [np.average(data2), a, b]
    #             else:
    #                 var_mulp3[key][ele] = False
    #                 logger("ERRor in market_data _3 " + ele)
    #                 continue
    #             # [a,b]=semi_std(temp_data,np.average(temp_data))
    #             # var_mulp3[key][ele]=[np.average(temp_data),a,b]
    #         else:
    #             var_mulp3[key][ele] = False
    #             logger("ERRor in market_data _3 " + ele)
    #             break

    return [var_mulpA, roe]

# get_Indus_VM({"451030": 1.0})
