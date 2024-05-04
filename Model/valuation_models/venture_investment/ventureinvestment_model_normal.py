# -*- coding: utf-8 -*-：
import numpy as np

from Tool.functions.vc_round_two import round2
from Report.Log import logger
##########
#结果：如果max。min。avg均有值，则正常输出，否则只返回退出年最终估值 及 为负年的值，flag 设为False 不管是否正常输出，一定会遍历max。min。avg三值
#########


class Normal_VI():
    def get_VC2(self, predict, finance_plan, var_mulpA, indus_DEratio, indus_re, amount_plan, MUTILPLIER,
                interval, remain_round):
        predict_Rev = predict['EY_WM'] * predict['EY_MA']
        predict_NI = predict_Rev * predict['EY_NIM']
        # predict_EBT=predict_NI/(1-predict['EY_TaxR'])

        suojian = [0.7, 0.85]
        ########处理行业值##################
        EndVal_EVtoS = 0
        EndVal_EVtoEBIT = 0
        EndVal_PE = 0
        EndVal_PS = 0

        EndVal_EVtoS_Max = 0
        EndVal_EVtoEBIT_Max = 0
        EndVal_PE_Max = 0
        EndVal_PS_Max = 0

        EndVal_EVtoS_Min = 0
        EndVal_EVtoEBIT_Min = 0
        EndVal_PE_Min = 0
        EndVal_PS_Min = 0
        AA_rate = 0.06  #####AA债权的利率
        count = 0
        if var_mulpA == False:
            logger(2, 'Error in Mkt Data')
            return
        flag = 0
        for var_mulp in [var_mulpA]:
            ##########用A股数据进行估值#########
            for key in var_mulp.keys():
                if var_mulp[key]['PE'] == False or var_mulp[key]['EV_SALE'] == False:
                    flag +=1
                    count += 1
                    continue
                indus_EV_S = var_mulp[key]['EV_SALE']
                # indus_EV_EBIT=var_mulp[key]['EV_EBIT']
                indus_PE = var_mulp[key]['PE']
                # indus_PS=var_mulp[key]['PS']
                percent = var_mulp[key]['percent']

                a = pow(sum([(indus_EV_S[1] / indus_EV_S[0]) ** 2, (indus_PE[1] / indus_PE[0]) ** 2]) / 2, 0.5)
                b = pow(sum([(indus_EV_S[2] / indus_EV_S[0]) ** 2, (indus_PE[2] / indus_PE[0]) ** 2]) / 2, 0.5)

                # predict_B=predict_NI/indus_ROE
                # predict_Debt=predict_B*indus_DEratio
                # predict_insExp=predict_Debt*AA_rate
                # predict_EBIT=predict_EBT+predict_insExp
                EtoEV = 1 / (1 + indus_DEratio)

                temp1 = predict_Rev * indus_EV_S[0] * EtoEV * percent * suojian[count]
                EndVal_EVtoS += temp1  # 用企业销售率计算
                # EndVal_EVtoEBIT += predict_EBIT * indus_EV_EBIT[0]*EtoEV* 0.5*percent*suojian[count] # 用EV/EBIT乘数计算
                temp2 = predict_NI * indus_PE[0] * percent * suojian[count]
                EndVal_PE += temp2  # 用市盈率计算
                # EndVal_PS += predict_Rev * indus_PS[0] * 0.5*percent*suojian[count]

                EndVal_EVtoS_Max += temp1 * (1 + a)  # 用企业销售率计算
                # EndVal_EVtoEBIT_Max += EndVal_EVtoEBIT * (1+a)  # 用EV/EBIT乘数计算
                EndVal_PE_Max += temp2 * (1 + a)  # 用市盈率计算
                # EndVal_PS_Max += EndVal_PS * (1+a)

                EndVal_EVtoS_Min += temp1 * (1 - b)  # 用企业销售率计算
                # EndVal_EVtoEBIT_Min += EndVal_EVtoEBIT * (1-b)  # 用EV/EBIT乘数计算
                EndVal_PE_Min += temp2 * (1 - b)  # 用市盈率计算
                # EndVal_PS_Min += EndVal_PS * (1-b)
            count += 1
        if flag == 0:

            EndVals = [EndVal_EVtoS * 0.5, EndVal_EVtoEBIT * 0.5, EndVal_PE * 0.5, EndVal_PS * 0.5]
            EndVals_Max = [EndVal_EVtoS_Max * 0.5, EndVal_EVtoEBIT_Max * 0.5, EndVal_PE_Max * 0.5, EndVal_PS_Max * 0.5]
            EndVals_Min = [EndVal_EVtoS_Min * 0.5, EndVal_EVtoEBIT_Min * 0.5, EndVal_PE_Min * 0.5, EndVal_PS_Min * 0.5]
        elif flag==1:
            EndVals = [EndVal_EVtoS, EndVal_EVtoEBIT, EndVal_PE, EndVal_PS]
            EndVals_Max = [EndVal_EVtoS_Max, EndVal_EVtoEBIT_Max, EndVal_PE_Max, EndVal_PS_Max]
            EndVals_Min = [EndVal_EVtoS_Min, EndVal_EVtoEBIT_Min, EndVal_PE_Min, EndVal_PS_Min]
        else:
            raise NotImplemented

        avg_val = np.average(EndVals)
        min_val = np.average(EndVals_Min)
        max_val = np.average(EndVals_Max)
        val_scap = {'avg': avg_val, 'min': min_val, 'max': max_val}

        ans = {}

        for key in val_scap.keys():
            ans[key] = []
            value = round2(val_scap[key])
            count = 1
            ans[key].append([value, finance_plan['Exit_year']])
            zero_flag = 0
            dShare = 1
            for round_c in range(1, remain_round + 1):
                finance_round = remain_round + finance_plan['now_round'] - round_c
                re = indus_re * MUTILPLIER[finance_round]
                post_amount = round2(value / pow((1 + re), interval))  ########融资后估值
                if post_amount <= 0:
                    ans[key].append([0, round(finance_plan['Exit_year'] - count * interval, 1), 0])
                    zero_flag = 1
                else:
                    ans[key].append([post_amount, round(finance_plan['Exit_year'] - count * interval, 1)])
                pre_amount = post_amount - amount_plan[-round_c] * finance_plan['Amount']  ##########融资前估值
                if pre_amount <= 0:
                    ans[key].append([0, round(finance_plan['Exit_year'] - count * interval, 1)])
                    zero_flag = 1
                else:
                    dShare *= pre_amount / post_amount  ##############稀释比例
                    ans[key].append([pre_amount, round(finance_plan['Exit_year'] - count * interval, 1)])
                value = pre_amount

                count += 1
            # 添加现值
            ans['MV_' + key] = pre_amount
            # 判断结果中是否没有负数
            if zero_flag == 1:
                count1 = 1
                while count1 < len(ans[key]):
                    ans[key][count1].append(0)
                    count1 += 2
            # 逆向加比例
            else:
                count1 = 1
                while count1 < len(ans[key]):
                    if len(ans[key][count1]) == 3:
                        break
                    ans[key][count1].append(round((1 - dShare) * 100, 2))
                    if ans[key][count1 + 1][0] == 0:
                        break
                    else:
                        dShare /= (ans[key][count1 + 1][0] / ans[key][count1][0])
                    count1 += 2

            # 逆转list
            ans[key] = list(reversed(ans[key]))

        return ans
