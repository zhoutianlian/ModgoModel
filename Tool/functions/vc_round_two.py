# -*- coding: utf-8 -*-：
##ZXW
#############模拟分配金额计划 ########最多只能有两个非零整数
import numpy as np
from math import ceil, log10
def get_Amount_plan(remain_round):

    amount_plan=[]

    for e in range(remain_round):
        if e !=remain_round-1:
            temp_amount=round((1.5**e)/(2*(1.5**remain_round-1)),2)
            amount_plan.append(temp_amount)
        else:
            temp_amount=round(1-sum(amount_plan),2)
            amount_plan.append(temp_amount)



    return amount_plan

def round2(value):

    # try:
    #     if value<0:
    #         value = str(int(value))
    #         ans = int(value[1:3])
    #         for e in range(len(value) - 3):
    #             ans *= 10
    #         ans=-ans
    #
    #     else:
    #         value = str(int(value))
    #         ans = int(value[:2])
    #         for e in range(len(value) - 2):
    #             ans *= 10
    # except:
    #     print('!')
    #     ans = 0
    # return ans
    try:
        digit = ceil(log10(abs(value)))
        round_value = round(value, 2 - digit)
    except:
        round_value = 0
    return round_value

