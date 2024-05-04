# -*- coding: utf-8 -*-：
import copy
import itertools
from math import isnan


# 0 准备函数


# 0.1 制作顺序和倒叙list
from Config.global_V import GlobalValue
from Config.mongodb import read_mongo_limit


def order_list(number):
    list_a = []
    for i in range(0, number + 1):
        list_a.append(i)
    return list_a


def reverse_order_list(number):
    list_b = []
    for i in range(0, number + 1):
        ele = number - i
        list_b.append(ele)
    return list_b


# 0.2 根据行业代码和轮次寻找折现率/回报率

# 0.2.1 根据行业代码找到行业回报率
def indus_return(indus_code):
    indus_a = list(indus_code.keys())[0]
    a_pct = indus_code[indus_a]
    indus_b = list(indus_code.keys())[1]
    b_pct = indus_code[indus_b]
    rate_a = round(read_mongo_limit("AM_hypothesis", "industry_re", {'gics_code_third': indus_a},
                            {'_id': 0})["industry_re"].values[0], 3)
    rate_b = round(read_mongo_limit("AM_hypothesis", "industry_re", {'gics_code_third': indus_b},
                              {'_id': 0})["industry_re"].values[0], 3)
    rate = (rate_a * a_pct + rate_b * b_pct).item()
    return rate


# 0.2.2 根据行业代码和融资轮次调整回报率
def discount_rate(rounds, indus_code):
    factor_set = GlobalValue.MUTILPLIER
    factor = factor_set[rounds] if rounds <= 6 else factor_set[(len(factor_set) - 1)]
    indus_rr = indus_return(indus_code)
    vc_rr = round(indus_rr * factor, 3)
    return vc_rr


# 0.3.1 制作折现/未来 输出函数
def adjust_value(value, rate, time, future_or_back):
    f_or_b = 1 if future_or_back == 'future' else -1
    adjusted = value * pow(pow((1 + rate), f_or_b), time)
    adjusted = round(adjusted, 3)
    return adjusted


# 0.3.2对投资者proceed_list进行折现
def discount_proceed_to_now(best_proceed, investors, vc_series, indus_code, years_to_exit):
    discounted_proceed = []
    # use same discount rate
    for i in range(vc_series + 1):
        # print(discount_rate(vc_series, indus_code))
        discounted_i = adjust_value(best_proceed[i], discount_rate(vc_series, indus_code), years_to_exit, "back")
        discounted_proceed.append(discounted_i)
    # # use different discount rate
    # for i in range(vc_series + 1):
    #     discounted_i = adjust_value(best_proceed[i], discount_rate(i, indus_code), investors[i].years, "back")
    #     discounted_proceed.append(discounted_i)
    return discounted_proceed


# 1 考虑优先权
# 1.1 制作优先权所得函数
def total_pref_value(i, investor):
    y1 = investor[i].pref_multiple * investor[i].pref_multiple
    y2 = investor[i].req_return * investor[i].invested_capital * investor[i].years
    y = y1 + y2
    if isnan(y):
        y = 0
    return y


# 1.2 制作优先权循环函数：存在real_pref，优先权分配之后剩下left_value
def get_pref_left(list321, exit_value, investor, pref):
    left = exit_value
    for i in list321:
        # print(i)
        # 直接执行的话每个人执行多少优先权
        y = total_pref_value(i, investor)
        # 考虑是否执行之后究竟执行多少优先权：
        y = y * pref[i]
        # 考虑剩余额度之后，执行多少优先权：
        y = min(y, left)
        # 综合所有情况得出i要执行多少优先权，成为investor的属性之一
        investor[i].real_pref = y
        # 执行完这一轮总共还剩多少总值(无优先权或不执行优先权则为0）
        left = left - y

    return left


# 2 考虑普通股/参与权分配

# 2.1 参与普通股分配的股数
def get_common_shares(list123, investor, pref):
    for i in list123:
        # 考虑无分配权的投资者，一旦执行优先权，分配权股数为0；不执行的话，分配权股数为shares
        if (pref[i] == 1) and (investor[i].clear_form == 0):
            common_shares = 0
        else:
            common_shares = investor[i].shares
        # 考虑无分配权投资者之后的股票数
        investor[i].real_shares = common_shares


# 2.2 计算参与权分配上限

# 2.2.1把所有上限转换为乘数模式
def clear_cap_multiple(i, investor):
    # 此计算过程仅限于clear_form == 2(即表示附上限参与权）的情况下
    if investor[i].clear_cap_form == 0:
        multiple = investor[i].clear_cap_multiple
    else:
        multiple = investor[i].clear_cap_rate * investor[i].years
    return multiple


