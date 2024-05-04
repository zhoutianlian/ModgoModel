import math
import numpy as np


def get_summary(vr_result, SC):
    vals = []
    abs_r = [vr_result["min_abs"], vr_result["avg_abs"], vr_result["max_abs"]]
    mkt_r = [vr_result["min_mkt"], vr_result["avg_mkt"], vr_result["max_mkt"]]
    sam_r = [vr_result["min_sam"], vr_result["avg_sam"], vr_result["max_sam"]]
    for i in [abs_r, mkt_r, sam_r]:
        flag = 0
        for demo in i:
            if demo == 0 or math.isnan(demo):
                flag = 1
                break
        if flag == 0:
            vals.append(i)        
    bad = []
    base = []
    good = []
    
    for approach in vals:
        bad.append(approach[0])
        base.append(approach[1])
        good.append(approach[2])
    
    result = []
    steps = 0
    wts = []
    for case in [bad, base, good]:
        floor = min(case)
        ceil = max(case)
        while True:
            steps += 1
            eq = floor * 0.5 + ceil * 0.5
            upper = 0
            lower = 0
            for each in case:
                upper += each / (2 * pow(eq, 2) - 2 * eq * each + pow(each, 2))
                lower += 1 / (2 * pow(eq, 2) - 2 * eq * each + pow(each, 2))
            cal = upper / lower
            # print('eq', round(eq, 2), 'cal', round(cal, 2))
            if abs(eq - cal) <= 0.001:
                result.append(round(eq, 2))
                # print('finish in', steps, 'times!')
                steps = 0
                wt = []
                sum_wt = 0
                for each in case:
                    # upper += each / (2 * pow(eq, 2) - 2 * eq * each + pow(each, 2))
                    sum_wt += 1 / (2 * pow(eq, 2) - 2 * eq * each + pow(each, 2))
                    wt.append(1 / (2 * pow(eq, 2) - 2 * eq * each + pow(each, 2)))
                for i in range(len(wt)):
                    wt[i] /= sum_wt
                wts.append(wt)
                break
            elif eq > cal:
                ceil = eq
            elif eq < cal:
                floor = eq

    mv_min = min(result)
    mv_max = max(result)
    for i in result:
        if i != mv_min and i != mv_max:
            mv_avg = i
            break

    proportion_list = []
    proportion = []
    flag = 0
    for i in wts:
        for index in range(len(i)):
            if flag == 0:
                proportion_list.append([])
            proportion_list[index].append(i[index])
        flag += 1
    for demo in proportion_list:
        proportion.append(round(np.mean(demo), 2).item())
    # 兜底
    proportion[-1] = proportion[-1]+(1-sum(proportion))
    proportion = get_proportion(abs_r, mkt_r, sam_r, proportion)

    score_abs = math.pow(vr_result["score_abs"], 2)
    score_mkt = math.pow(vr_result["score_mkt"], 2)
    score_sam = math.pow(vr_result["score_sam"], 2)
    score_avg = np.mean([score_abs, score_mkt, score_sam])
    score = math.sqrt(score_avg)
    summary_result = {"MV_min": mv_min, "MV_avg": mv_avg, "MV_max": mv_max, "p_min": mv_min/SC,
                      "p_avg": mv_avg/SC, "p_max": mv_max/SC, "score": score}
    # sum_r = [summary_result["MV_min"], summary_result["MV_avg"], summary_result["MV_max"]]
    # df = pd.DataFrame([abs_r, mkt_r, sam_r, sum_r], )

    return summary_result, proportion


def get_proportion(abs_r, mkt_r, sam_r, proportion):
    proportion_list = [0, 0, 0]
    length = len(proportion)
    if length == 1:
        if abs_r[0] == 0:
            if mkt_r[0] == 0:
                proportion_list[2] = proportion[0]
            else:
                proportion_list[1] = proportion[0]
        else:
            proportion_list[0] = proportion[0]
    elif length == 2:
        if abs_r[0] == 0:
            proportion_list[1] = proportion[0]
            proportion_list[2] = proportion[1]
        elif mkt_r[0] == 0:
            proportion_list[0] = proportion[0]
            proportion_list[2] = proportion[1]
        else:
            proportion_list[0] = proportion[0]
            proportion_list[1] = proportion[1]
    else:
        proportion_list[0] = proportion[0]
        proportion_list[1] = proportion[1]
        proportion_list[2] = proportion[2]
    return proportion_list
