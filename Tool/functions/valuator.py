from pandas import DataFrame
from pandas import Timestamp, Timedelta
from mongodb import *
from fs import *
from monte_carlo import monte_carlo
from numpy.random import *
from math import ceil, floor


pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


def val_preparation(fs_list, industry_code, do_monte_carlo: bool=False):

    tb_data_dict = {'bal': [], 'flow': []}
    for data in fs_list:
        if data[0:1] == 'b':
            tb_data_dict['bal'].append(data)
        elif data[0:1] == 'f':
            tb_data_dict['flow'].append(data)

    tb_data = read_mongo_tb_data('test_data', tb_data_dict, 'fsid')

    # 提取基本信息
    acc_mod = tuple(tb_data['bal'][['Accounting_Code', 'Accounting_System']].iloc[0].tolist())  # 会计制度, 会计准则
    print(acc_mod)

    # 删除无用信息
    for tb in tb_data:
        for acc in ['Accounting_Code', 'Accounting_System', 'fsid']:
            del tb_data[tb][acc]

    uncertain = 0
    # 整理流量表
    sort_flow_data, uncertain_add = sort_flow(tb_data['flow'])
    uncertain += uncertain_add
    # 整理存量表
    dates = sort_flow_data['EndDate'].tolist()
    sort_bal_data, uncertain_add = sort_bal(tb_data['bal'], dates)
    uncertain += uncertain_add
    years = len(sort_flow_data)

    # 分配估值算法
    if (years >= 3) and (uncertain <= 6):
        pass
        # smart_valuation(sort_bal_data, sort_flow_data, industry_code)
        return True
    elif years >= 1:
        lite_valuation(balance_sheet=sort_bal_data, profit_statement=sort_flow_data,
                       industry=industry_code, do_monte_carlo=do_monte_carlo)
        return True
    else:
        print('Valuation Failed!')
        return False


# def smart_valuation(bal_data, flow_data, industry_code, do_monte_carlo: bool=False):
#     print('Call Smart Valuation!')
#     pass


