# -*- coding: utf-8 -*-：
from Tool.functions.save.save_data_for_businessmodel import save_data
from Model.business_model.process_data_for_businessmodel_above3 import process_data_above3
from Model.business_model.process_data_for_businessmodel_under3 import process_data_under3
from Model.business_model.process_data_for_businessmodel_dloc import process_data_dloc
from Model.business_model.process_data_for_businessmodel_profit_growth_rate_coef import process_data_profit_growth_rate_coef
from Model.business_model.process_data_for_businessmodel_gross_profit_ratio_coef import process_data_gross_profit_ratio_coef
from Model.business_model.process_data_for_businessmodel_cost_ratio_coef import process_data_cost_ratio_coef
from Model.business_model.process_data_for_businessmodel_expense_ratio_coef import process_data_expense_ratio_coef
from Model.business_model.process_data_for_businessmodel_risk_premium_coef import process_data_risk_premium_coef


def business_model(VID, flag, financial_report_data, data, main_industry):
    #flag=0:精简-》financial_report_data 最新年报数据 or 月报年化数据
    #flag=1:精细-》financial_report_data 最新年报数据 or 月报年化数据
    #flag=2:风投模型 -》 financial_report_data={}
    #financial_report_data={'Rev','NI','saleexp','Totalcost'}

    # 分别计算三年以上、三年及以下商模得分
    if data['company_operation_duration'] > 3:
        result = process_data_above3(data, flag, financial_report_data, main_industry)
    else:
        result = process_data_under3(data, main_industry)
    # 计算缺乏控制权折价
    dloc = process_data_dloc(data)

    # 计算营收增长率调整系数
    if flag == 2:
        profit_growth_rate = None
    else:
        profit_growth_rate = process_data_profit_growth_rate_coef(data, flag, financial_report_data)

    # 计算毛利率调整系数
    if flag == 2:
        gross_profit_ratio = None
    else:
        gross_profit_ratio = process_data_gross_profit_ratio_coef(data, flag, financial_report_data)

    # 计算成本率调整系数，精简模型，营业成本/营业收入
    if flag == 2:
        cost_ratio = None
        expense_ratio = None
    if flag == 0:
        cost_ratio = process_data_cost_ratio_coef(data, financial_report_data)
        expense_ratio = None
    if flag == 1:
        cost_ratio = None
        expense_ratio = process_data_expense_ratio_coef(data, financial_report_data)

    # 计算特殊风险调整系数
    risk_premium = process_data_risk_premium_coef(data, flag, financial_report_data, main_industry)

    # 存储数据
    save_data(result, dloc, profit_growth_rate, gross_profit_ratio, cost_ratio, expense_ratio, risk_premium, PID)

    # wacc调整系数
    nresult = result * 0.6 + dloc * 0.1 + risk_premium * 0.3
    if nresult > 60:
        wacc_coef = (60 - nresult) / 5 * 0.0125
    else:
        wacc_coef = (60 - nresult) / 5 * 0.0083

    # 成本率/费用率调整系数
    if flag == 0:
            cost_ratio_coef = 1 - (cost_ratio - 60) / 5 * 0.0125
    elif flag == 1:
            cost_ratio_coef = 1 - (expense_ratio - 60) / 5 * 0.0125
    else:
        cost_ratio_coef = None

    # 毛利率调整系数
    if flag == 2:
        gross_profit_ratio_coef = None
    else:
        gross_profit_ratio_coef = 1 + (gross_profit_ratio - 60) / 2.5 * 0.01


    # 营收增长率调整系数
    if flag == 2:
        profit_growth_rate_coef = None
    else:
        profit_growth_rate_coef = 1 + (profit_growth_rate - 60) / 4 * 0.0875

    dict_bmcoef = {
                   'wacc_coef': wacc_coef,
                   'cost_ratio_coef': cost_ratio_coef,
                   'gross_profit_ratio_coef': gross_profit_ratio_coef,
                   'profit_growth_rate_coef': profit_growth_rate_coef}
    # print(dict_bmcoef)
    return [VID, dict_bmcoef]


# print(PID)
# gl.set_name('test')
# financial_report_data = {'Rev':3715203,'NI':1130565,'saleexp':1213526,'Totalcost':2375621}
# main_industry = '201010'
# flag = 1
# business_model(99, flag, financial_report_data, main_industry)
# data={'adictionary':{'one':1,'two':2},'alist':[12,31,4,52,5],'astr':'aaaa'}
