# -*- coding: utf-8 -*-：
import re
from calendar import monthrange
from abc import abstractmethod
from datetime import datetime
from pandas import DataFrame as Df, Timestamp
from math import log10, floor, log, sqrt
from numpy import isnan
import platform
from Config.Exceptions import ExchangeError
from Config.Database import ConnDB as db_config

__all__ = ['month_start', 'month_end', 'month_coverage', 'bat_eval', 'WA', 'Treat', 'GenTreat', "merge_data",
           "merge_data_lite", "change_format", "volatility_accuracy", "change_data", "get_sigma", "send_mq"]


def list_drop_duplicate(origin_list):
    """
    在列表中去除重复值
    :param origin_list:
    :return:
    """
    output_list = []
    for item in origin_list:
        if item not in output_list:
            output_list.append(item)
    return output_list


def month_end(base_date: datetime):
    """
    这个方法用于计算某个日期所在月份的最后一天
    :param base_date:
    :return:
    """
    year = base_date.year
    month = base_date.month
    day = monthrange(year, month)[1]
    return datetime(year=year, month=month, day=day)


def month_start(base_date: datetime):
    """
    这个方法用于计算某个日期所在月份的第一天
    :param base_date:
    :return:
    """
    year = base_date.year
    month = base_date.month
    return datetime(year=year, month=month, day=1)


def month_coverage(start_date, end_date):
    """
    计算两个日期之间覆盖的月数
    :param start_date:
    :param end_date:
    :return:
    """
    year_diff = end_date.year - start_date.year
    month_diff = end_date.month - start_date.month
    return year_diff * 12 + month_diff + 1


def df_cal(df: Df, index1: str, index2: str, func, exclude: dict):
    value1 = df.loc[index1, :].to_dict()
    value2 = df.loc[index2, :].to_dict()
    value3 = {}
    for name in df.columns:
        if name not in exclude:
            value3[name] = func(value1[name], value2[name])
    value3.update(exclude)
    return Df(value3, index=[0])


def add(x1, x2):
    return x1 + x2


def sub(x1, x2):
    return x1 - x2


def sumproduct(df: Df, value: str, weight: str, bot: float = None, top: float = None):
    new_df = select_df(df, value, [weight], bot, top)
    if len(new_df) > 0:
        new_df['wa'] = new_df[value] * new_df[weight]
        return new_df['wa'].sum() / new_df[weight].sum()
    else:
        return None


def asym_dev(df: Df, value: str, mark: float, weight: str, dev_type: str = 'upper',
             bot: float = None, top: float = None):
    new_df = select_df(df, value, [weight], bot, top)
    if dev_type == 'upper':
        new_df = new_df[new_df[value] >= mark]
    elif dev_type == 'lower':
        new_df = new_df[new_df[value] <= mark]
    else:
        raise ValueError

    new_df['w_dev'] = pow(new_df[value] - mark, 2)
    var = sumproduct(new_df, 'w_dev', weight)
    return sqrt(var)


def select_df(df: Df, value_col: str, leave_cols: list, bot: float = None, top: float = None):
    leave_cols.append(value_col)
    new_df = df.loc[:, leave_cols]
    if bot is not None:
        new_df = new_df[new_df[value_col] > bot]
    if top is not None:
        new_df = new_df[new_df[value_col] < top]

    new_df.dropna()
    return new_df


def asym_range(df: Df, value: str, weight: str, bot: float = None, top: float = None):
    avg = sumproduct(df, value, weight, bot, top)
    top = avg + asym_dev(df, value, avg, weight, 'upper', bot, top)
    bot = avg - asym_dev(df, value, avg, weight, 'lower', bot, top)
    return bot, avg, top


def bat_eval(df: Df, *args, **kwargs):
    locals().update(kwargs)
    for expr in args:
        df.eval(expr, inplace=True)
    return df


class WA(dict):
    def __init__(self, *args):
        super().__init__()
        for key in args:
            self[key] = 0
        self.__length__ = len(args)
        self.__weight__ = 0

    def add(self, wt, *args):
        for key, value in zip(self, args):
            value = 0 if isnan(value) else value
            self[key] += wt * value
        self.__weight__ += wt

    def cal(self, dgt: int = None):
        if dgt is None:
            def eq(val, *args):
                return val
        else:
            eq = round

        for key in self:
            try:
                self[key] = eq(self[key] / self.__weight__, dgt)
            except ZeroDivisionError:
                continue

    def sum_wt(self):
        return self.__weight__


