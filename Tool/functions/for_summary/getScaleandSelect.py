# -*- coding: utf-8 -*-：
import numpy as np

from Tool.functions.for_summary.sub.select_best_n_marketR import select_the_best_market
from Tool.functions.for_summary.sub.select_best_n_absR import select_the_best_abs
from Config.global_V import GlobalValue

# 给出在页面显示的结果名称 show_in_page,只是用选中的方法进行综合
# 给出各个方法中最小的差值 min_dif
# 给出收入，市场，sam各个最大值，最小值


def getScaleandSelect(abs_result, market_result, samuelson_result):
    min_abs = 0
    max_abs = 0
    avg_abs = 0
    score_abs = 0
    avg_mkt = 0
    min_mkt = 0
    max_mkt = 0
    score_mkt = 0
    avg_sam = 0
    min_sam = 0
    max_sam = 0
    score_sam = 0
    min_dif = 0

    show_in_page = []

    # remain=3

    # 得到被选择的abs方法名 及其 最大值最小值，min_dif参与
    if abs_result!={}:

        select_abs=select_the_best_abs(1,abs_result)
        if select_abs!=[]:
            min_abs=abs_result[select_abs[-1][0]][select_abs[-1][1]]['MV_min']
            max_abs = abs_result[select_abs[-1][0]][select_abs[-1][1]]['MV_max']
            avg_abs = abs_result[select_abs[-1][0]][select_abs[-1][1]]['MV_avg']
            try:
                score_abs = abs_result[select_abs[-1][0]][select_abs[-1][1]]['score']
            except:
                pass
            min_dif = max_abs-min_abs
            show_in_page.append(select_abs[-1])
            # remain-=1
        else:
            show_in_page.append(False)

    else:
        show_in_page.append(False)

    # 得到被选择的mkt方法名 及其 最大值最小值，min_dif参与
    if market_result!= {}:
        select_market = select_the_best_market(1, market_result)
        if select_market != []:
            min_mkt = market_result[select_market[0]]['MV_min']
            max_mkt = market_result[select_market[0]]['MV_max']
            avg_mkt = market_result[select_market[0]]['MV_avg']
            try:
                score_mkt = market_result[select_market[0]]['score']
            except:
                pass
            if min_dif==0 or max_mkt-min_mkt <min_dif:
                min_dif = max_mkt - min_mkt
            show_in_page.append(select_market[0])

            # remain -= 1
        else:
            show_in_page.append(False)

    else:
        show_in_page.append(False)

    # 得到sam最大值，最小值，min_dif 参与
    if samuelson_result!={}:
        for key,value in samuelson_result.items():
            if value!=False:
                max_sam = value['MV_max']
                min_sam = value['MV_min']
                avg_sam = value['MV_avg']
                score_sam= 0
                # remain -= 1
                if min_dif == 0 or max_sam - min_sam < min_dif:
                    min_dif = max_sam - min_sam
                show_in_page.append(GlobalValue.SAM_NAME)
            else:
                show_in_page.append(False)
    else:
        show_in_page.append(False)

    scal={'max_abs':max_abs, 'min_abs':min_abs,"avg_abs":avg_abs,"score_abs":score_abs,'max_mkt':max_mkt,
          'min_mkt':min_mkt,"avg_mkt": avg_mkt,"score_mkt": score_mkt,'max_sam':max_sam,'min_sam':min_sam,
          "avg_sam":avg_sam,"score_sam": score_sam,'min_dif':min_dif}
    # 值相差过大,剔除过大值
    extrame_index = check_extrame_diff(scal)
    for e in extrame_index:
        show_in_page[e] = False
    for key in scal.keys():
        if type(scal[key]) == np.float64:
            scal[key] = scal[key].item()
    return [scal, show_in_page]


def check_extrame_diff(scal):
    ans_index = []
    count=-1
    for e in GlobalValue.METHODSUMMOD:
        count += 1
        if scal['max_' + e] == 0:
            ans_index.append(count)
            continue
        if (scal['max_' + e] - scal['min_' + e]) / scal['min_dif'] > 100:
            scal['max_' + e] = scal['min_' + e] = 0
            scal["avg_" + e] = 0
            ans_index.append(count)
            continue
    return ans_index
