# -*- coding: utf-8 -*-：


def dcf(cfs: list, discount_rate: float = 0, periods: list = None):
    period_count = len(cfs)
    if periods is None:
        periods = range(1, period_count + 1)
    elif period_count != len(periods):
        print('Cash flows mismatch the periods!')
        return None

    sum_npv = 0
    npv_cf = []
    df = []
    for i in range(period_count):
        df.append(1 / pow(1 + discount_rate, periods[i]))
        npv_cf.append(cfs[i] * df[-1])
        sum_npv += npv_cf[-1]

    return sum_npv, npv_cf, df
