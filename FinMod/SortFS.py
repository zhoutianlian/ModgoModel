from calendar import monthrange
from FinMod.FS import *
from Hypothesis.Basement import Hypo
from Report.Log import logger
from pandas import DataFrame as Df
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime, timedelta
from Tool.Util import month_coverage, month_start, month_end


__all__ = ['sort_fs']


def sort_fs(bal_data, flow_data):
    """
    整理财务数据
    :param bal_data:
    :param flow_data:
    :return:
    """
    sorted_bal = sort_bal(bal_data)
    sorted_flow = sort_flow(flow_data)
    # print(sorted_flow)

    # 套用报表类
    years = sorted_bal.loc[:, 'date'].tolist()
    years.sort(reverse=False)

    # 将成本项改为负值
    for acc in ['e3201', 'e321201', 'e321202', 'e321301', 'e35']:
        sorted_flow[acc] *= -1

    # 检修
    # print('整理后的流量表')
    # print(sorted_flow)

    fs = FinStm()
    for year in years:
        bs_df = sorted_bal[sorted_bal['date'] == year]
        bs = BS(bs_df.iloc[0].to_dict())
        ps_df = sorted_flow[sorted_flow['date'] == year]
        if len(ps_df) > 0:
            ps = PS(ps_df.iloc[0].to_dict())
            fs.add(bs, ps)
        else:
            fs.add(bs)

    return fs


def sort_bal(bal: Df):
    logger(0, '整理资产负债表')
    trace = Hypo()['trace']
    cpt_bal = deepcopy(bal)
    acc_list = cpt_bal.columns.tolist()
    for not_acc in ['_id', 'date']:
        acc_list.remove(not_acc)

    # 替换数据类型
    cpt_bal.fillna(0)
    for row, data in cpt_bal.iterrows():
        ending = str(int(data['date']))
        year, month = ending[:4], ending[4:6]
        year, month = int(year), int(month)
        day = monthrange(year, month)[1]
        cpt_bal.loc[row, 'date'] = datetime(year=year, month=month, day=day)

        _id = data['_id']
        cpt_bal.loc[row, '_id'] = _id

    # 删除重复报表
    repeat_list = []
    for row, data in cpt_bal.iterrows():
        repeat = cpt_bal[(cpt_bal['date'] == data['date']) & (cpt_bal['_id'] > data['_id'])]
        if len(repeat) > 0:
            repeat_list.append(data['_id'])
    cpt_bal = cpt_bal[~cpt_bal['_id'].isin(repeat_list)]
    cpt_bal.drop(['_id'], axis=1, inplace=True)

    # 找到每个应有报表日期最近的报表并用插值法获取
    today = month_start(datetime.now())
    end = datetime(year=today.year - trace, month=today.month, day=1) + timedelta(days=-1)
    yearly_fs = []
    while end < today:
        exact = cpt_bal[cpt_bal['date'] == end]
        # 正好存在此报表的情况
        if len(exact) > 0:
            exact = exact.iloc[0].to_dict()
            yearly_fs.append(exact)
        else:
            near_early = cpt_bal[cpt_bal['date'] < end]
            near_late = cpt_bal[cpt_bal['date'] > end]
            # 之前没有报表的情况
            if len(near_early) == 0 and len(near_late) > 0:
                near_late = near_late[near_late['date'] == min(near_late['date'])].iloc[0]
                near_late = near_late.to_dict()
                near_late['date'] = end
                yearly_fs.append(near_late)
            # 之后没有报表的情况
            elif len(near_early) > 0 and len(near_late) == 0:
                near_early = near_early[near_early['date'] == max(near_early['date'])].iloc[0]
                near_early = near_early.to_dict()
                near_early['date'] = end
                yearly_fs.append(near_early)
            # 前后都有报表的情况
            else:
                near_early = near_early[near_early['date'] == max(near_early['date'])].iloc[0]
                near_early = near_early.to_dict()
                near_late = near_late[near_late['date'] == min(near_late['date'])].iloc[0]
                near_late = near_late.to_dict()
                prior = month_coverage(near_early['date'] + timedelta(days=1), end)
                follow = month_coverage(end + timedelta(days=1), near_late['date'])
                wt_prior = prior / (prior + follow)
                wt_follow = follow / (prior + follow)
                year_dict = {'date': end}
                for acc in acc_list:
                    year_dict[acc] = near_early[acc] * wt_prior + near_late[acc] * wt_follow
                yearly_fs.append(year_dict)
        start = end + timedelta(days=1)
        next_start = datetime(year=start.year + 1, month=start.month, day=1)
        end = next_start + timedelta(days=-1)

    return round(Df(yearly_fs), 2)


