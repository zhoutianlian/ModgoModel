# 财务报表
import pandas as pd
from pandas import DataFrame, Timestamp, Timedelta
import numpy as np
from collections import OrderedDict
from copy import copy
from quickfunction import *
from CONFIG.config import Config

# 该组件定义了 类：存量表 类：流量表
# 函数：整理流量报表
# 函数：整理存量报表

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def count_months(date1, date2):
    d1 = min(date1, date2)
    d2 = max(date1, date2)
    dy = d2.year - d1.year
    dm = d2.month - d1.month
    return dy * 12 + dm + 1


# 函数：整理流量报表
def sort_flow(fs):
    uncertain = 0

    # 提取最早时间
    month_start = min(fs['StartDate'])
    month_start = Timestamp(year=month_start.year, month=month_start.month, day=1)
    month_end = Timestamp(year=month_start.year, month=month_start.month, day=month_start.daysinmonth)

    # 循环递推
    today = Timestamp.now()
    while month_end <= today:
        in_cover = fs[(fs['StartDate'] <= month_start) & (fs['EndDate'] >= month_end)]  # 筛选覆盖了本期的报表
        fs = fs[(fs['StartDate'] >= month_end) | (fs['EndDate'] <= month_start)]  # 筛选未覆盖本期的报表
        if len(in_cover) > 0:
            at_cover = in_cover[in_cover['EndDate'] == min(in_cover['EndDate'])]  # 筛选最小覆盖报表
            over_cover = in_cover[in_cover['EndDate'] > min(in_cover['EndDate'])]  # 非最小覆盖报表

            # 对最小覆盖报表提取单月值
            average_month_data = {}
            single_month_data = {}
            rest_month_data = {}
            period_start = at_cover['StartDate'].iloc[0]
            period_end = at_cover['EndDate'].iloc[0]
            at_cover_month = count_months(period_start, period_end)
            for acc in at_cover.columns:
                if acc not in ['StartDate', 'EndDate']:
                    average_month_data[acc] = np.average(at_cover[acc])
                    single_month_data[acc] = average_month_data[acc] / at_cover_month
                    rest_month_data[acc] = average_month_data[acc] - single_month_data[acc]

            # 创建第一个月的报表
            single_month_data['StartDate'] = month_start
            single_month_data['EndDate'] = month_end
            single_month = DataFrame(single_month_data, index=['s'])
            fs = fs.append(single_month, sort=False)

            # 创建剩余月份的报表
            rest_month_data['StartDate'] = month_end + Timedelta(days=1)
            rest_month_data['EndDate'] = period_end
            rest_month_data = DataFrame(rest_month_data, index=['m'])
            fs.append(rest_month_data, sort=False)

            # 对非最小覆盖报表扣减值
            if len(over_cover) > 0:
                for acc in over_cover.columns:
                    if acc not in ['StartDate', 'EndDate']:
                        over_cover.loc[:, acc] -= average_month_data[acc]
                over_cover.loc[:, 'StartDate'] = period_end + Timedelta(days=1)
                fs = fs.append(over_cover, sort=False)
        # 超出覆盖的月份按最新月份等推
        elif len(in_cover) == 0:
            hypo_data = fs[fs['EndDate'] < month_start]
            hypo_data = hypo_data[hypo_data['EndDate'] == max(hypo_data['EndDate'])]
            hypo_data.loc[:, 'StartDate'] = month_start
            hypo_data.loc[:, 'EndDate'] = month_end
            fs = fs.append(hypo_data, sort=False)
            uncertain += 1

        # 把报告期向后推一个月
        month_start += Timedelta(days=month_start.days_in_month)
        month_end += Timedelta(days=month_start.days_in_month)

    ttm_end = max(fs['EndDate'])
    yfs = {}
    while ttm_end > min(fs['StartDate']):
        ttm_start = Timestamp(year=ttm_end.year - 1, month=ttm_end.month + 1, day=1)
        ttm_fs = fs[(fs['EndDate'] <= ttm_end) & (fs['StartDate'] >= ttm_start)]
        if len(ttm_fs) < 12:
            break
        yfs[ttm_end] = {'StartDate': ttm_start, 'EndDate': ttm_end}
        for acc in ttm_fs.columns:
            if acc not in ['StartDate', 'EndDate']:
                yfs[ttm_end][acc] = ttm_fs[acc].sum()
        ttm_end = ttm_start - Timedelta(days=1)

    yfs = DataFrame(yfs).T
    yfs.sort_index(axis=0, ascending=True)
    return yfs, uncertain


