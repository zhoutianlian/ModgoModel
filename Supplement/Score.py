from datetime import datetime
import math


__all__ = ['effectiveness']


def effectiveness(bal, flow, doc):
    # 最新报表时间度量
    bal_dates, flow_dates = bal['date'].tolist(), flow['date'].tolist()
    new_bal, new_flow = max(bal_dates), max(flow_dates)
    new_year = math.sqrt(int(str(new_bal)[:4]) * int(str(new_flow)[:4]))
    new_month = math.sqrt(int(str(new_bal)[4:6]) * int(str(new_flow)[4:6]))
    new_eft = new_year * 100 + new_month

    # 报表丰富度度量
    bal_acc = len(bal.columns)
    flow_acc = len(flow.columns)
    detail_eft = math.sqrt(bal_acc * flow_acc)

    # 报表数量度量
    count_eft = math.sqrt(math.sqrt(len(bal) * len(flow)))  # 对几何平均数开2次方，报表数量增多效益递减

    # 报表跨度度量
    old_bal = min(bal_dates)
    flow_sinces = flow['start'].tolist()
    old_flow = min(flow_sinces)
    old_year = math.sqrt(int(str(old_bal)[:4]) * int(str(old_flow)[:4]))
    old_month = math.sqrt(int(str(old_bal)[4:6]) * int(str(old_flow)[-2:]))
    span_year = new_year - old_year
    span_month = new_month - old_month
    span_eft = span_year * 100 + span_month
    span_eft = min(span_eft, 350)  # 限制在3年（利润表+0.5年）内，并非报表越多越好

    # 评估时间度量
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    after_year = year - new_year
    after_month = month - new_month - 1  # 月报都是月末的，故扣去1个月
    after_day = day
    time_eft = math.sqrt(after_year * 10000 + after_month * 100 + after_day)  # 对差异天数开方，远离报表越远越无效

    # 评估方法度量
    sum_wt = 0
    for approach in ['dcf', 'mkt', 'opt', 'aba']:
        approach_name = approach + '_detail'
        if approach_name in doc:
            for sub_model in doc[approach_name].values():
                if type(sub_model) is dict:
                    try:
                        sum_wt += pow(sub_model['wt'], 2) / 10
                    except:
                        continue
    method_eft = sum_wt

    syn_eft = new_eft + detail_eft / 1e2 + count_eft / 1e3 + span_eft / 1e5 + time_eft / 1e4 + method_eft / 1e4
    return syn_eft
