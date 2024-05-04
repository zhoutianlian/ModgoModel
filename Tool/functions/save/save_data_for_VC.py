# -*- coding: utf-8 -*-：
import datetime
import random
import numpy as np

from Config.mongodb import save_mongo_from_dict
from Report.Log import logger
from Tool.functions.adjust_accuracy import adjust_accuracy_vc


def save_VC_result(VID, ans_normal, ans_samuelson, SS_R, listtime_ans, gpscore, listtime_h5, flag, ipo):
    VID = int(VID)
    modify_time = datetime.datetime.now()
    proportion = [0.5, 0.5]
    beat = random.randint(70, 95)
    str_ans = {}
    for key in ['avg', 'max', 'min']:
        str_ans[key] = str(SS_R[key])[1:-1]
        str_ans[key] = str_ans[key].replace('], ', '];')
    score = 10
    for i in range(len(listtime_h5)):
        if type(listtime_h5[i]) is np.float64 or type(listtime_h5[i]) is np.int64 or type(listtime_h5[i]) is np.int32:
            listtime_h5[i] = listtime_h5[i].item()
    for i in range(len(listtime_ans)):
        if type(listtime_ans[i]) is np.float64 or type(listtime_ans[i]) is np.int64 or type(
                listtime_ans[i]) is np.int32:
            listtime_ans[i] = listtime_ans[i].item()
    ipo = 1 if ipo else 0
    result = {"_id": VID, "time": modify_time,
              "ipo_prospect": {"IpoMarket": {listtime_ans[0]: listtime_ans[1]},
                               "IpoList": listtime_h5, "GPScore": gpscore, "LeadingPeers": beat, "ipo": ipo},
              "val": {"syn": [SS_R["MV_min"], SS_R["MV_avg"], SS_R["MV_max"]],
                      "syn_list": [str_ans["min"], str_ans["avg"], str_ans["max"]],
                      "score": SS_R["score"],
                      "detail": {"700000": {
                          "syn": [ans_normal["MV_min"], ans_normal["MV_avg"], ans_normal["MV_max"]],
                          "score": score, "wt": proportion[0]},
                          "400000": {
                              "syn": [ans_samuelson["MV_min"], ans_samuelson["MV_avg"], ans_samuelson["MV_max"]],
                              "score": score, "wt": proportion[1]}
                      }}}
    save_vc_to_mongo(result)
    adjust_accuracy_vc(VID)


def save_vc_to_mongo(result):
    # valuation_res = dict(ans_normal, **ans_samuelson)
    # valuation_res["vid"] = VID
    try:
        save_mongo_from_dict("rdt_fintech", "ValuationResult", result)
        # save_mongo_from_dict("rdt_fintech", "valuation_result", valuation_res)
    except Exception as e:
        logger(2, e)


def get_score(SS_R, ta, l):
    score = SS_R["MV_avg"] / (ta - l)
    if 2 <= score <= 10:
        SS_R["score"] = 10
    else:
        SS_R["score"] = 5
    return SS_R
