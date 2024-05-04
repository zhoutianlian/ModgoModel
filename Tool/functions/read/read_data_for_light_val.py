# -*- coding: utf-8 -*-：
import pandas as pd

from Config.mongodb import Conn, read_mongo_limit
from Data.Conn import connect_mysql_rdt_fintech
from Report.Log import logger
from Tool.functions.read.get_something import get_ins, get_para, get_id, get_hypothesis


def get_data_for_simplemodel(VID):
    bal_list, flow_list, indus, hy_id, market, finance_round = get_id(VID)
    bal_df = read_df("rdt_fintech", "NewBal", bal_list)
    flow_df = read_df("rdt_fintech", "NewFlow", flow_list)
    # Dr = read_mongo_limit("rdt_fintech", "Hypo", {"_id": hy_id}, None)["kd"].values[0]
    Dr, AP, debt, Cash, Inv, AR, TA, L, SC, financialreport_year = get_bal_data(bal_list, bal_df)
    NI, EBIT, EBT, Rev = get_flow_data(flow_list, flow_df)
    # bal_dict = get_bal_data(bal_list, bal_df)
    indus_code, code_list=get_ins(indus)
    [pc_A,pc_3,pc_pbp,pc_pep,pc_evsp,exitY,bestY,exitYpc,TVpc,perpetuity_g_basic,perpetuity_eva_pc,
     perpetuity_ri_pc,M_pc,perpetuity_g_pc,perpetuity_ed_pc]=get_para(VID)
    CS, riskfree_rate = get_hypothesis(indus_code)
    [Rev_adjustment, flag] = get_rev_adj(VID)

    return [Dr,AP,debt,Cash,Inv,AR,TA,L,SC,NI,EBIT,EBT,Rev,indus_code,pc_A,pc_3,pc_pbp,pc_pep,pc_evsp,exitY,bestY,
            exitYpc,TVpc,perpetuity_g_basic,perpetuity_eva_pc,perpetuity_ri_pc,M_pc,perpetuity_g_pc,perpetuity_ed_pc,
            CS,financialreport_year,riskfree_rate,code_list, Rev_adjustment, flag, market, finance_round]


def get_bal_data(bal_list, bal_df):
    # bal_dict = {}
    # for i in bal_list:
    #     bal_dict[i] = {}
    demo = bal_df[bal_df["_id"] == bal_list[0]]
    Dr = demo["e9900"].values[0]
    Ap = demo["e1022"].values[0]
    debt = demo["e1001"].values[0]
    Cash = demo["e0001"].values[0]
    Inv = demo["e0031"].values[0]
    AR = demo["e0022"].values[0]
    TA = demo["e0s"].values[0]
    L = demo["e1s"].values[0]
    SC = demo["e2001"].values[0]
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
    financialreport_year = str(financialreport_year)[:4]
    return Dr, Ap, debt, Cash, Inv, AR, TA, L, SC, financialreport_year


def get_flow_data(flow_list, flow_df):
    # bal_dict = {}
    # for i in bal_list:
    #     bal_dict[i] = {}
    demo = flow_df[flow_df["_id"] == flow_list[0]]
    NI = demo["e35s1"].values[0]
    EBIT = demo["e33s1"].values[0]
    EBT = demo["e34s1"].values[0]
    rev = demo["e3101"].values[0]
    REV = [rev/1.8, rev/1.5, rev]
    #     bal_dict[i]["NI"] = demo["e35s1"]
    #     bal_dict[i]["EBIT"] = demo["e33s1"]
    #     bal_dict[i]["EBT"] = demo["e34s1"]
    #     bal_dict[i]["REV"] = [demo["e3101"], demo["e8011"], demo["e8012"]]
    return NI, EBIT, EBT, REV


def get_rev_adj(VID):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    sql_rev_ad = 'select operatingrevenue1,operatingrevenue2,operatingrevenue3,adjustment from company_operatingrevenue_modification where valuation_id=%s '
    rev_ad = []
    try:
        cursor.execute(sql_rev_ad,[VID])
        rev_ad = list(cursor.fetchall())
        cursor.close()
        db.close()
    except Exception as e:
        logger(2, e)
        cursor.close()
        db.close()
    if rev_ad!=[]:
        ans=rev_ad[-1][:-1]
        flag=rev_ad[-1][-1]
        return [ans,flag]
    else:
        return [[],0]


def read_df(db, collection, id_list):
    conn = Conn(db)
    db = conn[db]
    collection = db[collection]
    cursor = collection.find({"_id": {"$in": id_list}}).batch_size(5000)
    temp_list = []
    # i = 0
    for single_item in cursor:
        temp_list.append(single_item)
    # print(cursor.next())
    df = pd.DataFrame(temp_list)
    conn.close()

    return df




