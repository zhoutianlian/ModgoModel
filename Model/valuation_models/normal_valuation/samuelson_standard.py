# -*- coding: utf-8 -*-：
import numpy as np
import pandas as pd
import math
from scipy.stats import norm

from Config.global_V import GlobalValue
from Tool.functions.is_result_legal import result_legal
from Data.Conn import connect_mysql_valuation_samuelson, connect_mysql_Require_Rate_of_Return


class Samuelson_Normal_Standard():

    def valuation_samuelson(self,sam_input_norstandard):
        # 暂定的变量
        # 无风险利率按照2018年最后一天取
        year_now = 2018
        growth_rate_discount = 0.5
        # 定义取上下coef值的区间宽度
        ratio = 0.5


        #分解输入值
        asset3=sam_input_norstandard['asset3']
        asset2=sam_input_norstandard['asset2']
        asset1=sam_input_norstandard['asset1']
        debt=sam_input_norstandard['debt']
        liabi=sam_input_norstandard['liabi']
        wacc=sam_input_norstandard['wacc']
        interestrate=sam_input_norstandard['interestrate']
        induscode=sam_input_norstandard['induscode']
        SC=sam_input_norstandard['SC']

        # 读数据库
        connect = connect_mysql_valuation_samuelson()
        sql_data = 'select * from samuelsonFull'
        ref = pd.read_sql(sql_data, connect)
        connect.close()

        # standard与light的区别是
        # light版本只需要输入近三年sales，并以sales的增长率作为资本增长率
        # standard版本需要输入近三年asset，直接计算asset的增长率


        # 提取债券利率数据
        connect_Rf = connect_mysql_Require_Rate_of_Return()
        sql_GovBond = 'select * from Faye_GovernmentBond'
        GovBond = pd.read_sql(sql_GovBond, connect_Rf)

        # 数据清洗
        rf = float(GovBond[pd.to_datetime(GovBond['Date']).dt.year == year_now].iloc[0, 1])


        # 读取两个行业的代码和占比
        indus_a = list(induscode.keys())[0]
        indus_a_index = int(indus_a)
        pct_a = induscode[indus_a]
        if pct_a == 1:
            pct_b = 0
            indus_b_index = None
        else:
            indus_b = list(induscode.keys())[1]
            pct_b = induscode[indus_b]
            indus_b_index = int(indus_b)

        # 计算coef list
        ref['ev'] = ref['liabi'] + ref['mv']
        ref['coef'] = ref['ev'] / ref['asset']

        # 对于两个行业分别读取三个coef
        # 行业a
        med_a = ref.loc[ref['GICS'] == indus_a_index, 'coef'].median()
        number_a = ref.loc[ref['GICS'] == indus_a_index, 'stockcode'].count().item()
        downnumber_a = int(number_a / 2)
        upnumber_a = number_a - downnumber_a
        # 行业a的上下系数
        ref['squaredis'] = pow(ref['coef'] - med_a, 2)
        upsum_a = (ref.loc[(ref['GICS'] == indus_a_index) & (ref['coef'] - med_a >= 0), ('squaredis')].sum()).item()
        upstd_a = pow(upsum_a / upnumber_a, 0.5)
        up_a = med_a + upstd_a * ratio
        downsum_a = (ref.loc[(ref['GICS'] == indus_a_index) & (ref['coef'] - med_a < 0), 'squaredis'].sum()).item()
        downstd_a = pow(downsum_a / downnumber_a, 0.5)
        down_a = med_a - downstd_a * ratio
        # 行业a得到三个系数
        coef1a = down_a
        coef2a = med_a
        coef3a = up_a

        # 行业b
        if pct_a == 1:
            coef1b = 0
            coef2b = 0
            coef3b = 0
        else:
            med_b = ref.loc[ref['GICS'] == indus_b_index, 'coef'].median()
            number_b = ref.loc[ref['GICS'] == indus_b_index, 'stockcode'].count().item()
            downnumber_b = int(number_b / 2)
            upnumber_b = number_b - downnumber_b
            # 行业a的上下系数
            ref['squaredis'] = pow(ref['coef'] - med_b, 2)
            upsum_b = (ref.loc[(ref['GICS'] == indus_b_index) & (ref['coef'] - med_b >= 0), ('squaredis')].sum()).item()
            upstd_b = pow(upsum_b / upnumber_b, 0.5)
            up_b = med_b + upstd_b * ratio
            downsum_b = (ref.loc[
                             (ref['GICS'] == indus_b_index) & (ref['coef'] - med_b < 0), 'squaredis'].sum()).item()
            downstd_b = pow(downsum_b / downnumber_b, 0.5)
            down_b = med_b - downstd_b * ratio
            # 行业a得到三个系数
            coef1b = down_b
            coef2b = med_b
            coef3b = up_b

        # 结合两个行业的coef
        coef1 = coef1a * pct_a + coef1b * pct_b
        coef2 = coef2a * pct_a + coef2b * pct_b
        coef3 = coef3a * pct_a + coef3b * pct_b

        # 以下为Samuelson估算mv

        # 参数计算
        T = 5
        asset = asset3
        ev1 = coef1 * asset
        ev2 = coef2 * asset
        ev3 = coef3 * asset

        # 计算增长率r=ga-ra=资产增长率-资产成本（WACC）
        ga = np.average([math.log(asset2 / asset1), math.log(asset3 / asset2)]).item()
        ra = wacc * (asset - liabi + debt) / asset + rf * (liabi - debt) / asset
        ra = math.log(ra + 1)
        ra = min(0.15, ra)
        ra = max(0, ra)

        ga = max(ra, ga * growth_rate_discount)
        r = ga - ra
        # 计算liability cost rl:rate of liability负债成本
        rl = math.log(interestrate * debt / liabi + rf * (liabi - debt) / liabi + 1)

        # 计算N(d1)和N(d2)
        #  计算sigma
        assetrate1_2 = math.log(asset2 / asset1)
        assetrate2_3 = math.log(asset3 / asset2)
        sigma = np.std([assetrate1_2, assetrate2_3]).item()
        sigma = min[sigma, 10]

        # 针对下、中、上三个系数，计算Nd1,Nd2，mv
        cal_mvlist = []
        for ev in [ev1, ev2, ev3]:

            liabi = max(ev / 100, liabi)

            d1 = (math.log(ev / liabi) + (ra + pow(sigma, 2) / 2) * T) / (sigma * pow(T, 0.5))
            d2 = (math.log(ev / liabi) + (rl - pow(sigma, 2) / 2) * T) / (sigma * pow(T, 0.5))

            Nd1 = norm.cdf(d1).item()
            Nd2 = norm.cdf(d2).item()

            cal_mv = ev * Nd1 * math.exp(r * T) - liabi * Nd2 * math.exp(-rl * T)
            cal_mvlist.append(cal_mv)

        # 放进字典里
        dic_mv = {'MV_min': cal_mvlist[0], 'MV_avg': cal_mvlist[1], 'MV_max': cal_mvlist[2],
                  'p_min': cal_mvlist[0] / SC, 'p_avg': cal_mvlist[1] / SC, 'p_max': cal_mvlist[2] / SC}

        #判断合法
        if result_legal('nor_same_standard',dic_mv)==False:
            dic_mv=False
        else:
            #约2位
            for key in dic_mv.keys():
                if type(dic_mv[key])==float:
                    dic_mv[key]=round(dic_mv[key],2)
        # if dic_mv['MV_min'] < 0:
        #     log1 = math.log(asset2 / asset1)
        #     log2 = math.log(asset3 / asset2)
        #     print("log12:", log1, log2)
        #     print(ga)
        # print("r = ga - ra(weighted wacc) = ", ga, " - ", ra)
        # print("r:", r, "rl:", rl)
        # print(indus_a_index)
        # print (asset - liabi)
        # print(dic_mv['MV_min'], dic_mv['MV_avg'], dic_mv['MV_max'])
        # print("coeficiant:", coef1, coef2, coef3)

        ans = {GlobalValue.SAM_NAME: dic_mv}

        return ans






# if __name__ == '__main__':
# temp = samuelson_mv(3008886700,1281457200,1310119600,1415404900,224872200,2105332900,0.15,0.10,{'101010': 1},100)
#     # asset,sales1,sales2,sales3,debt,liabi,wacc,interestrate,induscode
#     # asset = 3008886700
#     # sales1 = 1281457200
#     # sales2 = 1310119600
#     # sales3 = 1415404900
#     # debt = 224872200
#     # liabi = 2105332900
#     # wacc = 0.15
#     # interestrate = 0.10
#     # induscode = {'101010': 1}
# print(temp)

