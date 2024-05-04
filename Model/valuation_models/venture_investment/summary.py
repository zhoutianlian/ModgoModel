from Tool.functions.is_result_legal import result_legal_minus

def get_summary_result(normal_ans,sam_ans):
    total_fround=len(normal_ans['max'])
    summary_ans={}
    if sam_ans=={}:
        summary_ans=normal_ans
        # 转换ans的数据形式
        for key in ['max', 'min', 'avg']:
            a = 1
            while a < len(summary_ans[key]):
                summary_ans[key][a].extend(summary_ans[key][a + 1])
                summary_ans[key].remove(summary_ans[key][a + 1])
                a += 1
        return summary_ans

    if result_legal_minus('vi_sam',sam_ans) and result_legal_minus('vi_normal',normal_ans): #如果两个结果都有效
        if normal_ans['MV_max'] <= 0 or normal_ans['MV_avg'] <= 0 or normal_ans['MV_min'] <= 0:
            if sam_ans['MV_min'] > 0:
                # 使用sam作为最终结果
                summary_ans = sam_ans

            else:
                # --
                summary_ans['max'] = []
                summary_ans['min'] = []
                summary_ans['avg'] = []
                summary_ans['MV_max'] = (sam_ans['MV_max'] + normal_ans['MV_max']) / 2
                summary_ans['MV_min'] = (sam_ans['MV_min'] + normal_ans['MV_min']) / 2
                summary_ans['MV_avg'] = (sam_ans['MV_avg'] + normal_ans['MV_avg']) / 2
                for key in ['max', 'min', 'avg']:
                    if sam_ans[key][0][0] <= 0 and normal_ans[key][0][0] <= 0:
                        for fround in range(total_fround):
                            if fround % 2 == 1:
                                summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                         sam_ans[key][fround][1], 0])
                            else:
                                summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                         sam_ans[key][fround][1]])
                    else:
                        keepShare = 1
                        for fround in range(total_fround):
                            if fround % 2 == 1:
                                keepShare *= (sam_ans[key][fround - 1][0] + normal_ans[key][fround - 1][0]) / \
                                             (sam_ans[key][fround][0] + normal_ans[key][fround][0])
                                summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                         sam_ans[key][fround][1], round((1 - keepShare) * 100, 2)])
                            else:
                                summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                         sam_ans[key][fround][1]])



        else:
            if sam_ans['MV_min'] > 0:
                # ++
                summary_ans['max'] = []
                summary_ans['min'] = []
                summary_ans['avg'] = []
                summary_ans['MV_max'] = (sam_ans['MV_max'] + normal_ans['MV_max']) / 2
                summary_ans['MV_min'] = (sam_ans['MV_min'] + normal_ans['MV_min']) / 2
                summary_ans['MV_avg'] = (sam_ans['MV_avg'] + normal_ans['MV_avg']) / 2
                for key in ['max', 'min', 'avg']:
                    keepShare = 1
                    for fround in range(total_fround):
                        if fround % 2 == 1:
                            keepShare *= (sam_ans[key][fround - 1][0] + normal_ans[key][fround - 1][0]) / \
                                         (sam_ans[key][fround][0] + normal_ans[key][fround][0])
                            summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                     sam_ans[key][fround][1], round((1 - keepShare) * 100, 2)])
                        else:
                            summary_ans[key].append([(sam_ans[key][fround][0] + normal_ans[key][fround][0]) / 2,
                                                     sam_ans[key][fround][1]])
            else:
                summary_ans = normal_ans
    elif result_legal_minus('vi_sam',sam_ans):
        summary_ans=sam_ans
    elif result_legal_minus('vi_normal',normal_ans):
        summary_ans=normal_ans
    else:      #没有一个结果合法的时候，估值失败
        summary_ans=False


    if summary_ans!=False:
        # 转换ans的数据形式
        for key in ['max', 'min', 'avg']:
            a = 1
            while a < len(summary_ans[key]):
                summary_ans[key][a].extend(summary_ans[key][a + 1])
                summary_ans[key].remove(summary_ans[key][a + 1])
                a += 1


    return summary_ans
