from abc import abstractmethod
from Config.Accounts import BsNames as Bs, PsNames as Ps, CfNames as Cf, BmNames as Bm
from datetime import date, datetime, timedelta
from numpy import float64
from copy import deepcopy
from calendar import monthrange
from math import ceil
from pandas import DataFrame as Df


__all__ = ['FinStm', 'BS', 'PS', 'CF', 'BM']


class Stm(dict):
    """
    这是一个报表的父类
    """
    __name__ = '<Class.FinStm>'
    __names__ = None

    def __init__(self, data: dict):
        super().__init__()
        for name in data:
            if name in self.__names__.__dir__():
                value = data[name]
                value = float(value) if type(value) is float64 else value
                value = datetime(value.year, value.month, value.day, 0, 0) if type(value) is date else value
                self[self.__names__.__getattribute__(name)] = value
        self.__complete__()

    @abstractmethod
    def __complete__(self):
        """
        这是一个补充缺失数据的方法
        :return:
        """
        raise NotImplemented

    def __str__(self):
        string = '----------%s----------\n' % self.__name__
        string += '%-50s%50s\n' % ('<Account>', '<Data>')
        for key in self:
            value = self[key]
            if type(value) in [float, float64]:
                value = format(value, ',.2f')
            string += '%-50s%50s\n' % (key, value)
        string += '----------end----------\n'
        return string


class BS(Stm):
    """
    精简资产负债表
    """
    __name__ = 'Balance Sheet'
    __names__ = Bs()

    def __complete__(self):
        self['oa'] = self['ta'] - self['cash'] - self['ar'] - self['inv'] - self['ppe']
        self['ol'] = self['tl'] - self['loan'] - self['ap']
        self['na'] = self['ta'] - self['tl']
        self['re'] = self['na'] - self['share']


class PS(Stm):
    """
    精简利润表
    """
    __name__ = 'Income Statement'
    __names__ = Ps()

    def __complete__(self):
        self['gp'] = self['rev'] + self['cogs']
        self['tp'] = self['np'] - self['tax']
        self['op'] = self['tp'] - self['ie']
        self['opda'] = self['op'] - self['da']
        self['sga'] = self['opda'] - self['gp'] - self['rd']


class CF(Stm):
    """
    精简现金流量表
    """
    __name__ = 'Cash Flow Statement'
    __names__ = Cf()

    def __complete__(self):
        self['cfo'] = self['np'] + self['dap'] + self['inv_reduce'] + self['rec_reduce'] + self['pay_raise']
        self['cfi'] = self['capex']
        self['cff'] = self['nb'] + self['div']
        self['tcf'] = self['cfo'] + self['cfi'] + self['cff']


class BM(Stm):
    """
    商业模式报表
    """
    __name__ = 'Business Model'
    __names__ = Bm()

    def __complete__(self):
        pass