# 函数：整理存量报表
def sort_bal(fs, dates: list):
    uncertain = 0
    yfs = {}

    for inter_date in dates:
        ref_fs = DataFrame()

        # 找更早和更晚的报表
        equal_fs = fs[fs['EndDate'] == inter_date]
        early_fs = fs[fs['EndDate'] < inter_date]
        late_fs = fs[fs['EndDate'] > inter_date]
        if len(equal_fs) > 0:
            ref_fs = ref_fs.append(equal_fs)
        elif len(early_fs) == 0:
            ref_fs = ref_fs.append(fs[fs['EndDate'] == min(fs['EndDate'])])
            uncertain += count_months(inter_date + Timedelta(days=1), ref_fs['EndDate'].iloc[0])
        elif len(late_fs) == 0:
            ref_fs = ref_fs.append(fs[fs['EndDate'] == max(fs['EndDate'])])
            uncertain += count_months(ref_fs['EndDate'].iloc[0] + Timedelta(days=1), inter_date)
        else:
            # 选取最近的前后两期报表
            ref1 = early_fs[early_fs['EndDate'] == max(early_fs['EndDate'])]
            ref2 = late_fs[late_fs['EndDate'] == min(late_fs['EndDate'])]

            # 求权重
            sum_weight = ref2['EndDate'].iloc[0] - ref1['EndDate'].iloc[0]
            w1 = (ref2['EndDate'].iloc[0] - inter_date) / sum_weight
            w2 = (inter_date - ref1['EndDate'].iloc[0]) / sum_weight

            wa_fs = {'EndDate': inter_date}
            for acc in fs.columns:
                if acc not in ['EndDate']:
                    wa_fs[acc] = np.average(ref1[acc]) * w1 + np.average(ref2[acc]) * w2
            ref_fs = DataFrame(wa_fs, index=['x'])

        # 将参考表平均作为当期报表
        inter_fs = {'EndDate': inter_date}
        for acc in ref_fs.columns:
            if acc not in ['EndDate']:
                inter_fs[acc] = np.average(ref_fs[acc])
        yfs[inter_date] = inter_fs

    yfs = DataFrame(yfs).T
    yfs.sort_index(axis=0, ascending=True)
    return yfs, uncertain


# 函数：提取数据
# 从DataFrame类型的报表，提取一组数据，若为空则返回None
def draw(data_sheet, acc_list: list, year=None, default_data=None):
    data = []
    if type(data_sheet) is DataFrame:
        if year in data_sheet.columns:
            for acc in acc_list:
                if acc in data_sheet.index:
                    data.append(data_sheet.loc[acc, year])
                else:
                    data.append(default_data)
        elif year in data_sheet.index:
            for acc in acc_list:
                if acc in data_sheet.columns:
                    data.append(data_sheet.loc[year, acc])
                else:
                    data.append(default_data)
        else:
            print('Can\'t find', year, 'in DataFrame axis!')
            return None
    elif type(data_sheet) is dict:
        for acc in acc_list:
            if acc in data_sheet.keys():
                data.append(data_sheet[acc])
            else:
                data.append(default_data)
    return data


# 类：财务报表
class FS(object):

    def __init__(self, report_date):
        self.report_date = report_date

    def report(self, table_name: str = 'FS', digit: int = Config.DIGIT):
        my_report = dict()
        if table_name == 'DATA':
            my_report = self.data
        elif table_name == 'DER':
            my_report = self.derivative
        elif table_name == 'RATE':
            my_report = self.ratio
        report = DataFrame(my_report, index=[self.report_date]).T
        return round(report, digit)