def lite_valuation(balance_sheet, profit_statement, industry, do_monte_carlo: bool=False):
    bs = BalLite(balance_sheet)  # 存量数据
    cc = CCLite(balance_sheet)  # 资本成本数据
    ps = FlowLite(profit_statement, bs, cc)  # 流量数据
    fs = FSLite(bs, ps)
    end_date = fs.report_date

    # 基本配置
    shrinkage = Config.SHRINKAGE
    slow_shrinkage = Config.SLOW_SHRINKAGE

    print(industry)
    # 提取资本成本
    target_de_ratio = 0.2112  # 目标带息债/全部投资资本比
    unleveraged_beta = 0.9721  # 行业无杠杆Beta
    risk_free_rate = 0.0392  # 无风险收益率
    market_risk = 0.0318  # 市场风险溢价
    liquidity_risk = [0.02, 0.19]  # 流动性溢价（贴现率）/折价（估值乘数）
    control_risk = [0, 0]  # 控制权折价（贴现率）/溢价（估值乘数）
    business_model = [0.02, 0.25]  # 商业模型风险折价（贴现率）/溢价（估值乘数）
    emotion_risk = [0, 0]  # 情感折价（贴现率）/溢价（估值乘数）
    policy_risk = [0, 0]  # 政策风险溢价（贴现率）/折价（估值乘数）

    market_growth_rate = 0.02  # 市场增长率
    industry_growth_rate = 0.18  # 行业增长率
    growth_rate = 0.23  # 公司增长率（预期）
    industry_cost_rate = 0.34  # 行业成本率
    industry_expense_rate = 0.25  # 行业费用率
    industry_turnover_days = {'DSI': 15.3, 'DSO': 37.2, 'DPO': 133.6}  # 行业营运资本周转天数（存货、应收、应付）
    business_cycle = 2  # 行业周期

    market_ev_to_ebit = 12.45  # 市场EV/EBIT
    industry_ev_to_ebit = 16.2  # 行业EV/EBIT率
    market_pe = 22.93  # 市场市盈率
    industry_pe = 22.1  # 行业市盈率
    market_roic = 0.08  # 市场ROIC
    market_roe = 0.12  # 市场ROE

    # 换算资本成本
    tax_rate = cc.data['TR']  # 公司所得税率
    leveraged_beta = unleveraged_beta * (1 + target_de_ratio * (1 - tax_rate))
    kd = cc.data['IR']  # 债务成本
    non_market_risk = liquidity_risk[0] + control_risk[0] + business_model[0] + emotion_risk[0] + policy_risk[0]
    unleveraged_ke = risk_free_rate + unleveraged_beta * market_risk + non_market_risk  # 无杠杆股东要求回报率
    ke = risk_free_rate + leveraged_beta * market_risk + non_market_risk  # 股东要求回报率

    # 打包变量
    parameters = {'EndDate': end_date,
                  'Financial Statement': fs,
                  'Shrinkage': shrinkage,
                  'Slow Shrinkage': slow_shrinkage,

                  'Target DE Ratio': target_de_ratio,
                  'Equity Cost': ke,
                  'Unleveraged Equity Cost': unleveraged_ke,
                  'Debt Cost': kd,
                  'Tax Rate': tax_rate,
                  'Special Risk Premium': 0,  # 特殊风险溢价

                  'Market Growth Rate': market_growth_rate,
                  'Industry Growth Rate': industry_growth_rate,
                  'Company Growth Rate': growth_rate,
                  'COGS Rate': -fs.data['COGS'] / fs.data['Sales'],
                  'Industry Cost Rate': industry_cost_rate,
                  'SGA Rate': -fs.data['SGA'] / fs.data['Sales'],
                  'Industry Expense Rate': industry_expense_rate,
                  'Turnover Days': {'DSI': -fs.data['Inv'] / fs.data['COGS'] * 360,
                                    'DSO': fs.data['AR'] / fs.data['Sales'] * 360,
                                    'DPO': -fs.data['AP'] / fs.data['COGS'] * 360},
                  'Industry Turnover Days': industry_turnover_days,
                  'Business Cycle': business_cycle,

                  'Market EV/EBIT': market_ev_to_ebit,
                  'Industry EV/EBIT': industry_ev_to_ebit,
                  'Market P/E': market_pe,
                  'Industry P/E': industry_pe,
                  'Market ROIC': market_roic,
                  'Market ROE': market_roe,

                  'Running': True,  # 经营状态
                  }

    # 设置随机变量
    random_sets = {'Company Growth Rate': {'Dist': 'Normal', 'Sigma': 0.19},  # 预期公司增长率（短期）
                   'Industry Cost Rate': {'Dist': 'Normal', 'Sigma': 0.01},  # 行业成本率
                   'Industry Expense Rate': {'Dist': 'Normal', 'Sigma': 0.11},  # 行业费用率
                   'Industry EV/EBIT': {'Dist': 'Normal', 'Sigma': 3.8},  # 行业EV/EBIT率
                   'Industry P/E': {'Dist': 'Normal', 'Sigma': 2.5},  # 行业P/E
                   'Special Risk Premium': {'Dist': 'Normal', 'Sigma': 0.01},  # 特殊风险溢价，围绕0的正态分布
                   }

    if do_monte_carlo:
        monte_carlo(lite_income_approach, parameters, random_sets, simulate_times=1)
    print('Call Lite Valuation!')


def lite_income_approach(parameters, random_process: bool=False, scenario: bool=False):
    assumption = ['Base']
    if scenario:
        assumption.extend(['Optimal', 'Pessimal'])

    for case in assumption:
        predict_data = [parameters]

        # 根据情景调整赋值
        if case == 'Optimal':
            pass
        elif case == 'Pessimal':
            pass

        # 递推报表
        for year in range(Config.PREDICT_PERIOD):
            if predict_data[-1]['Running']:
                predict_data.append(lite_predict_next_year(predict_data[-1], random_process))
            else:
                break

        fcff_val, fcff_score = dcf_fcff(predict_data)
        fcfe_val, fcfe_score = dcf_fcfe(predict_data)
        eva_val, eva_score = dcf_eva(predict_data)
        ae_val, ae_score = dcf_ae(predict_data)
        apv_val, apv_score = dcf_apv(predict_data)


    return None