class FinStm(list):
    """
    这是一个报表集合的类
    """
    __start__ = None
    __survival__ = []
    __orig_ppe__ = []
    __orig_capex__ = []

    def add(self, bs: BS = None, ps: PS = None, cf: CF = None):
        if bs:
            fs = deepcopy(bs)
            fs.__name__ = 'Financial Statement'
        else:
            fs = dict()
        if ps:
            fs.update(ps)
        if cf:
            fs.update(cf)
        self.append(fs)

    def start(self):
        if self.__start__ is None:
            self.__start__ = len(self)
        else:
            return self.__start__

    def forecast(self, hypo_orig):
        """
        这个函数用于根据最新一期[-1]财报向后预测一期，将预测的报表添加到自己，并返回调整后的hypo
        :param hypo_orig:
        :return:
        """
        # 检修
        # print('预测')
        # print(self[-1])

        hypo = hypo_orig.get_copy()
        forecast_year = len(self) - self.__start__
        if forecast_year == 0:
            __survival__ = []
            __orig_ppe__ = []
            __orig_capex__ = []

        last = deepcopy(self[-1])
        year, month = last['date'].year + 1, last['date'].month
        day = monthrange(year=year, month=month)[1]
        new_date = datetime(year=year, month=month, day=day)
        since = last['date'] + timedelta(days=1)
        new = dict(date=new_date, since=since)

        new['rev'] = last['rev'] * (1 + hypo['rg'][forecast_year])
        new['ar'] = new['rev'] * hypo['dso'] / hypo['yds']
        new['rec_reduce'] = last['ar'] - new['ar']

        new['cogs'] = -new['rev'] * hypo['cm']
        new['ap'] = -new['cogs'] * hypo['dpo'] / hypo['yds']
        new['pay_raise'] = new['ap'] - last['ap']

        new['inv'] = -new['cogs'] * hypo['dsi'] / hypo['yds']
        new['inv_reduce'] = last['inv'] - new['inv']

        new['gp'] = new['rev'] + new['cogs']

        new['sga'] = -new['rev'] * hypo['sm']
        new['rd'] = -new['rev'] * hypo['rdr'] if hypo['rd'] is None else hypo['rd'][forecast_year]
        new['capex'] = -new['rev'] * hypo['capr']
        new['opda'] = new['gp'] + new['sga'] + new['rd']

        # print(new)
        # 调取固定资产和capex的原值
        if forecast_year == 0:
            self.__orig_ppe__ = [last['ppe'], last['ppe']]

        da_exp = 0
        # 对固定资产进行折旧
        if self.__orig_ppe__[1] > 0:
            orig_ppe_da = min(self.__orig_ppe__[0] / hypo['pda'], self.__orig_ppe__[1])
            self.__orig_ppe__[1] -= orig_ppe_da
            da_exp -= orig_ppe_da

        # 对以前的固定资产投资进行折旧
        if len(self.__orig_capex__) > 0:
            for year in range(len(self.__orig_capex__)):
                if self.__orig_capex__[year][1] > 0:
                    orig_capex_da = min(self.__orig_capex__[year][0] / hypo['cda'], self.__orig_capex__[year][1])
                    self.__orig_capex__[year][1] -= orig_capex_da
                    da_exp -= orig_capex_da

        # 对当期的固定资产进行折旧（按半年折旧）
        # print('hypo.cda', hypo['cda'])
        new_capex_da = min(-new['capex'] / max(hypo['cda'], 1) * 0.5, -new['capex'])
        da_exp -= new_capex_da
        new_capex_bv = -new['capex'] - new_capex_da
        self.__orig_capex__.append([-new['capex'], new_capex_bv])

        new['da'] = da_exp
        new['dap'] = -da_exp
        new['ppe'] = last['ppe'] - new['capex'] - new['dap']
        new['op'] = new['opda'] + new['da']

        # print(new)
        # 尝试预测受利息影响的其他数据
        try_gen = self.__trier__(new, hypo, forecast_year)
        try_gen.__next__()
        nb = 0.0 if hypo['nb'] is None else hypo['nb'][forecast_year]
        whether_div = True

        hypo['tt'] = int(hypo['tt'])
        for i in range(hypo['tt']):
            trial, shortfall = try_gen.send((nb, whether_div))
            if shortfall != 0:
                if trial['div'] < 0:
                    whether_div = False
                else:
                    nb += shortfall
                    if hypo['nb'] is not None:
                        nb = max(nb, hypo['nb'][forecast_year])
            else:
                new.update(trial)
                break
        # 预测失败
        else:
            new_hypo = hypo.advance()
            new_hypo['run'] = False
            return new_hypo

        # 预测成功
        trial['ta'] = trial['cash'] + trial['ar'] + trial['inv'] + trial['ppe'] + last['oa']
        trial['tl'] = trial['loan'] + trial['ap'] + last['ol']
        trial['share'] = last['share']
        new_bs = BS(trial)
        new_ps = PS(trial)
        new_cf = CF(trial)
        self.add(new_bs, new_ps, new_cf)
        accum = 1 if len(self.__survival__) == 0 else self.__survival__[-1]
        self.__survival__.append(accum * (1 - hypo['ybp']))
        new_hypo = hypo.advance()
        if trial['na'] < 0:
            new_hypo['insol'] -= 1
        if trial['np'] < 0:
            new_hypo['defi'] -= 1
        if new_hypo['insol'] * new_hypo['defi'] <= 0:
            new_hypo['run'] = False
        return new_hypo

    def __trier__(self, trial_dict, hypo, forecast_year):
        last = self[-1]
        trial = deepcopy(trial_dict)
        shortfall = max(hypo['lcash'], 1)
        optimize_dic = True
        whether_div = True

        while True:
            trial['nb'], whether_div = yield trial, shortfall
            trial['loan'] = last['loan'] + trial['nb']
            trial['ie'] = -(trial['loan'] + last['loan']) / 2 * hypo['kd'] + last['cash'] * hypo['ks'] * 0.5
            trial['tp'] = trial['op'] + trial['ie']
            trial['tax'] = -trial['tp'] * hypo['tr']
            trial['np'] = trial['tp'] + trial['tax']
            if trial['np'] > 0 and whether_div:
                trial['div'] = -trial['np'] * hypo['divr'] if hypo['div'] is None else hypo['div'][forecast_year]
            else:
                trial['div'] = -0.0
            trial['cfo'] = trial['np'] + trial['dap'] + trial['inv_reduce'] + trial['rec_reduce'] + trial['pay_raise']
            trial['cfi'] = trial['capex']
            trial['cff'] = trial['nb'] + trial['div']
            trial['tcf'] = trial['cfo'] + trial['cfi'] + trial['cff']
            trial['cash'] = last['cash'] + trial['tcf']
            trial['na'] = last['na'] + trial['np'] + trial['div']
            trial['ic'] = trial['na'] + trial['loan']

            if trial['ap'] > 0 and trial['cash'] / trial['ap'] < hypo['lcp']:
                shortfall = hypo['lcp'] * trial['ap'] - trial['cash']
                shortfall *= (1 + hypo['kd'] / 2)
                shortfall = ceil(shortfall)
            elif trial['ap'] == 0 and trial['cash'] < hypo['lcash']:
                shortfall = hypo['lcash'] - trial['cash']
                shortfall *= (1 + hypo['kd'] / 2)
                shortfall = ceil(shortfall)
            elif optimize_dic:
                shortfall = - hypo['frc'] * (trial['loan'] - trial['ic'] * hypo['dic'])
                shortfall = max(shortfall, -trial['loan'])
                optimize_dic = False
            else:
                shortfall = 0

    def get(self, acc_name):
        acc = {}
        for item in self:
            try:
                key = item['date']
                value = item[acc_name]
                acc[key] = value
            except KeyError:
                pass
        return acc

    def get_predict(self, acc_list: list, delay: int = 0):
        acc_df = []
        year = 1
        for fs in self[self.__start__ + delay:]:
            acc_dict = {'year': year}
            for acc in acc_list:
                acc_dict[acc] = fs[acc]
            acc_df.append(acc_dict)
            year += 1
        return Df(acc_df)

    def get_now(self, acc_list: list):
        acc_values = []
        fs = self[self.__start__ - 1]
        for acc in acc_list:
            acc_values.append(fs[acc])
        return tuple(acc_values)

    def get_survival(self):
        return self.__survival__

    def get_start(self):
        return self.__start__

    def get_copy(self):
        new_copy = FinStm()
        for item in self:
            new_copy.append(item)
        new_copy.__start__ = self.__start__
        for name in ['__survival__', '__orig_ppe__', '__orig_capex__']:
            new_copy.__setattr__(name, [])
        return new_copy

    def to_general(self):
        fs_list = []
        for item in self:
            fs = {}
            for name in item:
                fs[name] = item[name]
            fs_list.append(fs)
        return fs_list