# 子类：Lite版存量报表（继承自 类：财务报表）
class BalLite(FS):

    def __init__(self, bal):
        report_date = Timestamp.now().date()

        if type(bal) is DataFrame:
            data_df = bal[bal['EndDate'] == max(bal['EndDate'])]
            last_year_data = data_df.iloc[0].to_dict()
            report_date = last_year_data['EndDate']

            # 依次提取0.货币资金、1.应收账款、2.存货、3.资产总计、4.短期借款、5.应付账款、6.负债合计、7.股本
            acc_list = ['e0001', 'e0022', 'e0031', 'e0s', 'e1001', 'e1022', 'e1s', 'e2001']
            cash, ar, inv, ta, debt, ap, tl, share = draw(data_sheet=last_year_data, acc_list=acc_list, default_data=0)

            self.data = {'Cash': cash,  # 现金
                         'AR': ar,  # 应收账款
                         'Inv': inv,  # 存货
                         'OA': ta - cash - ar - inv,  # 其他资产
                         'TA': ta,  # 资产总计
                         'Debt': debt,  # 借款
                         'AP': ap,  # 应付账款
                         'OL': tl - debt - ap,  # 其他负债
                         'TL': tl,  # 负债合计
                         'Share': share,  # 股本
                         'RE': ta - tl - share,  # 留存收益
                         'SE': ta - tl,  # 所有者权益合计
                         'LE': ta}  # 负债和所有者权益合计

        elif type(bal) is dict:
            self.data = bal
            report_date = bal['EndDate']

        FS.__init__(self, report_date=report_date)


# 子类：Lite版资本成本（继承自 类：财务报表）
class CCLite(FS):

    def __init__(self, bal):
        report_date = Timestamp.now().date()

        if type(bal) is DataFrame:
            data_df = bal[bal['EndDate'] == max(bal['EndDate'])]
            last_year_data = data_df.iloc[0].to_dict()
            report_date = last_year_data['EndDate']

            # 依次提取0.平均借款利率、1.适用的所得税率
            acc_list = ['e9901', 'e9932']
            ir, tr = draw(data_sheet=last_year_data, acc_list=acc_list)

            if ir is None:
                ir = Config.DEFAULT_INTEREST_RATE

            if tr is None:
                tr = Config.DEFAULT_INCOME_TAX_RATE

            self.data = {'IR': ir,  # 借款利率
                         'TR': tr}  # 公司所得税率

        elif type(bal) is dict:
            self.data = bal
            report_date = bal['EndDate']

        FS.__init__(self, report_date=report_date)


# 子类：Lite版流量报表（继承自 类：财务报表）
class FlowLite(FS):

    def __init__(self, flow, bs=None, cc=None):
        report_date = Timestamp.now().date()

        if type(flow) is DataFrame:
            data_df = flow[flow['EndDate'] == max(flow['EndDate'])]
            last_year_data = data_df.iloc[0].to_dict()
            report_date = last_year_data['EndDate']
            self.period_start = last_year_data['StartDate']

            # 依次提取0.营业总收入、1.营业成本、2.所得税费用、3.净利润
            acc_list = ['e31', 'e3201', 'e35', 'e35s1']
            sales, cogs, tax, profit = draw(last_year_data, acc_list, default_data=0)

            # 初始化资金成本
            if (cc is not None) and (cc.data['IR'] is not None):
                ir = cc.data['IR']
            else:
                ir = Config.DEFAULT_INTEREST_RATE

            if bs is None:
                interest, = draw(last_year_data, ['e6501'], report_date, 0)
            else:
                interest = -bs.data['Debt'] * ir

            self.data = {'Sales': sales,
                         'COGS': cogs,
                         'GP': sales + cogs,
                         'SGA': profit - sales - cogs - tax - interest,
                         'EBIT': profit - tax - interest,
                         'Int': interest,
                         'EBT': profit - tax,
                         'Tax': tax,
                         'NP': profit}

        elif type(flow) is dict:
            self.data = flow
            self.period_start = flow['StartDate']
            report_date = flow['EndDate']

        FS.__init__(self, report_date=report_date)


# 子类：Lite版财务报表（继承自 类：财务报表）
class FSLite(FS):

    def __init__(self, bal: BalLite, flow: FlowLite, cot: list=None):
        report_date = bal.report_date
        FS.__init__(self, report_date=report_date)
        self.data = bal.data
        self.data.update(flow.data)
        if cot is None:
            self.cot = [0] * Config.MAX_COT_YEAR
        else:
            self.cot = cot
