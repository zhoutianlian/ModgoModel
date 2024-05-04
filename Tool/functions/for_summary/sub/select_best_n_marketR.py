# -*- coding: utf-8 -*-：
# 选出市场法得出结果中，评分最好的前n个方法的名称【name1,name2,name3...】
# 检查市场法中所有结果的合法性
# 如果num大于最大有效结果，则尽可能返回值,如果没有值返回[]

from Tool.functions.is_result_legal import result_legal


def select_the_best_market(num, mkt_result):
    ans=[]
    for e in range(num):
        score=0
        count=0
        select=False
        for key,value in mkt_result.items():
            # if value=={} or value['score']==0 :
            if value == {} or value['score'] == 0 or result_legal('mkt_' + key, value) == False:
                count+=1
                continue
            if key not in ans:
                if score<value['score']:
                    score=value['score']
                    select=key
        if select!=False:
            ans.append(select)

        if len(ans)+count==len(mkt_result):
            break

    return ans