class Treat:
    dgt = 2

    def round(self, value, extra: int = 0):
        if value:
            if type(value) is list:
                vl = [self.round(item, extra) for item in value]
                return vl
            elif type(value) is tuple:
                vt = [self.round(item, extra) for item in value]
                return tuple(vt)
            elif type(value) is dict:
                vd = {}
                for name in value:
                    vd[name] = self.round(value[name], extra)
                return vd
            elif type(value) in [str, datetime, Timestamp]:
                return value
            else:
                try:
                    if value == 0 or isnan(value):
                        return value
                    elif abs(value) > 1:
                        return round(value, self.dgt + extra)
                    else:
                        mag = floor(log10(abs(value)))
                        return round(value, -mag + self.dgt + extra)
                except Exception as err:
                    print(err)
                    print(value)
                    print(type(value))
                    return value
        else:
            return value

    def mark(self, value, ref, level):
        dev = abs(value - ref) / level
        score = self.round(max(5 - dev, 0))
        return score

    @abstractmethod
    def __unpack(self, **kwargs):
        """
        这是处理类中的解包方法
        :param kwargs:
        :return:
        """
        raise NotImplemented

    @abstractmethod
    def get(self):
        """
        这是获得结果的方法
        :return:
        """
        raise NotImplemented

    @staticmethod
    def drop_abnormal(df, col, z=1, bottom=0):
        dataset = df.query(f'{col} > @bottom')[col]
        q1 = dataset.quantile(0.25)
        q3 = dataset.quantile(0.75)
        sigma = abs(q1 - q3) / 1.35
        median = dataset.median()
        dn = max(median - z * sigma, bottom)
        up = median + z * sigma
        return df.query(f'@dn < {col} < @up')


class GenTreat(Treat):
    def __init__(self, data, dgt):
        self.__data__ = data
        self.__dgt__ = dgt

    def __unpack(self):
        pass

    def get(self):
        return self.round(self.__data__)


def change_format(num_str):
    exchange = {"美元": 70000, "人民币": 10000, "日元": 660, "港币": 8932, "": 10000, "元": 10000, "港元": 8932,
                "元人民币": 10000, "欧元": 80000, "新加坡元": 50000}
    exchange_larger = {"人民币": 100000000, "美元": 700000000, "日元": 6600000, "港币": 89320000,
                       "港元": 89320000, "欧元": 800000000, "新加坡元": 500000000}
    if "万" in num_str:
        num_str = re.sub(u'[()（）]', '', num_str)
        [num, unit] = num_str.strip().split('万')
        if unit in exchange:
            num = float(num) * exchange[unit]
        else:
            print("货币单位未匹配，请更新代码配置")
            num = 10000
    elif "亿" in num_str:
        num_str = re.sub(u'[()（）]', '', num_str)
        [num, unit] = num_str.strip().split('亿')
        if unit in exchange_larger:
            num = float(num) * exchange_larger[unit]
        else:
            print("货币单位未匹配，请更新代码配置")
            num = 100000000
    else:
        try:
            num = float(num_str)
        except:
            num = 10000
    return num


def merge_data(com_data, tyc_data):
    indus = list(com_data["inputIndustry"].keys())[0]
    com_data["inputIndustry"] = indus
    if "regCapital" in tyc_data:
        reg = change_format(tyc_data["regCapital"])
        tyc_data["regCapital"] = reg
    if "actualCapital" in tyc_data:
        pic = change_format(tyc_data["actualCapital"])
        tyc_data["actualCapital"] = pic

    vid_data = {**com_data, **tyc_data}
    return vid_data


def merge_data_lite(com_data, tyc_data, vr_method):
    if "regCapital" in tyc_data:
        reg = change_format(tyc_data["regCapital"])
        tyc_data["regCapital"] = reg
    vid_data = {**com_data, **tyc_data, **vr_method}
    return vid_data


def change_data(data):
    date = data["estiblishTime"][0]
    reg = data["regCapital"][0]
    reg = change_format(reg)
    if type(date) is str:
        if "-" in date:
            date = datetime.strptime(date, "%Y-%m-%d")
        else:
            date = datetime.strptime(date, "%Y/%m/%d")
    else:
        date = datetime.fromtimestamp(date / 1000)
    return date, reg


def volatility_accuracy(res_before, res_now, year, s):

    g = 0.1
    # delta = 0.2
    # sigma = 1.96
    # g*T +- δ*(根号T)*sigma

    z = (log(res_now / res_before) - (g - (s ** 2) / 2) * year) / (s * sqrt(year))
    score = (-1.28 < z < 1.28) + (-1.65 < z < 1.65) + (-1.96 < z < 1.96) + (-2.58 < z < 2.58)
    return score


def get_sigma(year, value):
    # # 分配系数
    # a = 0.7
    # # 系数
    # A = 8
    # # 基数
    # s0 = 0.8
    # s = sqrt(year) ** (-a) * sqrt(value) ** (a - 1) * A * s0

    a = 0.7
    base_var = 64

    value_var = base_var * pow(0.5, log(value, 10))  # 估值每提高一个数量级，方差减半
    year_var = base_var * pow(0.5, year/2.5)  # 每经过2.5年，方差减半

    base_var = pow(0.05, 2)  # 基础波动率
    return sqrt(sqrt(pow(value_var, a) * pow(year_var, (1 -a))) + base_var)


def send_mq(eid):
    if platform.system().lower() == 'linux':
        from rocketmq.client import Producer, Message
        producer = Producer('PID-1')
        # producer.set_namesrv_domain('http://onsaddr-internet.aliyun.com/rocketmq/nsaddr4client-internet')
        # For ip and port name server address, use `set_namesrv_addr` method, for example:
        producer.set_namesrv_addr(db_config.mq)
        # producer.set_session_credentials('XXX', 'XXXX', 'ALIYUN') # No need to call this function if you don't use Aliyun.
        producer.start()

        msg = Message('enterprise-valuation')
        msg.set_keys('demo')
        msg.set_tags('demo')
        msg.set_body(str(eid))
        ret = producer.send_sync(msg)
        # print(ret.status, ret.msg_id, ret.offset)
        producer.shutdown()