# 2.2.2得到上限具体值
def cap_value(i, investor, pref):
    if pref[i] == 0:  # 不执行优先权，则无上限
        cap = None
    else:  # pref[i] == 1 执行优先权
        if investor[i].clear_form == 2:  # clear_form == 2 意思是参与权是有上限的，则cap == 上限
            multiple = clear_cap_multiple(i, investor)
            cap = multiple * investor[i].invested_capital
            # 假如cap表示的是包括优先权和分配权总共的上限
            # cap = cap - investor[i].invested_capital * investor[i].pref_multiple
        elif investor[i].clear_form == 1:  # elif clear_form == 1 完全参与分配优先权，参与权没有上限
            cap = None
        else:  # 即表示investor[i].clear_form == 0 无参与分配优先权,，上限为0
            cap = 0

    return cap


# 2.3 按普通股进行分配
def distribute(list123, price, investor):
    list_result = []
    for i in list123:
        hold = round((price * investor[i].real_shares).item(), 2)
        list_result.append(hold)
    return list_result


# 2.4 判断参与分配权所得是否有人超额
def i_beyond(i, common_proceed, investor, pref):
    cap = cap_value(i, investor, pref)
    equal_cap = []
    if cap is None:
        beyond = 0
    elif common_proceed[i] > cap:
        beyond = 1
    else:
        beyond = 0
        if common_proceed[i] == cap:
            equal_cap.append(i)
    return beyond


def i_equal_cap(i, common_proceed, investor, pref):
    cap = cap_value(i, investor, pref)
    if common_proceed[i] == cap:
        equal = 1
    else:
        equal = 0
    return equal


def someone_beyond(list123, common_proceed, investor, pref):
    y = 0
    for i in list123:
        y += i_beyond(i, common_proceed, investor, pref)
    return y


# 2.5 参与分配循环函数
def distribute_round(list123, common_proceed, investor, pref):

    # 初始化excess_value, 初始化配的股数shares_to_add
    excess_value = 0
    shares_to_add = 0

    # step1 首先确定每一个人的beyond变量，按顺序放在beyond list里
    beyond = []
    for i in list123:
        whether_i_beyond = i_beyond(i, common_proceed, investor, pref)
        beyond.append(whether_i_beyond)

    # step2 其次把多余的部分存在excess_value, 计算重新分配的股数shares_to_add
    for i in list123:
        if beyond[i] == 1:  # beyond[i]为 1 说明该投资者超过自身上限
            # print("number", i, "is beyond")
            # 如果i超过上限，则把多余的部分加入excess_value，不参与继续分配,i的proceed存储为cap
            cap = cap_value(i, investor, pref)
            # print("cap =", cap, "proceed =", common_proceed[i])
            excess_value += common_proceed[i] - cap
            shares_to_add += 0
            common_proceed[i] = cap
        elif i_equal_cap(i, common_proceed, investor, pref) == 1:  # beyond[i]为0，但i_equal_cap为1说明刚好等于其cap，不参与继续分配
            shares_to_add += 0
            common_proceed[i] = common_proceed[i]
        else:
            # 如果i没有超过上限，则把i的股数加入继续分配的股数shares_to_add参与继续分配,i的proceed暂不做调整
            shares_to_add += investor[i].real_shares
            common_proceed[i] = common_proceed[i]

    # step3 再次分配
    add_price = (excess_value / shares_to_add).item()
    for i in list123:
        proceed_before = common_proceed[i]
        if (beyond[i] == 0) and (i_equal_cap(i, common_proceed, investor, pref) != 1):
            proceed_after = round((proceed_before + add_price * investor[i].real_shares).item(), 3)
        else:
            proceed_after = proceed_before
        common_proceed[i] = round(proceed_after, 2)
    # print("after", common_proceed)


# 2.6 执行循环中的必要函数

# 2.6.1 给proceed初始量
def initial_common_proceed(list123, price, investor):
    common_proceed = []
    for i in list123:
        hold_i = distribute(list123, price, investor)[i]
        common_proceed.append(hold_i)
    return common_proceed


# 2.6.2 执行循环分配函数
def distri_till_flat(list123, common_proceed, investor, pref):
    whether_someone_beyond = someone_beyond(list123, common_proceed, investor, pref)
    round_number = 1
    while whether_someone_beyond > 0:
        # test print
        # print("第", round_number, "轮分配开始-------------------------------------------")
        # print("how many investors beyond：", whether_someone_beyond)
        # for i in list123:
            # ib = i_beyond(i, common_proceed, investor, pref)
            # if  ib > 0:
                # print(i, "is beyond")
        distribute_round(list123, common_proceed, investor, pref)
        whether_someone_beyond = someone_beyond(list123, common_proceed, investor, pref)
        round_number += 1
        # print("\n")
        # print("\n")
        # print("\n")
        # print("\n")


