# -*- coding: utf-8 -*-：
from Tool.functions.for_summary.sub.select_best_n_marketR import select_the_best_market
from Config.global_V import GlobalValue

# 给出在页面显示的结果名称 show_in_page,只是用选中的方法进行综合
# 给出各个方法中最小的差值 min_dif
# 给出收入，市场，sam各个最大值，最小值


def getScaleandSelect(asset_result, market_result, samuelson_result):
    min_ass = 0
    max_ass = 0
    avg_ass = 0
    min_mkt = 0
    max_mkt = 0
    avg_mkt = 0
    min_sam = 0
    max_sam = 0
    avg_sam = 0
    min_dif = 0
    score_ass = 0
    score_mkt = 0
    score_sam = 0
    show_in_page = []

    # remain=3
    # 得到sam最大值，最小值，min_dif 参与
    if asset_result != {}:
        for key, value in asset_result.items():
            if value != False:
                max_ass = value['MV_max']
                min_ass = value['MV_min']
                avg_ass = value["MV_avg"]
                try:
                    score_ass = value['score']
                except:
                    score_ass = 0
                # remain -= 1
                if min_dif == 0 or max_ass - min_ass < min_dif:
                    min_dif = max_ass - min_ass
                show_in_page.append(GlobalValue.ASS_NAME)
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
                score_mkt = 0
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
                try:
                    score_sam = value['score']
                except:
                    score_sam = 0
                # remain -= 1
                if min_dif == 0 or max_sam - min_sam < min_dif:
                    min_dif = max_sam - min_sam
                show_in_page.append(GlobalValue.SAM_NAME)
            else:
                show_in_page.append(False)
    else:
        show_in_page.append(False)

    scal={'max_ass': max_ass, 'min_ass': min_ass, "avg_ass": avg_ass, "score_ass": score_ass, 'max_mkt': max_mkt,
          'min_mkt': min_mkt, "score_mkt": score_mkt, 'avg_mkt': avg_mkt, 'max_sam': max_sam, 'min_sam': min_sam,
          "avg_sam": avg_sam, "score_sam": score_sam, 'min_dif': min_dif}
    # 值相差过大,剔除过大值
    extrame_index = check_extrame_diff(scal)
    for e in extrame_index:
        show_in_page[e] = False

    return [scal, show_in_page]


def check_extrame_diff(scal):
    ans_index = []
    count=-1
    for e in GlobalValue.METHODSUMMOD:
        count += 1
        try:
            if scal['max_' + e] == 0:
                ans_index.append(count)
                continue
            if (scal['max_' + e] - scal['min_' + e]) / scal['min_dif'] > 100:
                scal['max_' + e] = scal['min_' + e] = 0
                ans_index.append(count)
                continue
        except:
            continue
    return ans_index
