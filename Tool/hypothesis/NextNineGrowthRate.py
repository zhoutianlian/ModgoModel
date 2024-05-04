# -*- coding: utf8 -*-：
import numpy as np
import math
import copy

from Config.mongodb import read_mongo_all
from Tool.functions.indus_code_forA import retrack_Ainsudcode



def get_GR9(growth_rate1, growth_rate2, growth_rate3, gics_code):

    gics_code = retrack_Ainsudcode("industry_ln_revenue_growth_rate", gics_code, column="gics_code")

    # 读取数据
    LnRevenue_avg = read_mongo_all("AM_hypothesis","industry_ln_revenue_growth_rate")
    SimpleRevenue_avg = read_mongo_all("AM_hypothesis", "industry_simple_revenue_growth")
    GDP_n_M2 = read_mongo_all("AM_hypothesis", "gdp_n_m2")

    if len(gics_code.keys())==2:
        gics_code1 = list(gics_code.items())[0][0]
        gics_code1_percent = list(gics_code.items())[0][1]
        gics_code2 = list(gics_code.items())[1][0]
    else:
        gics_code1 = list(gics_code.items())[0][0]
        gics_code1_percent = list(gics_code.items())[0][1]
        gics_code2=0


    if gics_code2 != 0:
        gics_code_third1 = str(gics_code1)[0:6]
        gics_code_third2 = str(gics_code2)[0:6]

        # 转化为ln之后的增长率
        if (growth_rate1 > -1) | (growth_rate2 > -1) | (growth_rate3 > -1):
            gowth_ln1 = math.log(growth_rate1 + 1)
            gowth_ln2 = math.log(growth_rate2 + 1)
            gowth_ln3 = math.log(growth_rate3 + 1)

            trend = np.polyfit([1, 2, 3], [gowth_ln1, gowth_ln2, gowth_ln3], 1)[1]
            basic_avg = (gowth_ln1 + gowth_ln2 + gowth_ln3) / 3

            industry_avg1 = \
            LnRevenue_avg.loc[LnRevenue_avg['gics_code'] == gics_code_third1, 'industry_growth_rate_avg'].values[-1]

            industry_avg2 = \
            LnRevenue_avg.loc[LnRevenue_avg['gics_code'] == gics_code_third2, 'industry_growth_rate_avg'].values[-1]

            industry_avg = industry_avg1 * gics_code1_percent + industry_avg2 * (1 - gics_code1_percent)

        else:
            trend = np.polyfit([1, 2, 3], [growth_rate1, growth_rate2, growth_rate3], 1)[1]
            basic_avg = (growth_rate1 + growth_rate2 + growth_rate3) / 3
            industry_avg1 = SimpleRevenue_avg.loc[
                SimpleRevenue_avg['gics_code'] == gics_code_third1, 'industry_growth_rate_avg'].values[-1]
            industry_avg2 = SimpleRevenue_avg.loc[
                SimpleRevenue_avg['gics_code'] == gics_code_third2, 'industry_growth_rate_avg'].values[-1]
            industry_avg = industry_avg1 * gics_code1_percent + industry_avg2 * (1 - gics_code1_percent)
    else:
        gics_code_third1 = str(gics_code1)[0:6]

        # 转化为ln之后的增长率
        if (growth_rate1 > -1) & (growth_rate2 > -1) & (growth_rate3 > -1):
            gowth_ln1 = math.log(growth_rate1 + 1)
            gowth_ln2 = math.log(growth_rate2 + 1)
            gowth_ln3 = math.log(growth_rate3 + 1)

            trend = np.polyfit([1, 2, 3], [gowth_ln1, gowth_ln2, gowth_ln3], 1)[1]
            basic_avg = (gowth_ln1 + gowth_ln2 + gowth_ln3) / 3
            industry_avg = \
            LnRevenue_avg.loc[LnRevenue_avg['gics_code'] == gics_code_third1, 'industry_growth_rate_avg'].values[-1]

        else:
            trend = np.polyfit([1, 2, 3], [growth_rate1, growth_rate2, growth_rate3], 1)[1]
            basic_avg = (growth_rate1 + growth_rate2 + growth_rate3) / 3
            industry_avg = SimpleRevenue_avg.loc[
                SimpleRevenue_avg['gics_code'] == gics_code_third1, 'industry_growth_rate_avg'].values[-1]

    gdp = GDP_n_M2['gdp_growth'].values[-1]

    # 计算九年营收增长率
    GR_name = {}
    if (basic_avg > industry_avg) & (trend >= 0):
        # 先按照trend增长两年
        GR_name['growth_rate_year1'] = basic_avg + trend
        GR_name['growth_rate_year2'] = GR_name['growth_rate_year1'] + trend

        # 然后三年降回industry水平
        decreas_speed_industry = (GR_name['growth_rate_year2'] - industry_avg) / 3
        GR_name['growth_rate_year3'] = GR_name['growth_rate_year2'] - decreas_speed_industry
        GR_name['growth_rate_year4'] = GR_name['growth_rate_year3'] - decreas_speed_industry
        GR_name['growth_rate_year5'] = GR_name['growth_rate_year4'] - decreas_speed_industry

        # 维持两年industry水平
        GR_name['growth_rate_year6'] = GR_name['growth_rate_year5']
        GR_name['growth_rate_year7'] = GR_name['growth_rate_year6']

        # 十年趋近于gdp
        decrease_speed_gdp = (GR_name['growth_rate_year7'] - gdp) / 10
        GR_name['growth_rate_year8'] = GR_name['growth_rate_year7'] - decrease_speed_gdp
        GR_name['growth_rate_year9'] = GR_name['growth_rate_year8'] - decrease_speed_gdp

    elif (basic_avg > industry_avg) & (trend < 0):
        # 按照trend降回industry水平
        x = 0
        temp_growth_rate = copy.deepcopy(basic_avg) + copy.deepcopy(trend)
        GR_name['growth_rate_year' + str(x)] = temp_growth_rate
        while temp_growth_rate > industry_avg:
            x = x + 1
            if x > 9:
                break
            GR_name['growth_rate_year' + str(x)] = temp_growth_rate
            temp_growth_rate = temp_growth_rate + trend

        # 维持3年industry
        count_three = 0
        while x <= 9:
            x = x + 1
            count_three = count_three + 1
            if x > 9:
                break
            if count_three > 3:
                x = x -1
                break
            GR_name['growth_rate_year' + str(x)] = GR_name['growth_rate_year' + str(x - 1)]

        # 十年趋近于gdp
        while x <= 9:
            decrease_speed_gdp = (GR_name['growth_rate_year' + str(x - 1)] - gdp) / 10
            x = x + 1
            if x > 9:
                break
            GR_name['growth_rate_year' + str(x)] = GR_name['growth_rate_year' + str(x - 1)] - decrease_speed_gdp

    elif (basic_avg <= industry_avg) & (trend > 0):
        # 按trend上升到industry水平
        x = 0
        temp_growth_rate = copy.deepcopy(basic_avg) + copy.deepcopy(trend)
        GR_name['growth_rate_year' + str(x)] = temp_growth_rate
        while temp_growth_rate < industry_avg:
            x = x + 1
            if x > 9:
                break
            GR_name['growth_rate_year' + str(x)] = temp_growth_rate
            temp_growth_rate = temp_growth_rate + trend

        # 维持3年industry
        count_three = 0
        while x <= 9:
            x = x + 1
            count_three = count_three + 1
            if x > 9:
                break
            if count_three > 3:
                x = x-1
                break
            GR_name['growth_rate_year' + str(x)] = GR_name['growth_rate_year' + str(x - 1)]

        # 十年趋近于gdp
        while x <= 9:
            decrease_speed_gdp = (GR_name['growth_rate_year' + str(x - 1)] - gdp) / 10
            x = x + 1
            if x > 9:
                break
            GR_name['growth_rate_year' + str(x)] = GR_name.get('growth_rate_year' + str(x - 1)) - decrease_speed_gdp

    elif (basic_avg <= industry_avg) & (trend <= 0):
        # 按trend下降两年
        GR_name['growth_rate_year1'] = basic_avg + trend
        GR_name['growth_rate_year2'] = GR_name['growth_rate_year1'] + trend

        # 然后三年升回industry水平
        decreas_speed_industry = (GR_name['growth_rate_year2'] - industry_avg) / 3
        GR_name['growth_rate_year3'] = GR_name['growth_rate_year2'] - decreas_speed_industry
        GR_name['growth_rate_year4'] = GR_name['growth_rate_year3'] - decreas_speed_industry
        GR_name['growth_rate_year5'] = GR_name['growth_rate_year4'] - decreas_speed_industry

        # 维持两年industry水平
        GR_name['growth_rate_year6'] = GR_name['growth_rate_year5']
        GR_name['growth_rate_year7'] = GR_name['growth_rate_year6']

        # 十年趋近于gdp
        decrease_speed_gdp = (GR_name['growth_rate_year7'] - gdp) / 10
        GR_name['growth_rate_year8'] = GR_name['growth_rate_year7'] - decrease_speed_gdp
        GR_name['growth_rate_year9'] = GR_name['growth_rate_year8'] - decrease_speed_gdp

    GR_list = [float(GR_name['growth_rate_year1']), float(GR_name['growth_rate_year2']), float(GR_name['growth_rate_year3']), float(GR_name['growth_rate_year4']), float(GR_name['growth_rate_year5']),
               float(GR_name['growth_rate_year6']), float(GR_name['growth_rate_year7']), float(GR_name['growth_rate_year8']), float(GR_name['growth_rate_year9'])]

    return GR_list