# 3 将优先值和普通股分配值相加
def add_pref_common(list123, common_proceed, investor):  # 本函数将已经得出的real_pref与common_proceed相应相加

    # 3.1 提取优先值
    real_pref = []
    for i in list123:
        real_pref_i = round(investor[i].real_pref, 3)
        real_pref.append(real_pref_i)

    # 3.2 得到普通股值
    # 存在common_proceed的list中

    # 3.3 优先值加上普通值
    final = []
    for i in list123:
        total = real_pref[i] + common_proceed[i]
        final.append(total)

    return final


# 4. 综合执行函数
def final_proceed(exit_value, vc_series, investor, pref):
    # 制作list123为所有投资者轮次编号
    list123 = order_list(vc_series)
    list321 = reverse_order_list(vc_series)

    # 修正输入数据"pref"是否行使优先权，将None换成 0
    for i in list123:
        if pref[i] is None:
            pref[i] = 0

    # 执行get_pref_left函数，将执行优先权放在investor.real_pref里，得出剩余分配值
    left_value = get_pref_left(list321, exit_value, investor, pref)

    # 执行获得普通股数量
    get_common_shares(list123, investor, pref)

    shares = 0
    for i in list123:
        shares = shares + investor[i].real_shares
    total_common = shares

    price = left_value / total_common
    # 执行普通股分配循环
    # 先进行普通股初始化
    common_proceed = initial_common_proceed(list123, price, investor)
    # 循环分配至所有人不超额
    distri_till_flat(list123, common_proceed, investor, pref)
    # 将优先和普通相加
    y = add_pref_common(list123, common_proceed, investor)

    return y


# 5. 一共有多少种情况函数
def get_all_possible_cases(investor):
    # 把所有的优先方式从table提取出来填写在pref里，0-无优先权，1-有优先权
    # 首先获取pref的一个list
    pref = []
    for i in range(len(investor)):
        pref_i = investor[i].pref
        pref.append(pref_i)

    # 执行变量存在pref里：0-不执行优先权，1-执行优先权，None-不适用
    # 首先建立母集合，把不进行优先分配的设置为None，可以进行优先分配的设置为1
    master_pref = []
    not_pref = 0
    for i in range(len(pref)):
        if pref[i] == 0:
            master_pref.append(None)
            not_pref += 1
        else:
            master_pref.append(1)

    # 共有多少个可以优先分配的（series是非普通股轮数，这些不一定都有优先分配权，所以不能直接用series）
    count = len(pref) - not_pref
    # 针对母集合建立pref集合，把可以进行优先分配的（pref==1的）进行遍历，赋值0或1
    # neat_list仅仅包括需要考虑执行的投资者的执行情况（0,1）
    neat_list = []
    for i in itertools.product((0, 1), repeat=count):
        i = list(i)
        neat_list.append(i)

    cases = pow(2, count)
    # 复制一个all_list, 把原本没有优先权（pref为0）的投资者的pref值设置为None
    all_list = copy.deepcopy(neat_list)
    for i in range(len(pref)):
        if pref[i] == 0:
            for j in range(cases):
                all_list[j].insert(i, None)
    return all_list


# 6. 寻找最优的执行方式


def whether_consider_k(k, result):  # 考察第k个元素是否一致：一致，不consider；不一致：consider
    # 把所有的执行放在list_list中
    list_list = []
    cases = len(result)
    for i in range(cases):
        list_i = result[i].execute
        list_list.append(list_i)

    k_list = []
    for i in range(cases):
        k_i = list_list[i][k]
        k_list.append(k_i)

    factor = 0
    for i in range(cases - 1):
        for j in range(i+1, cases):
            if k_list[i] == k_list[j]:
                factor += 0
            else:
                factor += 1

    # consider = 1 if factor != 0 else 0
    return factor != 0


def i_cut_k_execute(i, k, result):  # 返回cases_list里面第i个case的、去掉第k个执行者（及其后者）的执行状况
    i_execute = result[i].execute
    if k <= len(i_execute):
        cut = i_execute[:k]
    else:
        cut = []
        print(k, "k is too large")
    return cut


def larger_case(i, j, k, result):
    # print("look at here, comparing proceed", "_________________", i, result[i].proceed[k], j, result[j].proceed[k])
    if result[i].proceed[k] > result[j].proceed[k]:
        larger = i
    else:
        larger = j
    return larger


def investor_sequence(result):
    sequence_list = []
    how_many = len(result[0].execute)
    for i in range(how_many):
        i = how_many - 1 - i
        sequence_list.append(i)
    # print(sequence_list)
    return sequence_list


