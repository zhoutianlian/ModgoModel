# coding= utf-8
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
import datetime
from Data.Conn import connect_mysql_Require_Rate_of_Return, connect_mysql_valuation_samuelson
from Config.global_V import GlobalValue


class SamulsonFin():
    def valuation_samuelson(self,sam_input_for_fin):

        #分解输入值
        gics_code=sam_input_for_fin['gics_code']
        pre_1year_asset=float(sam_input_for_fin['pre_1year_asset'])
        pre_2year_asset=float(sam_input_for_fin['pre_2year_asset'])
        pre_3year_asset=float(sam_input_for_fin['pre_3year_asset'])
        liability=float(sam_input_for_fin['liability'])
        equity=sam_input_for_fin['equity']

        gics_code1 = list(gics_code.items())[0][0]
        gics_code1_percent = list(gics_code.items())[0][1]
        gics_code2 = list(gics_code.items())[1][0] if len(gics_code.keys()) == 2 else 0
        gics_code1_percent = float(gics_code1_percent)

        if str(gics_code1)[:2] != '40':
            gics_code1 = 0
            gics_code1_percent=0
        if str(gics_code2)[:2] != '40':
            gics_code2 = 0
            gics_code1_percent = 1

        if gics_code1==0:
            gics_code1, gics_code2 = gics_code2, gics_code1
            gics_code1_percent = 1


        # 提取系数
        connect_coef = connect_mysql_valuation_samuelson()
        sql_coef = 'select * from valuation_samuelson_model_coef'
        coef = pd.read_sql(sql_coef, connect_coef)

        # 提取债券利率数据
        connect_Rf = connect_mysql_Require_Rate_of_Return()
        sql_GovBond = 'select * from Faye_GovernmentBond'
        GovBond = pd.read_sql(sql_GovBond, connect_Rf)

        # 数据清洗
        Date = datetime.datetime.strptime(coef['updatedate'].values[-1], '%Y-%m-%d')
        Rf = float(GovBond[pd.to_datetime(GovBond['Date']).dt.year == Date.year].iloc[0, 1])

        if gics_code2 != 0:
            gics_third1 = str(gics_code1)
            gics_third2 = str(gics_code2)
            gics_second1 = str(gics_code1)[0:4]
            gics_second2 = str(gics_code2)[0:4]

            # 提取系数
            coef_assemblage1 = coef[coef['gics_code'] == gics_third1]
            if coef_assemblage1.empty:
                coef_assemblage1 = coef[coef['gics_code'] == gics_second1]

            coef_assemblage2 = coef[coef['gics_code'] == gics_third2]
            if coef_assemblage2.empty:
                coef_assemblage2 = coef[coef['gics_code'] == gics_second2]

            coef_assemblage = coef_assemblage1[['upper_limit', 'median_limit', 'lower_limit']].reset_index(
                drop=True) * gics_code1_percent + coef_assemblage2[
                                  ['upper_limit', 'median_limit', 'lower_limit']].reset_index(
                drop=True) * (1 - gics_code1_percent)

        else:
            gics_third1 = str(gics_code1)
            gics_second1 = str(gics_code1)[0:4]

            # 提取系数
            coef_assemblage = coef[coef['gics_code'] == gics_third1]
            if coef_assemblage.empty:
                coef_assemblage = coef[coef['gics_code'] == gics_second1]

            coef_assemblage = coef_assemblage[['upper_limit', 'median_limit', 'lower_limit']]

        result = False
        try:
            # 计算估值
            T = 5
            r1 = math.log(pre_1year_asset / pre_2year_asset)*0.5
            r2 = math.log(pre_2year_asset / pre_3year_asset)*0.5
            Rs = np.mean([r1, r2]) if np.mean([r1, r2]) >= Rf else Rf
            Rs = min(0.15, Rs)
            Rs = max(0, Rs)
            std = np.std([r1, r2])
            std = min(std, 10)


            liability = max(pre_1year_asset / 100, liability)
            d1 = (math.log(pre_1year_asset / liability) + Rf * T + 0.5 * pow(std, 2) * T) / pow((pow(std, 2) * T), 0.5)

            d2 = d1 - pow((pow(std, 2) * T), 0.5)
            Nd1 = norm.cdf(d1)
            Nd2 = norm.cdf(d2)
            cal_mv = pre_1year_asset * math.exp((Rs - Rf) * T) * Nd1 - liability * math.exp(-Rf * T) * Nd2

            mv_max = (cal_mv * coef_assemblage['upper_limit'].values[0]).item()
            mv_avg = (cal_mv * coef_assemblage['median_limit'].values[0]).item()
            mv_min = (cal_mv * coef_assemblage['lower_limit'].values[0]).item()

            price_max = mv_max / equity
            price_avg = mv_avg / equity
            price_min = mv_min / equity

            result = {'MV_max': mv_max, 'MV_avg': mv_avg, 'MV_min': mv_min, 'p_max': price_max, 'p_avg': price_avg,
                      'p_min': price_min}
        except Exception as e:
            print(e)
            pass
        ans = {GlobalValue.SAM_NAME: result}
        return ans





