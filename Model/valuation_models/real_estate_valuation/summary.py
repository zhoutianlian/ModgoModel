# -*- coding: utf-8 -*-：
##ZXW
# 判断结果是否有效
# 选取最佳算法
# 算出综合结果
from valuation_models.real_estate_valuation.for_summary.getScaleandSelect import getScaleandSelect
from valuation_models.real_estate_valuation.for_summary.summary_model import summary_model


def summary(real_estate_res,a_res,b_res,SC):

    [scal, show_in_page]=getScaleandSelect(real_estate_res,a_res,b_res)
    result=[real_estate_res,a_res,b_res]
    summary_result=summary_model(result,scal,show_in_page,SC)

    return [summary_result,show_in_page]









