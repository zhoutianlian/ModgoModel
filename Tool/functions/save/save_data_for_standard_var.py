# -*- coding: utf-8 -*-：
##ZXW

import datetime
import random

from Tool.functions.adjust_accuracy import adjust_accuracy
from Tool.functions.save.save_data_for_light_val import save_to_mongo


def save_data(VID,abs_R,market_R,samuelson_result,SS_R,wacc,a,para,FFR,flag,market_para,listtime_ans,gpscore,
              listtime_h5,proportion,scal, peer_list,para_from_apv, multiplier):
    Modify_time = datetime.datetime.now()
    adjust_accuracy(VID)
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

    save_to_mongo(VID, result, abs_R, market_R, samuelson_result, FFR, wacc, a, para, market_para, peer_list,
                  para_from_apv, multiplier)
    return VID




