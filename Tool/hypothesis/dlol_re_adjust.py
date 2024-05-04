import pandas as pd

from Config import mongodb
from Data.read_mongo import merge_table_all


def dlol_re_adjust(rf, indus_code, capital_market, finance_round, a):
    beta_last_date = mongodb.read_mongo_limit("AM_origin", 'update_record',
                                                 {'tablename': 'valuation_list_company_market_beta'},
                                                 {'last_update_date': 1, '_id': 0})

    beta_last_date = pd.Timestamp(beta_last_date.values[0][0])
    all_beta = mongodb.read_mongo_limit("AM_origin", 'valuation_list_company_market_beta',
                                           {'update_date': beta_last_date}, {'beta': 1, 'beta_no_leverage': 1,
                                                                             'stock_code': 1, '_id': 0})
    company = mongodb.read_mongo_limit("AM_basement", 'valuation_basic_list_company_info',
                                          {'update_date': beta_last_date},
                                          {'gics_code_third': 1, 'stock_code': 1, '_id': 0})
    rm_last_date = mongodb.read_mongo_limit("AM_hypothesis", 'update_record', {'tablename': 'market_return_rate_SZ'},
                                               {'last_update_date': 1, '_id': 0})

    rm_last_date = pd.Timestamp(rm_last_date.values[0][0])

    rm = mongodb.read_mongo_limit("AM_hypothesis", 'market_return_rate_SZ', {'update_date': rm_last_date},
                                     {'market_return_rate_SZ': 1, '_id': 0})

    rm = rm.values[0][0]

    code_list = list(indus_code.keys())
    if len(code_list) == 1:
        valuation_industry_code1 = code_list[0]
        valuation_industry_code2 = ""
    else:
        valuation_industry_code1 = code_list[0]
        valuation_industry_code2 = code_list[1]

    target_company = company[(company['gics_code_third'] == valuation_industry_code1[:6]) | (
            company['gics_code_third'] == valuation_industry_code2[:6])]

    merge_list = [all_beta, target_company]

    all_beta_company = merge_table_all(merge_list, 'stock_code', 'inner').dropna()
    ul_beta = all_beta_company.mean()['beta_no_leverage']
    beta = all_beta_company.mean()['beta']
    round_dict = {0: 0.09, 1: 0.07, 2: 0.06, 3: 0.05, 4: 0.04, 5: 0.03, 6: 0}
    market_dict = {0: 0, 1: 0.03, 2: 0.04, 3: 0.01, 4: 0.05, 5: 0.06}
    alpha = round_dict[finance_round] + market_dict[capital_market]
    mp = rm - rf
    re = rf + beta * mp + alpha
    a["beta"] = beta
    a["mp"] = mp
    a["alpha"] = alpha
    a["ul_beta"] = ul_beta
    # if capital_market not in [0, 3]:
    #     listtime = GetListTime(None, NI, None, None, None, FFR['NI'], FFR['Rev'], Rev[0])
    #     listtime_for_dlol = listtime.get_dlol_re()
    #     # 2018年上市排队时长平均15个月
    #     t = listtime_for_dlol + 1.25
    #     if t > 5:
    #         re += 0.043
    #     else:
    #         re += 0.0098808 + 0.00659798 * t
    return re, a

