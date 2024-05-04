# -*- coding: utf-8 -*-：
# 判断结果是否有效
# 选取最佳算法
# 算出综合结果
from Tool.functions.for_summary.getScaleandSelect import getScaleandSelect
from Tool.functions.new_summary.get_summary_result import get_summary


def summary(abs_result,market_result,samuelson_result,SC):
    [scal, show_in_page] = getScaleandSelect(abs_result,market_result,samuelson_result)
    # result = [abs_result,market_result,samuelson_result]
    summary_result, proportion = get_summary(scal, SC)

    return [summary_result,show_in_page, proportion, scal]
