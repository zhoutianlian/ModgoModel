import datetime
import random
import numpy as np

from Config.mongodb import save_mongo_from_dict
from Report.Log import logger
from Tool.functions.adjust_accuracy import adjust_accuracy


def save_real_estate_valuation_result(VID, real_estate_res, SS_R, wacc,
                                      listtime_ans, gpscore, listtime_h5, flag, multiplier, ipo):
    VID = int(VID)
    est_result = {"real_estate_res": real_estate_res}
    Modify_time = datetime.datetime.now()
    proportion = [1]
    beat = random.randint(70, 95)
    for i in range(len(listtime_h5)):
        if type(listtime_h5[i]) is np.float64 or type(listtime_h5[i]) is np.int64 or type(listtime_h5[i]) is np.int32:
            listtime_h5[i] = listtime_h5[i].item()
    for i in range(len(listtime_ans)):
        if type(listtime_ans[i]) is np.float64 or type(listtime_ans[i]) is np.int64 or type(
                listtime_ans[i]) is np.int32:
            listtime_ans[i] = listtime_ans[i].item()
    ipo = 1 if ipo else 0
    result = {"_id": VID, "time": Modify_time,
              "ipo_prospect": {"IpoMarket": {listtime_ans[0]: listtime_ans[1]},
                               "IpoList": listtime_h5, "GPScore": gpscore, "LeadingPeers": beat, "ipo": ipo},
              "val": {"syn": [SS_R["MV_min"], SS_R["MV_avg"], SS_R["MV_max"]],
                      "peer_value": [SS_R["p_min"], SS_R["p_avg"], SS_R["p_max"]],
                      "score": SS_R["score"],
                      "detail": {"610001": {"syn": [real_estate_res["var_real_estate"]["MV_min"],
                                                    real_estate_res["var_real_estate"]["MV_avg"],
                                                    real_estate_res["var_real_estate"]["MV_max"]],
                                            "score": real_estate_res["var_real_estate"]["score"],
                                            "wt": proportion[0]}}}}

    save_real_to_mongo(VID, result, est_result, wacc, multiplier)
    adjust_accuracy(VID)


def save_real_to_mongo(VID, result, real_estate_res, wacc, multiplier):
    real_estate_res["vid"] = VID
    pre_para = dict(wacc, **multiplier)
    pre_para["vid"] = VID
    try:
        save_mongo_from_dict("rdt_fintech", "ValuationResult", result)
        save_mongo_from_dict("rdt_fintech", "valuation_result", real_estate_res)
        save_mongo_from_dict("rdt_fintech", "para", pre_para)
    except Exception as e:
        logger(2, e)