def sort_flow(flow: Df):
    logger(0, '整理利润表')
    trace = Hypo()['trace']
    cpt_flow = deepcopy(flow)
    acc_list = cpt_flow.columns.tolist()
    for not_acc in ['_id', 'start', 'date']:
        acc_list.remove(not_acc)
    if "_class" in acc_list:
        acc_list.remove("_class")

    # 替换数据类型
    cpt_flow.fillna(0)
    for row, data in cpt_flow.iterrows():
        starting = str(int(data['start']))
        year, month = starting[:4], starting[4:6]
        year, month = int(year), int(month)
        cpt_flow.loc[row, 'start'] = datetime(year=year, month=month, day=1)

        ending = str(int(data['date']))
        year, month = ending[:4], ending[4:6]
        year, month = int(year), int(month)
        day = monthrange(year, month)[1]
        cpt_flow.loc[row, 'date'] = datetime(year=year, month=month, day=day)

        _id = data['_id']
        cpt_flow.loc[row, '_id'] = _id

    # 去除报告期重复的旧报表，并按开始日期排序
    repeat_list = []
    for row, data in cpt_flow.iterrows():
        repeat = cpt_flow[(cpt_flow['date'] == data['date']) &
                          (cpt_flow['start'] == data['start']) &
                          (cpt_flow['_id'] > data['_id'])]
        if len(repeat) > 0:
            repeat_list.append(data['_id'])

    cpt_flow = cpt_flow[~cpt_flow['_id'].isin(repeat_list)]
    cpt_flow = cpt_flow.drop(['_id'], axis=1)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # 对报表进行拆分
    done = False
    while not done:
        # 拆分开始时间一致的报表
        done = False
        while not done:
            cpt_flow, done = cut_head(cpt_flow, acc_list)

        # 拆分截止时间一致的报表
        done = False
        while not done:
            cpt_flow, done = cut_tail(cpt_flow, acc_list)

        # 拆分内包含报表，一旦做出调整立即重新执行之前的步骤
        cpt_flow, done = cut_heart(cpt_flow, acc_list)
        if not done:
            continue

        # 拆分交叠报表，一旦做出调整立即重新执行之前的步骤
        cpt_flow, done = cut_cross(cpt_flow, acc_list)
        if not done:
            continue

    # 生成单月份报表
    today = month_start(datetime.today())
    start = datetime(year=today.year - trace, month=today.month, day=1)
    monthly_fs = []
    while start < today:
        end = month_end(start)
        covered = cpt_flow[(cpt_flow['start'] <= start) & (cpt_flow['date'] >= end)]

        # 如果该月被报表覆盖，则参考该报表
        if len(covered) > 0:
            ref = covered.iloc[0].to_dict()
        # 如果该月未被任何报表覆盖，且列表中已有列表，则参考列表中最后一期报表
        elif len(monthly_fs) > 0:
            ref = monthly_fs[-1]
        # 如果该月未被任何报表覆盖，且列表中未有报表，则参考最早一期报表
        else:
            ref = cpt_flow[cpt_flow['start'] == min(cpt_flow['start'])].iloc[0].to_dict()

        month_count = month_coverage(ref['start'], ref['date'])
        month_dict = {'start': start, 'date': end}
        for acc in acc_list:
            a = ref[acc]
            if a == "":
                a = 0
            month_dict[acc] = a / month_count

        monthly_fs.append(month_dict)
        start = end + timedelta(days=1)
    monthly_fs = Df(monthly_fs)
    monthly_fs.sort_values(by='start', ascending=False, inplace=True)

    # 将每12个月合并为年数据
    yearly_fs = []
    yearly_end = max(monthly_fs['date'])

    while True:
        yearly_start = yearly_end + timedelta(days=1)
        yearly_start = datetime(year=yearly_start.year - 1, month=yearly_start.month, day=1)
        year_month_fs = monthly_fs[(monthly_fs['start'] >= yearly_start) & (monthly_fs['date'] <= yearly_end)]
        if len(year_month_fs) < 12:
            break
        year_month_fs = year_month_fs.drop(['start', 'date'], axis=1)
        year_fs = year_month_fs.sum().to_dict()
        year_fs['date'] = yearly_end
        year_fs['start'] = yearly_start
        yearly_fs.append(year_fs)
        yearly_end = yearly_start + timedelta(days=-1)
    return round(Df(yearly_fs), 2)


