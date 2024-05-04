# -*- coding: utf-8 -*-：
# 判断结果是否有效
# 选取最佳算法
# 算出综合结果
# from numpy import average
from Model.valuation_models.financial_valuation.for_summary.getScaleandSelect import getScaleandSelect
from Model.valuation_models.financial_valuation.for_summary.summary_model import summary_model
# from math import pow, sqrt
# from numpy import mean
#
# from Algorithm.Average import weight_lite


def summary(fincial_asset_res, financial_mkt_res,financial_samuelson_res,SC):

    [scal, show_in_page]=getScaleandSelect(fincial_asset_res,financial_mkt_res,financial_samuelson_res)
    result=[fincial_asset_res,financial_mkt_res,financial_samuelson_res]
    summary_result, proportion=summary_model(result,scal,show_in_page,SC)
    # model_dict = dict()
    # model_dict["ass"] = [fincial_asset_res["MV_min"], fincial_asset_res["MV_avg"], fincial_asset_res["MV_max"]]
    # model_dict["mkt"] = [financial_mkt_res["MV_min"], financial_mkt_res["MV_avg"], financial_mkt_res["MV_max"]]
    # model_dict["sam"] = [financial_samuelson_res["MV_min"], financial_samuelson_res["MV_avg"],
    #                      financial_samuelson_res["MV_max"]]
    #
    # syn_val, syn_wt = weight_lite(model_dict)
    #
    # scal = {"min_ass": fincial_asset_res["MV_min"], "avg_ass": fincial_asset_res["MV_avg"],
    #         "max_ass": fincial_asset_res["MV_max"], "min_mkt": financial_mkt_res["MV_min"],
    #         "avg_mkt": financial_mkt_res["MV_min"], "max_mkt": financial_mkt_res["MV_min"],
    #         "score_ass": fincial_asset_res["score_ass"], "score_mkt": fincial_asset_res["score_mkt"],
    #         "min_sam": financial_samuelson_res["MV_min"], "avg_sam": financial_samuelson_res["MV_min"],
    #         "max_sam": financial_samuelson_res["MV_min"], "score_sam": fincial_asset_res["score_sam"]}
    # proportion = syn_wt
    # score_abs = pow(scal["score_ass"], 2)
    # score_mkt = pow(scal["score_mkt"], 2)
    # score_sam = pow(scal["score_sam"], 2)
    # score_avg = mean([score_abs, score_mkt, score_sam])
    # score = sqrt(score_avg)
    # summary_result = {"MV_min": syn_val[0], "MV_avg": syn_val[1], "MV_max": syn_val[2], 'p_max': syn_val[2] / SC,
    #                   'p_min': syn_val[0] / SC, 'p_avg': syn_val[1] / SC, "score": score}

    return summary_result, proportion, scal









