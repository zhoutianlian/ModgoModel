import numpy

from Tool.functions.vc_best_case_model.read_vc_table import read_for_share_value_case
from Tool.functions.vc_best_case_model.vc_best_case_functions import final_proceed, get_all_possible_cases, best_case, \
    ResultSet, InvestorAttr, discount_rate, adjust_value, discount_proceed_to_now, user_value, exit_multipliers, \
    exit_price, user_price, user_multiple, user_invested


def vc_best_case():

    exit_value, vc_series, vc_table, years_to_exit, indus_code = read_for_share_value_case()
    # 每一个投资者作为实例调用InvestAttr，并把所有投资者实例放在investor这个list里
    investor = []

    now = 0
    if now == 1:
        for i in range(vc_series + 1):
            investor_i = InvestorAttr(vc_table["series"][i], vc_table["invested_capital"][i], vc_table["buy_price"][i],
                                      vc_table["year"][i], vc_table["shares"][i], vc_table["pref"][i],
                                      vc_table["pref_multiple"][i], vc_table["req_return"][i],
                                      vc_table["clear_form"][i], vc_table["clear_cap_form"][i],
                                      vc_table["clear_cap_multiple"][i], vc_table["clear_cap_rate"][i],
                                      vc_table["user_has"][i])
            investor.append(investor_i)
            # clear_form = 0,1,2: 0-无分配权；1-无上限分配权；2-附上限分配权
    else:
        for i in range(vc_series + 1):
            investor_i = InvestorAttr(vc_table["series"][i], vc_table["invested_capital"][i], vc_table["buy_price"][i],
                                      vc_table["year"][i] + years_to_exit, vc_table["shares"][i], vc_table["pref"][i],
                                      vc_table["pref_multiple"][i], vc_table["req_return"][i],
                                      vc_table["clear_form"][i], vc_table["clear_cap_form"][i],
                                      vc_table["clear_cap_multiple"][i], vc_table["clear_cap_rate"][i],
                                      vc_table["user_has"][i])
            investor.append(investor_i)

    # print(investor_i.clear_cap_rate)
    # print(investor)

    # 根据输入得到所有执行的可能性列表all_list
    all_list = get_all_possible_cases(investor)
    # print(all_list)
    cases = len(all_list)

    # 调整最终值
    exit_value = adjust_value(exit_value, discount_rate(vc_series, indus_code), years_to_exit, "future")

    # 对每一种执行情况，计算每轮投资者最终的退出所得
    final_list = []
    for i in range(cases):
        # print("case_set_number________________________________________________________________________", i)
        pref = all_list[i]
        final = final_proceed(exit_value, vc_series, investor, pref)
        # 确保结果不是float64，进行类型转换
        for j in range(len(investor)):
            # print(type(final[j]), "type")
            if type(final[j]) == numpy.float64:
                final[j] = final[j].item()
        final_list.append(final)

    # 每一种执行情况作为实例调用ResultSet，并把所有投资者实例放在result这个list里
    result = []
    for i in range(cases):
        cases_i = ResultSet(all_list[i], final_list[i])
        result.append(cases_i)

    # 执行最优情况，返回最优解的编号
    number_of_best_case = best_case(result)

    # 输出项计算
    # 1.0 输出变量-折现率
    vc_rr = discount_rate(vc_series + 1, indus_code)

    # 2 投资者一般性输出

    # 2.1 最优执行方案
    best_execute = result[number_of_best_case].execute
    # 2.2 最优方案所得
    best_proceed = result[number_of_best_case].proceed
    # 2.3 最优方案所得现值
    discounted_proceed = discount_proceed_to_now(best_proceed, investor, vc_series, indus_code, years_to_exit)
    # 2.4 最优方案退出股价
    exit_price_set = exit_price(investor, vc_series, best_proceed)
    # 2.4 最优方案退出倍数
    exit_multipliers_set = exit_multipliers(investor, vc_series, best_proceed)

    # 3 用户情况输出

    # 3.0 用户情况(总投资金额，（（每轮，投资数））)
    user_invest = user_invested(investor, vc_series)
    # 3.1 用户所得（退出值， 现值, 细节每轮值）
    user_get = user_value(investor, best_proceed, discounted_proceed, vc_series)
    # 3.2 用户退出股价（退出股价，现在折算股价）
    user_p = user_price(investor, best_proceed, discounted_proceed, vc_series)
    # 3.3 用户回报倍数（回报倍数）
    user_m = user_multiple(investor, best_proceed, discounted_proceed, vc_series)

    return vc_rr, best_execute, best_proceed, discounted_proceed, exit_price_set, exit_multipliers_set, \
        user_invest[0], user_invest[1], [user_get[0], user_get[1]], user_get[2], user_p, user_m


# do = vc_best_case()
# print(do)
