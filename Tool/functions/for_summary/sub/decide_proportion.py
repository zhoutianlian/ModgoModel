# -*- coding: utf-8 -*-：
##ZXW
# 确定方法间的比例，如果缺失某种方法（以【】表示），则比较仅剩的方法
# 顺序 收入，市场，sam
# position list, 记录空比重出现的位置，取值范围 0,1,2
# 增加变量，proportion_temporary，满足使用要求
import numpy as np
def get_proportion(selected_hight):
    # 确定市场法和DCF法,sam分别的比例
    sensitive = 1
    avglen=[]
    base=0
    count=0
    for e in selected_hight:
        if e!=[]:

            temp=len(e[2])
            avglen.append(temp)
            base+=(1 / temp) ** sensitive
        else:
            avglen.append(0)

    proportion=[]
    proportion_temporary = []
    for e in avglen:
        if e == 0:
            proportion_temporary.append(0)
        else:
            p=(1 / e) ** sensitive / base
            proportion.append(p)
            proportion_temporary.append(p)
    proportion=[]
    for e in selected_hight:
        if e==[]:
            proportion.append(0)
        else:
            proportion.append(1)

    if proportion[1]==proportion[2]==0:
        proportion[0] = 1
    else:
        proportion[0] = 0.7
        if proportion[1]==proportion[2]==1:
            proportion[1]=0.2
            proportion[2]=0.1
        elif proportion[1]==1:
            proportion[1]=0.3
        else:
            proportion[2]=0.3

    proportion_=[]
    for e in proportion:
        if e!=0:
            proportion_.append(e)


    return proportion_,proportion



