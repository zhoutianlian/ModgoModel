import datetime
import random
import numpy as np

from Config.mongodb import save_mongo_from_dict
from Report.Log import logger
from Tool.functions.adjust_accuracy import adjust_accuracy_fin


def save_financial_valuation_result(VID,re,financial_ass_res,financial_samuelson_res,financial_mkt_res,SS_R,wacc,
                                    listtime_ans,gpscore,listtime_h5,proportion,scal,multiplier, ipo):
    VID = int(VID)
    Modify_time = datetime.datetime.now()
    beat = random.randint(70, 95)
    for i in range(len(listtime_h5)):
        if type(listtime_h5[i]) is np.float64 or type(listtime_h5[i]) is np.int64 or type(listtime_h5[i]) is np.int32:
            listtime_h5[i] = listtime_h5[i].item()
    for i in range(len(listtime_ans)):
        if type(listtime_ans[i]) is np.float64 or type(listtime_ans[i]) is np.int64 or type(listtime_ans[i]) is np.int32:
            listtime_ans[i] = listtime_ans[i].item()
    ipo = 1 if ipo else 0
    result = {"_id": VID, "time": Modify_time,
              "ipo_prospect": {"IpoMarket": {listtime_ans[0]: listtime_ans[1]},
                               "IpoList": listtime_h5, "GPScore": gpscore, "LeadingPeers": beat, "ipo": ipo},
              "val": {"syn": [SS_R["MV_min"], SS_R["MV_avg"], SS_R["MV_max"]],
                      "peer_value": [SS_R["p_min"], SS_R["p_avg"], SS_R["p_max"]],
                      "score": SS_R["score"],
                      "detail": {"300000": {"syn": [scal["min_ass"], scal["avg_ass"], scal["max_ass"]],
                                            "score": scal["score_ass"], "wt": proportion[0]},
                                 "200000": {"syn": [scal["min_mkt"], scal["avg_mkt"], scal["max_mkt"]],
                                            "score": scal["score_mkt"], "wt": proportion[1]},
                                 "400000": {"syn": [scal["min_sam"], scal["avg_sam"], scal["max_sam"]],
                                            "score": scal["score_sam"], "wt": proportion[2]}}}}

    save_fin_to_mongo(VID, result, financial_ass_res, financial_samuelson_res, financial_mkt_res, wacc, multiplier)
    adjust_accuracy_fin(VID)


def save_fin_to_mongo(VID, result, financial_ass_res, financial_samuelson_res, financial_mkt_res, wacc, multiplier):
    pre_para = dict(wacc, **multiplier)
    pre_para["vid"] = VID
    valuation_res = dict(financial_ass_res, **financial_samuelson_res, **financial_mkt_res)
    valuation_res["vid"] = VID
    try:
        save_mongo_from_dict("rdt_fintech", "ValuationResult", result)
        save_mongo_from_dict("rdt_fintech", "valuation_result", valuation_res)
        save_mongo_from_dict("rdt_fintech", "para", pre_para)
    except Exception as e:
        logger(2, e)



