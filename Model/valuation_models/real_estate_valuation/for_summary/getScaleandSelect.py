# -*- coding: utf-8 -*-：
##ZXW

# 给出在页面显示的结果名称 show_in_page,只是用选中的方法进行综合
# 给出各个方法中最小的差值 min_dif
# 给出收入，市场，sam各个最大值，最小值

from functions.is_result_legal import result_legal
from functions.for_summary.sub.select_best_n_marketR import select_the_best_market
from CONFIG.global_V import GlobalValue
def getScaleandSelect(estate_result, a_result, b_result):
    min_est = 0
    max_est = 0
    min_a = 0
    max_a = 0
    min_b = 0
    max_b = 0
    min_dif = 0

    show_in_page = []

    # remain=3

    # 得到被选择的abs方法名 及其 最大值最小值，min_dif参与
    if estate_result!={}:
        for key,value in estate_result.items():
            if value!=False:
                max_est = value['MV_max']
                min_est = value['MV_min']
                # remain -= 1
                if min_dif == 0 or max_est - min_est < min_dif:
                    min_dif = max_est - min_est
                show_in_page.append(GlobalValue.REAL_NAME)
            else:
                show_in_page.append(False)
    else:
        show_in_page.append(False)


    # 得到被选择的mkt方法名 及其 最大值最小值，min_dif参与
    if a_result!= {}:
        select_market = select_the_best_market(1, a_result)
        if select_market != []:
            min_a = a_result[select_market[0]]['MV_min']
            max_a = a_result[select_market[0]]['MV_max']
            if min_dif==0 or max_a-min_a <min_dif:
                min_dif = max_a - min_a
            show_in_page.append(select_market[0])

            # remain -= 1
        else:
            show_in_page.append(False)

    else:
        show_in_page.append(False)




    # 得到sam最大值，最小值，min_dif 参与
    if b_result!={}:
        for key,value in b_result.items():
            if value!=False:
                max_b = value['MV_max']
                min_b = value['MV_min']
                # remain -= 1
                if min_dif == 0 or max_b - min_b < min_dif:
                    min_dif = max_b - min_b
                show_in_page.append(GlobalValue.SAM_NAME)
            else:
                show_in_page.append(False)
    else:
        show_in_page.append(False)



    scal={'max_est':max_est, 'min_est':min_est,'max_a':max_a, 'min_a':min_a,  'max_b':max_b,
          'min_b':min_b,'min_dif':min_dif}
    # 值相差过大,剔除过大值
    extrame_index = check_extrame_diff(scal)
    for e in extrame_index:
        show_in_page[e] = False

    return [scal, show_in_page]

def check_extrame_diff(scal):
    ans_index = []
    count=-1
    for e in GlobalValue.METHODREAL:
        count += 1
        if scal['max_' + e] == 0:
            ans_index.append(count)
            continue
        if  (scal['max_' + e] - scal['min_' + e]) / scal['min_dif'] > 100:
            scal['max_' + e]=scal['min_' + e]=0
            ans_index.append(count)
            continue
    return ans_index