def best_case(result):

    cases = []
    for i in range(len(result)):
        cases.append(i)
    # print(cases)
    # cases充满了0-31的编号

    for k in [6, 5, 4, 3, 2, 1, 0]:
        # print("This round is for investor number", k)

        cases_range = len(cases)
        # print("how many cases in this round?", cases_range)
        # print("k =", k, "----------------------------------")

        whether = whether_consider_k(k, result)
        if whether is True:
            # print("k is True. consider k =", k)
            cases_selected = []
            for i_index in range(cases_range - 1):
                for j_index in range(i_index + 1, cases_range):
                    i = cases[i_index]
                    j = cases[j_index]
                    # print(i, i_cut_k_execute(i, k, result), j, i_cut_k_execute(j, k, result))
                    # print(i, j)
                    # print(i_index, j_index, i, j)
                    if i_cut_k_execute(i, k, result) == i_cut_k_execute(j, k, result):
                        # print(i, j, "same", i_cut_k_execute(i, k, result))
                        larger = larger_case(i, j, k, result)
                        # print("larger:", larger)
                        cases_selected.append(larger)
                        # print("larger_added")
                    else:
                        # print("not same", i, j)
                        continue
        else:
            # print(k, "k Do not have a choice. Do not consider", k)
            continue
        # print(cases_selected)
        # print("")
        # print("")
        cases = cases_selected

    if len(cases_selected) == 1:
        selected = cases_selected[0]
    else:
        selected = None
        print("Error. Not returning to one case.")

    return selected


# 7. 退出价值考虑时间


# 8. 执行过程中的类的制作

# 8.1 投资者类，每个对象为投资者，其属性包括轮次、投入资本、购买价格、投资时长、优先股情况等
class InvestorAttr:
    # 为InvestorAttr添加属性
    def __init__(self, series, invested_capital, buy_price, year, shares, pref, pref_multiple, req_return, clear_form,
                 clear_cap_form, clear_cap_multiples, clear_cap_rate, user_has):
        self.series = series
        self.invested_capital = invested_capital
        self.buy_price = buy_price
        self.years = year
        self.shares = shares
        self.pref = pref
        self.pref_multiple = pref_multiple
        self.req_return = req_return
        self.clear_form = clear_form
        self.clear_cap_form = clear_cap_form
        self.clear_cap_multiple = clear_cap_multiples
        self.clear_cap_rate = clear_cap_rate
        self.user_has = user_has


# 8.2 把结果放进result_list中
class ResultSet:
    # 为Result添加属性
    def __init__(self, execute, proceed):
        self.execute = execute
        self.proceed = proceed


# 9 用户退出价值

# 9.1.0输入用户投资情况
def user_invested(investor, vc_series):
    invested = []
    total_invested = 0
    for i in range(vc_series + 1):
        has = investor[i].user_has
        if isnan(has) is False:
            this_round = [i, has]
            invested.append(this_round)

            invested_this_round = investor[i].buy_price * has
            total_invested += invested_this_round
    total_invested = round(total_invested, 2)

    return total_invested, invested


# 9.1.1输入用户有多少钱的股份
def user_value(investor, proceed_future, proceed_to_now, vc_series):
    user_get_future = 0
    user_get_future_detail = []
    user_get_to_now = 0
    for i in range(vc_series + 1):
        has = investor[i].user_has
        if isnan(has) is False:
            this_round_value = round(proceed_future[i] * has / investor[i].shares, 3)
            user_get_future += this_round_value
            this_round_get = [i, this_round_value]
            user_get_future_detail.append(this_round_get)

            user_get_to_now += proceed_to_now[i] * has / investor[i].shares

    user_get = [round(user_get_future, 3), round(user_get_to_now, 3), user_get_future_detail]

    return user_get


# 9.1.2 输入用户退出股价是多少
def user_price(investor, proceed_future, proceed_to_now, vc_series):
    user_shares = 0
    for i in range(vc_series + 1):
        has = investor[i].user_has
        if isnan(has) is False:
            user_shares += has

    user_get = user_value(investor, proceed_future, proceed_to_now, vc_series)
    price_future = round(user_get[0] / user_shares, 2)
    price_now = round(user_get[1] / user_shares, 2)
    return price_future, price_now


# 9.1.3 输入用户退出倍数是多少
def user_multiple(investor, proceed_future, proceed_to_now, vc_series):
    total_invested = user_invested(investor, vc_series)[0]
    user_get = user_value(investor, proceed_future, proceed_to_now, vc_series)
    multiple = round(user_get[0] / total_invested, 2)
    return multiple


# 9.2 每轮用户退出股价是多少？
def exit_price(investor, vc_series, best_proceed):
    exit_at = []
    for i in range(vc_series + 1):
        now_price = round(best_proceed[i] / investor[i].shares, 3)
        exit_at.append(now_price)
    return exit_at


# 9.3 每轮用户退出的回报倍数是多少？
def exit_multipliers(investor, vc_series, best_proceed):
    multi_set = []
    for i in range(vc_series + 1):
        exit_at = exit_price(investor, vc_series, best_proceed)[i]
        price = investor[i].buy_price
        multi = round(exit_at / price, 2)
        multi_set.append(multi)

    return multi_set