def cut_head(df, acc_list):
    for row, data in df.iterrows():
        align = df[(df['start'] == data['start']) & (df['date'] < data['date'])]
        if len(align) > 0:
            long_align = align[align['date'] == max(align['date'])].iloc[0]
            for acc in acc_list:
                df.loc[row, acc] = data[acc] - long_align[acc]
            df.loc[row, 'start'] = long_align['date'] + timedelta(days=1)
            return df, False
    else:
        return df, True


def cut_tail(df, acc_list):
    for row, data in df.iterrows():
        align = df[(df['date'] == data['date']) & (df['start'] > data['start'])]
        if len(align) > 0:
            long_align = align[align['start'] == min(align['start'])].iloc[0]
            for acc in acc_list:
                df.loc[row, acc] = data[acc] - long_align[acc]
            df.loc[row, 'date'] = long_align['start'] + timedelta(days=-1)
            return df, False
    else:
        return df, True


def cut_heart(df, acc_list):
    for row, data in df.iterrows():
        include = df[(df['start'] > data['start']) & (df['date'] < data['date'])]
        if len(include) > 0:
            include.eval('lasting = date - start', inplace=True)
            include = include[include['lasting'] == max(include['lasting'])]
            long_include = include[include['start'] == min(include['start'])].iloc[0]
            prior_end = long_include['start'] + timedelta(days=-1)
            follow_start = long_include['date'] + timedelta(days=1)
            prior = month_coverage(data['start'], prior_end)
            follow = month_coverage(follow_start, data['date'])
            for acc in acc_list:
                df.loc[row, acc] = data[acc] - long_include[acc]
            df.loc[row, 'date'] = prior_end
            follow_dict = {'start': follow_start, 'date': data['date']}
            for acc in acc_list:
                follow_dict[acc] = df.loc[row, acc] / (prior + follow) * follow
                df.loc[row, acc] = df.loc[row, acc] - follow_dict[acc]
            follow_df = Df(follow_dict, index=[0])
            df = df.append(follow_df)
            return df, False
    else:
        return df, True


def cut_cross(df, acc_list):
    num = len(df)
    for row, data in df.iterrows():
        cross = df[(df['start'] > data['start']) & (df['start'] < data['date'])]
        if len(cross) > 0:
            short_cross = cross[cross['start'] == max(cross['start'])].iloc[0]
            prior_end = short_cross['start'] + timedelta(days=-1)
            follow_start = data['date'] + timedelta(days=1)
            prior = month_coverage(data['start'], prior_end)
            follow = month_coverage(follow_start, short_cross['date'])
            crossing = month_coverage(short_cross['start'], data['date'])
            cross_dict = {'start': short_cross['start'], 'date': data['date']}
            for acc in acc_list:
                data_guess = data[acc] / (prior + crossing) * crossing
                wt_data = crossing / (prior + crossing)
                short_guess = short_cross[acc] / (crossing + follow) * crossing
                wt_short = crossing / (crossing + follow)
                cross_dict[acc] = (data_guess * wt_data + short_guess * wt_short) / (wt_data + wt_short)
            cross_df = Df(cross_dict, index=[num])
            num += 1
            df = df.append(cross_df)
            return df, False
    else:
        return df, True