def lite_predict_next_year(last_year, random_process: bool=False):
    # 确定随机参数
    if random_process:
        shrinkage = normal(last_year['Shrinkage'][0], last_year['Shrinkage'][1])
        slow_shrinkage = normal(last_year['Slow Shrinkage'][0], last_year['Slow Shrinkage'][1])
    else:
        shrinkage = last_year['Shrinkage'][0]
        slow_shrinkage = last_year['Slow Shrinkage'][0]

    # 确定经营目标
    min_cash_to_sales = Config.MIN_CASH_TO_SALES
    target_de_ratio = last_year['Target DE Ratio']

    # 提取财务报表
    fs = last_year['Financial Statement']
    last_end_date = last_year['EndDate']
    start_date = last_end_date + Timedelta(days=1)
    end_date = Timestamp(year=last_end_date.year + 1, month=last_end_date.month, day=1)
    end_date += Timedelta(days=end_date.days_in_month - 1)

    # 预测利润表不调整项目
    sales = fs.data['Sales'] * (1 + last_year['Company Growth Rate'])
    cogs = -sales * last_year['COGS Rate']
    gp = sales + cogs
    sga = -sales * last_year['SGA Rate']
    ebit = gp + sga

    # 预测资产负债表不调整项目
    inv = -cogs * last_year['Turnover Days']['DSI'] / 360
    ar = sales * last_year['Turnover Days']['DSO'] / 360
    ap = -cogs * last_year['Turnover Days']['DPO'] / 360
    oa = fs.data['OA']
    ol = fs.data['OL']
    share = fs.data['Share']

    # 预测现金流量表不调整项目
    inv_decrease = fs.data['Inv'] - inv
    ar_decrease = fs.data['AR'] - ar
    ap_increase = ap - fs.data['AP']

    # 预测调整项目
    cot = fs.cot
    borrow = 0  # 假设下年借款金额
    min_borrow = -fs.data['Debt']

    # 设置结束循环条件
    try_time = 0  # 尝试次数
    de_adjusted = False

    while True:

        interest = -(fs.data['Debt'] + borrow / 2) * last_year['Debt Cost']
        ebt = ebit + interest
        taxable = max(ebt, 0)
        if taxable > 0:
            for cot_year in range(Config.MAX_COT_YEAR):
                if taxable + cot[cot_year] > 0:
                    taxable += cot[cot_year]
                    cot[cot_year] = 0
                else:
                    cot[cot_year] += taxable
                    taxable = 0
                    break
            cot.append(0)
        elif taxable == 0:
            cot.append(ebt)
        cot.pop(0)
        tax = -taxable * last_year['Tax Rate']

        profit = ebt + tax
        ocf = profit + inv_decrease + ar_decrease + ap_increase
        cf = ocf + borrow
        cash = fs.data['Cash'] + cf
        debt = fs.data['Debt'] + borrow
        ta = cash + ar + inv + oa
        tl = debt + ap + ol
        se = ta - tl
        re = se - share

        try_time += 1
        if try_time >= Config.MAX_TRY_TIMES:
            break  # 超出尝试次数 结束循环

        if cash / sales < min_cash_to_sales:
            cash_shortfall = min_cash_to_sales * sales - cash
            min_borrow += min(cash_shortfall, 0)
            borrow += cash_shortfall
            de_adjusted = False  # 因尝试拯救现金，则调整DE改为False
            continue  # 做过调整，因此重做循环计算

        if not de_adjusted:
            target_debt = se * target_de_ratio
            debt_shortfall = debt - target_debt
            borrow_need = -debt_shortfall * (1 - shrinkage)
            borrow += borrow_need
            borrow = max(borrow, min_borrow)  # 防止过度还款
            de_adjusted = True  # 已尝试过1次调整DE，则改为True
            continue  # 做过调整，因此重做循环计算

        break  # 未检测出不良预测，直接结束循环

    # 生成下期数据
    bal_data = {'EndDate': end_date,
                'Cash': cash,  # 现金
                'AR': ar,  # 应收账款
                'Inv': inv,  # 存货
                'OA': oa,  # 其他资产
                'TA': ta,  # 资产总计
                'Debt': debt,  # 借款
                'AP': ap,  # 应付账款
                'OL': ol,  # 其他负债
                'TL': tl,  # 负债合计
                'Share': share,  # 股本
                'RE': re,  # 留存收益
                'SE': se,  # 所有者权益合计
                'LE': ta,  # 负债和所有者权益合计
                }
    bal = BalLite(bal_data)

    flow_data = {'EndDate': end_date,
                 'StartDate': start_date,
                 'Sales': sales,
                 'COGS': cogs,
                 'GP': gp,
                 'SGA': sga,
                 'EBIT': ebit,
                 'Int': interest,
                 'EBT': ebt,
                 'Tax': tax,
                 'NP': profit,
                 'dInv': inv_decrease,
                 'dAR': ar_decrease,
                 'dAP': ap_increase,
                 'OCF': ocf,
                 'Borrow': borrow,
                 'CF': cf,
                 }
    flow = FlowLite(flow_data)
    next_fs = FSLite(bal, flow, cot)

    company_gr = last_year['Industry Growth Rate'] * (1 - shrinkage) + last_year['Company Growth Rate'] * shrinkage
    industry_gr = last_year['Market Growth Rate'] * (1 - shrinkage) + last_year['Industry Growth Rate'] * shrinkage

    cogs_rate = last_year['Industry Cost Rate'] * (1 - slow_shrinkage) + last_year['COGS Rate'] * slow_shrinkage
    sga_rate = last_year['Industry Expense Rate'] * (1 - slow_shrinkage) + last_year['SGA Rate'] * slow_shrinkage
    dsi = last_year['Industry Turnover Days']['DSI'] * (1 - slow_shrinkage) \
        + last_year['Turnover Days']['DSI'] * slow_shrinkage
    dso = last_year['Industry Turnover Days']['DSO'] * (1 - slow_shrinkage) \
        + last_year['Turnover Days']['DSO'] * slow_shrinkage
    dpo = last_year['Industry Turnover Days']['DPO'] * (1 - slow_shrinkage) \
        + last_year['Turnover Days']['DPO'] * slow_shrinkage

    industry_ev_to_ebit = last_year['Market EV/EBIT'] * (1 - shrinkage) + last_year['Industry EV/EBIT'] * shrinkage
    industry_pe = last_year['Market P/E'] * (1 - shrinkage) + last_year['Industry P/E'] * shrinkage

    running = True
    if se <= 0:
        running = False

    next_year = {'EndDate': end_date,
                 'Financial Statement': next_fs,
                 'Shrinkage': last_year['Shrinkage'],
                 'Slow Shrinkage': last_year['Slow Shrinkage'],

                 'Target DE Ratio': target_de_ratio,
                 'Debt Cost': last_year['Debt Cost'],
                 'Tax Rate': last_year['Tax Rate'],
                 'Market Growth Rate': last_year['Market Growth Rate'],
                 'Industry Growth Rate': industry_gr,
                 'Company Growth Rate': company_gr,

                 'COGS Rate': cogs_rate,
                 'Industry Cost Rate': last_year['Industry Cost Rate'],
                 'SGA Rate': sga_rate,
                 'Industry Expense Rate': last_year['Industry Expense Rate'],
                 'Turnover Days': {'DSI': dsi, 'DSO': dso, 'DPO': dpo},
                 'Industry Turnover Days': last_year['Industry Turnover Days'],

                 'Market EV/EBIT': last_year['Market EV/EBIT'],
                 'Industry EV/EBIT': industry_ev_to_ebit,
                 'Market P/E': last_year['Market P/E'],
                 'Industry P/E': industry_pe,
                 'Market ROIC': last_year['Market ROIC'],
                 'Market ROE': last_year['Market ROE'],

                 'Running': running,
                 }
    return next_year
