# -*- coding: utf-8 -*-：
import datetime
import random

from Config.mongodb import save_mongo_from_dict
from Tool.functions.adjust_accuracy import adjust_accuracy
from Report.Log import logger


def save_data(VID,abs_R,market_R,samuelson_result,SS_R,wacc,a,para,FFR,market_para,listtime_ans,gpscore,
              listtime_h5,proportion,scal, peer_list,para_from_apv, multiplier):
    VID = int(VID)
    Modify_time = datetime.datetime.now()
    beat = random.randint(70, 95)
    result = {"_id": VID, "time": Modify_time,
              "ipo_prospect": {"IpoMarket": {listtime_ans[0]: listtime_ans[1]},
                               "IpoList": listtime_h5, "GPScore": gpscore, "LeadingPeers": beat},
              "val": {"syn": [SS_R["MV_min"], SS_R["MV_avg"], SS_R["MV_max"]],
                      "peer_value": [SS_R["p_min"], SS_R["p_avg"], SS_R["p_max"]],
                      "score": SS_R["score"],
                      "detail": {"100000": {"syn": [scal["min_abs"], scal["avg_abs"], scal["max_abs"]],
                                            "score": scal["score_abs"], "wt": proportion[0]},
                                 "200000": {"syn": [scal["min_mkt"], scal["avg_mkt"], scal["max_mkt"]],
                                            "score": scal["score_mkt"], "wt": proportion[1]},
                                 "400000": {"syn": [scal["min_sam"], scal["avg_sam"], scal["max_sam"]],
                                            "score": scal["score_sam"], "wt": proportion[2]}}}}

    save_to_mongo(VID, result, abs_R,market_R,samuelson_result, FFR, wacc, a, para, market_para, peer_list, para_from_apv, multiplier)
    adjust_accuracy(VID)
    return VID


def save_to_mongo(VID, result, abs_R,market_R,samuelson_result, FFR, wacc, a, para, market_para, peer_list, para_from_apv, multiplier):
    abs_R = change_result(abs_R)
    market_R = adjust_market(market_R, peer_list)
    para_name = ["pc_A","pc_3","pc_pbp","pc_pep","pc_evsp","exitY","bestY","exitYpc","TVpc","perpetuity_g_basic","perpetuity_eva_pc",
     "perpetuity_ri_pc","M_pc","perpetuity_g_pc","perpetuity_ed_pc"]
    market_para_name = ["range_std","MVIC_NOPAT","std_MVIC_NOPAT","m_MVIC_NOPAT"]
    para_dict = {}
    market_para_dict = {}
    for i in range(len(para)):
        para_dict[para_name[i]] = para[i]
    for i in range(len(market_para)):
        market_para_dict[market_para_name[i]] = market_para[i]
    pre_para = dict(wacc,  **a, **para_dict, **market_para_dict, **para_from_apv, **multiplier)
    valuation_res = dict(abs_R, **market_R, **samuelson_result)
    valuation_res["vid"] = VID
    pre_para["vid"] = VID
    FFR["vid"] = VID

    try:
        save_mongo_from_dict("rdt_fintech", "ValuationResult", result)
        save_mongo_from_dict("rdt_fintech", "valuation_result", valuation_res)
        save_mongo_from_dict("rdt_fintech", "para", pre_para)
        save_mongo_from_dict("rdt_fintech", "FFR", FFR)
    except Exception as e:
        logger(2, e)


def adjust_market(market_R, peer_list):
    demo = {}
    for key, value in market_R.items():
        name_list = ["idx_avg", "idx_max", "idx_min", "MV_avg", "MV_max", "MV_min", "score"]
        demo_list = get_list(value, name_list)
        demo[key] = demo_list
    demo["stock_code"] = peer_list
    return demo


def change_result(data):
    demo ={}
    model_list = ["exitm", "fix_gr", "value_drive", "near_zero"]
    for key, value in data.items():
        demo[key] = {}
        value_list = get_list(value, model_list)
        name_list = ["exit_value", "e_MV_b", "e_MV_a", "e_MV_c", "MV_avg", "MV_max", "MV_min", "score"]
        for i in range(len(value_list)):
            demo_list = get_list(value_list[i], name_list)
            value_list[i] = demo_list
        demo[key] = value_list

    return demo


def get_list(demo, name_list):
    demo_list = []
    for i in range(len(name_list)):
        try:
            demo_list.append(demo[name_list[i]])
        except:
            demo_list.append(None)
    return demo_list








