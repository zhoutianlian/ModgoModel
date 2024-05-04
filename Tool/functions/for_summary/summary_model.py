# -*- coding: utf-8 -*-：
##ZXW
# 合并选择出的结果
# results:[收入，市场，期权]
import copy
import math
import numpy as np

from functions.distribution import for_distribution
from functions.for_summary.sub.decide_proportion import get_proportion
from functions.is_result_legal import result_legal
from log.log import logger


def summary_model(results,scal,show_in_page,SC):


    total_step=25

    the_min=max([scal['min_mkt'],scal['min_abs'],scal['min_sam']])
    for e in [scal['min_mkt'],scal['min_abs'],scal['min_sam']]:
        if e!=0 and e<the_min:
            the_min=e
    the_max=max([scal['max_mkt'],scal['max_abs'],scal['max_sam']])
    while True:
        step=(the_max-the_min)/total_step
        if (step*3) > scal['min_dif'] :
            total_step*=2
        else:
            break

    ###########得到参与计算综合估值结果的柱子长度
    selected_high=[]
    score=None

    for e in range(len(show_in_page)):
        if show_in_page[e]!=False:
            #锁定result值
            if e==0:
                temp=results[e][show_in_page[e][0]][show_in_page[e][1]]

            else:
                temp=results[e][show_in_page[e]]

            num = (temp['MV_max'] - temp['MV_min']) / step

            selected_high.append([temp['MV_min'],temp['MV_max'],for_distribution(num, temp['MV_max'], temp['MV_min'],
                                                                            temp['MV_avg'])])
        else:
            selected_high.append([])



    # 确定选中方法的比例
    proportion, proportion_temporary=get_proportion(selected_high)

    mark=[]
    ans_high=[]
    for index in range(total_step):
        block_bottom=the_min+index*step
        block_up=block_bottom+step

        index_for_selected_hight=index_for_mark=0
        while index_for_selected_hight<len(selected_high):
            if selected_high[index_for_selected_hight]==[]:
                pass
            else:
                if len(mark)<3:
                    mark.append(0)
                current_min=selected_high[index_for_selected_hight][0]
                current_max=selected_high[index_for_selected_hight][1]
                current_distri=selected_high[index_for_selected_hight][2]
                while mark[index_for_mark]<len(current_distri) and current_max>block_bottom and current_min<=block_bottom:
                    current=current_min+mark[index_for_mark]*step
                    if current>block_up:
                        break
                    else:
                        if len(ans_high)<index+1:
                            ans_high.append(current_distri[mark[index_for_mark]]*proportion[index_for_mark])
                        elif len(ans_high)==index+1:
                            ans_high[index] += current_distri[mark[index_for_mark]]*proportion[index_for_mark]
                        else:
                            logger('error in summary,mark3')
                        mark[index_for_mark]+=1

                index_for_mark+=1
            index_for_selected_hight+=1
        if len(ans_high) < index + 1:
            ans_high.append(0)

    ans_avg = 0
    ans_max = 0
    ans_min = 0
    target = max(ans_high)
    percent = 0.5
    for count in range(total_step):
        if ans_high[count] == target:
            ans_avg = the_min + step * count
            #######最小值
            start = copy.deepcopy(count)
            while start - 1 >= 0:
                if ans_high[start] < target * percent:
                    ans_min = the_min + step * start
                    break
                start -= 1
            if ans_min == 0:
                ans_min = the_min
            if ans_min==ans_avg:
                ans_min=ans_avg*0.95
            #########最大值
            start2 = copy.deepcopy(count)
            while start2 + 1 < total_step:
                if ans_high[start2] < target * percent:
                    ans_max = the_min + step * start2
                    break
                start2 += 1
            if ans_max == 0:
                ans_max = the_max
    score_abs = math.pow(scal["score_abs"], 2)
    score_mkt = math.pow(scal["score_mkt"], 2)
    score_sam = math.pow(scal["score_sam"], 2)
    score_avg = np.mean([score_abs, score_mkt, score_sam])
    score = math.sqrt(score_avg)
    summary_result = {'MV_max': ans_max, 'MV_min': ans_min, 'MV_avg': ans_avg, 'p_max': (ans_max / SC),
                      'p_min': (ans_min / SC), 'p_avg': (ans_avg / SC), "score": score}

    if result_legal('Summary_normal',summary_result)==False:
        summary_result = {'MV_max': 0, 'MV_min': 0, 'MV_avg': 0, 'p_max': 0,
                      'p_min': 0, 'p_avg': 0}

    return summary_result, proportion_temporary

