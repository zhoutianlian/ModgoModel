# -*- coding: utf-8 -*-：
##ZXW
# 选出收入法得出结果中，评分最好的前n个方法的名称【name1,name2,name3...】
# 检查收入法中所有结果的合法性

from Tool.functions.is_result_legal import result_legal


def select_the_best_abs(num, abs_result):
    ans=[]
    for e in range(num):
        score=0

        for key,value in abs_result.items():
            for key1,value1 in value.items():
                if value1=={} or value1['score']==0 or result_legal(key+key1,value1)==False:
                    continue
                if [key,key1] not in ans:
                    if score<value1['score']:
                        score=value1['score']
                        select=[key,key1,score]
                        ans.append(select)

    return ans