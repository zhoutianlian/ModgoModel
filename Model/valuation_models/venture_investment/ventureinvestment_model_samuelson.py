# -*- coding: utf-8 -*-：
import math
import scipy.stats

from Tool.functions.vc_round_two import round2


##########
#结果：如果max。min。avg均有值，则正常输出，否则只返当前估值，flag 设为False 不管是否正常输出，一定会遍历max。min。avg三值
##########
class Samuelson_VI():
    def get_samuelson_results(self,predict, finance_plan, campany_scal, indus_DEratio, indus_dtol, indus_re, indus_turnover,
                              amount_plan, MUTILPLIER, interval, remain_round):
        SIGMA_COEFFICIENT = 3
        bondAA_rate = 0.068  ##### 连公司债数据库
        riskfree_rate = 0.035

        re = indus_re * MUTILPLIER[finance_plan['now_round']]
        predict_revenue = predict['EY_WM'] * predict['EY_MA']

        amount = [i * finance_plan['Amount'] for i in amount_plan]
        pv_amount = 0
        for e in range(len(amount)):
            pv_amount += amount[e] / (1 + re) ** (e * interval)

        ans = {}
        for key, indus_turnover_value in indus_turnover.items():
            exit_total_asset = predict_revenue / indus_turnover_value
            log_asset_gr = math.log(exit_total_asset / campany_scal['TA']) / finance_plan['Exit_year']
            sigma_asset = log_asset_gr * SIGMA_COEFFICIENT
            log_avg_debtcost = math.log(
                bondAA_rate * (1 - predict['EY_TaxR']) * indus_dtol + riskfree_rate * (1 - indus_dtol) + 1)
            log_wacc = math.log((indus_DEratio / (indus_DEratio + 1)) * bondAA_rate * (1 - predict['EY_TaxR']) + (
                    1 / (indus_DEratio + 1)) * re + 1)
            n_d1 = scipy.stats.norm(0, 1).cdf(
                (math.log(campany_scal['TA'] / campany_scal['L']) + (log_wacc + sigma_asset ** 2 / 2) *
                 finance_plan['Exit_year']) / (sigma_asset * finance_plan['Exit_year'] ** 0.5))
            n_d2 = scipy.stats.norm(0, 1).cdf(
                (math.log(campany_scal['TA'] / campany_scal['L']) + (log_avg_debtcost - sigma_asset ** 2 / 2) *
                 finance_plan['Exit_year']) / (sigma_asset * finance_plan['Exit_year'] ** 0.5))
            MV = campany_scal['TA'] * pow(math.e, (log_asset_gr - log_wacc) * finance_plan['Exit_year']) * n_d1 - \
                 campany_scal['L'] * pow(math.e, (log_asset_gr - log_avg_debtcost) * finance_plan['Exit_year']) * n_d2

            if key == 'max':
                key1 = 'min'
            elif key == 'min':
                key1 = 'max'
            else:
                key1 = 'avg'
            ans[key1] = []
            preamount = round2(MV - pv_amount)
            ans['MV_' + key1] = preamount
            dshare = 0
            keepShare = 1
            if preamount > 0:
                for round_c in range(remain_round):
                    ans[key1].append([preamount, round(interval * round_c, 2)])
                    postamount = round2(preamount + amount[round_c])
                    keepShare *= preamount / postamount
                    dshare = 1 - keepShare
                    ans[key1].append([postamount, round(interval * round_c, 2), round(dshare * 100, 2)])

                    preamount = round2(postamount * pow(1 + re, interval))

            else:
                for round_c in range(remain_round):
                    if preamount > 0:
                        ans[key1].append([preamount, round(interval * round_c, 2)])
                    else:
                        ans[key1].append([0, round(interval * round_c, 2)])
                    postamount = round2(preamount + amount[round_c])
                    if postamount > 0:
                        ans[key1].append([postamount, round(interval * round_c, 2), 0])
                    else:
                        ans[key1].append([0, round(interval * round_c, 2), 0])

                    preamount = round2(postamount * pow(1 + re, interval))

            ans[key1].append([preamount, finance_plan['Exit_year']])

        return ans
    # ans=get_samuelson_results(predict,finance_plan,campany_scal,indus_DEratio,indus_dtol,indus_re,indus_turnover)
