from Tool.Util import Treat, WA
from Config.Rule import Laws
from scipy.stats import norm, lognorm
from scipy.integrate import quad
from math import log, sqrt, exp, pow, pi
from numpy import median, inf, mean

# import sympy


__all__ = ['Val', 'ValMini']


class Val(Treat):
    """
    期权估值法是主要考量波动性的估值方法
    """

    def __init__(self, fs, peer_ratio, hypo):
        self.__unpack(fs, peer_ratio, hypo)

    def __unpack(self, fs, peer_ratio, hypo):
        self.dgt = int(hypo['dgt'])

        rf, lrp, srp, crp, prp, sprp = hypo.get_value(['rf', 'lrp', 'srp', 'crp', 'prp', 'sprp'])
        ko = lrp + srp + crp + prp + sprp

        dic, tr, kd = hypo.get_value(['dic', 'tr', 'kd'])

        if 'ke' in hypo:
            ke = hypo['ke']
        else:
            mrp, ub = hypo.get_value(['mrp', 'ub'])
            de = dic / (1 - dic)
            beta = ub * (1 + de * (1 - tr))
            ke = rf + beta * mrp + ko

        self.wacc = dic * kd * (1 - tr) + (1 - dic) * ke
        self.ke = ke
        self.kd = kd
        self.ub = hypo['ub']
        self.rf = rf

        try:
            capex = -fs['capex']
        except KeyError:
            capex = 0
        optn = hypo['optn']

        self.rev = fs['rev']
        if 'optn-cr' in optn:
            self.cr = optn['optn-cr']
        else:
            self.cr = 1 - (fs['np'] - fs['ie'] * (1 - Laws.int_tr) - capex) / fs['rev']
        self.std = self.__wstd('cr', peer_ratio.loc[:, ['cr', 'wt']], optn['optn-rate'])
        self.period = hypo['years']
        self.rg_list, self.pgr = hypo.get_value(['rg', 'pgr'])

        if type(self.rg_list) is list:
            rg = [log(1 + r) for r in self.rg_list]
            rg = mean(rg)
        else:
            rg = log(1 + self.rg_list)
        self.rg = rg
        self.dev = optn['optn-dev']
        self.last = optn['optn-last']
        self.ta, self.tl, self.ap = fs['ta'], fs['tl'], fs['ap']
        self.dic = hypo['dic']
        self.arg = peer_ratio.eval('wt * rg').sum() / peer_ratio['wt'].sum()

    # @logs
    def __rev_cost_opt(self):
        """
        这个方法将未来每年的收入作为资产价格，将每年的成本作为执行价格，计算期权价值（现值合计）
        :return:
        """
        val_dict = {}
        dev_dict = {'base': 0, 'optm': -self.dev, 'pess': self.dev}
        for case in ['base', 'optm', 'pess']:
            val = self.__binary_tree(self.rev, self.rg_list, self.pgr, self.cr, self.std, self.wacc, dev_dict[case],
                                     self.last, depth=self.period)
            val_dict[case] = round(val + self.ta - self.tl, self.dgt)
        val = val_dict['base']
        detail = {'depth': self.period,
                  'pgr': round(self.pgr, self.dgt + 2),
                  'cr': round(self.cr, self.dgt + 2),
                  'std': round(self.std, self.dgt + 2),
                  'last': self.last,
                  'wt': 2,
                  }
        detail.update(val_dict)
        return val, detail

    def __binary_tree(self, rev, rg, pgr, cr, std, r, case, last, depth: int = 5):
        """
        这个方法帮助收入/成本期权构建一个可迭代的二叉树
        :param rev:
        :param rg:
        :param pgr:
        :param cr:
        :param std:
        :param r:
        :param case:
        :param last:
        :param depth:
        :return:
        """
        irg = [r for r in rg]
        if len(irg) > 0:
            rev *= (1 + irg.pop(0))
        else:
            rev *= (1 + pgr)
        dist = lognorm(s=std, loc=0, scale=cr + case)  # 用对数正态分布作为成本率的分布

        survival = dist.cdf(1)

        val_add = quad(lambda x: (1 - x) * rev * dist.pdf(x), 0, 1)[0]

        if depth >= 1:
            future = self.__binary_tree(rev, irg, pgr, cr, std, r, case, last, depth - 1)
            val = (val_add + future) * survival / (1 + r)
        else:
            val = val_add * survival / (1 + r)
            val *= (1 + 0.95 * (1 + pgr) / (r - pgr))
        return val

    # @logs
    # def __ast_lia_opt(self):
    #     """
    #     资产/负债期权是常规的BSM模型的衍生，强调了资产的增值和负债的成本。
    #     :return:
    #     """
    #     s, x = self.ta - self.ap, self.tl - self.ap  # 剔除无息债的资产和负债
    #     g, sigma, kd, ke = self.pgr, self.std, self.kd, self.ke  # 增长率、波动率、带息债成本、股权要求回报率
    #     dgt = self.dgt
    #
    #     # 指数化
    #     g = log(1 + g)
    #     sigma = log(1 + sigma)
    #     kd = log(1 + kd)
    #     ke = log(1 + ke)
    #
    #     # 优化变换以保护l为0的情况
    #     tar_x = s * self.dic
    #     optm_x = (1 - pow(x / s, 2)) * tar_x + pow(x / s, 2) * x
    #     optm_s = s + optm_x - x
    #     status = log(optm_s / optm_x)
    #
    #     # 变量存档
    #     detail = {'oast': round(optm_s, dgt),
    #               'olia': round(optm_s, dgt),
    #               'pgr': round(g, dgt + 2),
    #               'sigma': round(sigma, dgt + 2),
    #               'kd': round(kd, dgt + 2),
    #               'ke': round(ke, dgt + 2),
    #               't': {},
    #               'wt': 1}
    #
    #     case_dict = {'base': self.last, 'optm': 2 * self.last - 1, 'pess': 1}
    #     val_dict = {}
    #     for case in case_dict:
    #         t = case_dict[case]
    #         nd1 = norm().cdf((status + (kd + g + pow(sigma, 2)) * t) / (sigma * sqrt(t)))
    #         nd2 = norm().cdf((status + (kd - pow(sigma, 2)) * t) / (sigma * sqrt(t)))
    #         val = optm_s * exp(g * t) * nd1 - optm_x * exp(-kd * t) * nd2
    #         val_dict[case] = round(val, self.dgt)
    #         detail['t'][case] = t
    #     val = val_dict['base']
    #     detail.update(val_dict)
    #     return val, detail

    def __ast_lia_opt(self):
        """
        资产负债期权，资产面值服从伊藤过程
        :return:
        """
        a0 = self.ta
        l0 = self.tl

        t = self.period
        rf = log(1 + self.rf)
        ke = log(1 + self.ke)

        pgr = log(1 + self.pgr)
        arg = log(1 + self.arg)

        min_rg = min(self.rg, arg, pgr)
        median_rg = median([self.rg, arg, pgr])
        max_rg = max(self.rg, arg, pgr)

        median_s = log(1 + self.ub * 0.3)
        min_s = abs(median_s * min_rg / median_rg)

        max_s = abs(median_s * max_rg / median_rg)

        # x = sympy.Symbol('x')

        def min_val_(x_):
            # 退出年资产价值分布
            a = exp(log(a0) + (min_rg - pow(min_s, 2) / 2) * t +
                    median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(min_s, 2)))
            return max(a - l0 * exp(rf * t), 0) * exp(-ke * t)

        min_val = quad(min_val_, -5, 5)[0]
        min_val = round(min_val, self.dgt)

        def median_val_(x_):
            # 退出年资产价值分布
            a = exp(log(a0) + (median_rg - pow(median_s, 2) / 2) * t +
                    median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(median_s, 2)))
            return max(a - l0 * exp(rf * t), 0) * exp(-ke * t)

        median_val = quad(median_val_, -5, 5)[0]
        median_val = round(median_val, self.dgt)

        def max_val_(x_):
            # 退出年资产价值分布
            a = exp(log(a0) + (max_rg - pow(max_s, 2) / 2) * t +
                    median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(max_s, 2)))
            return max(a - l0 * exp(rf * t), 0) * exp(-ke * t)

        max_val = quad(max_val_, -5, 5)[0]
        max_val = round(max_val, self.dgt)

        min_val, median_val, max_val = min(min_val, median_val, max_val), median([min_val, median_val, max_val]), max(min_val, median_val, max_val)

        detail = {
            'pess': min_val,
            'base': median_val,
            'optm': max_val,
            'pgr': median_rg,
            'sigma': median_s,
            'period': t,
            'wt': 1
        }
        return median_val, detail

    # @logs
    def get(self):
        detail = {}
        wa = WA('base', 'optm', 'pess')

        # 收入/成本期权
        # rco_val, rco_detail = self.__rev_cost_opt()
        # wa.add(rco_detail['wt'], rco_val, rco_detail['optm'], rco_detail['pess'])
        # detail['rco'] = rco_detail

        # 资产/负债期权
        alo_val, alo_detail = self.__ast_lia_opt()
        wa.add(alo_detail['wt'], alo_val, alo_detail['optm'], alo_detail['pess'])
        detail['alo'] = alo_detail

        wa.cal()

        detail.update(wa)
        detail = self.round(detail)
        return detail['base'], detail

    @staticmethod
    # @logs
    def __wstd(name, data, rate):
        wts = data['wt'].sum()
        wa = data.eval(f'{name} * wt').sum() / wts
        wvar = data.eval(f'wt * ({name} - @wa) ** 2').sum() / wts / rate
        return sqrt(wvar)


class ValMini(Treat):
    def __init__(self, fs, rg_list, npm_list, wacc, bottom):
        self.__unpack(fs)
        self.rg = rg_list
        self.cr = [1 - npm for npm in npm_list]
        self.wacc = wacc
        self.sigma = 0.05
        self.na = bottom
        self.detail = dict(sigma=self.sigma)
        self.die_prob = 0

    def __unpack(self, fs):
        self.fs = fs
        self.fs['tc'] = fs['rev'] - fs['np']

    # @logs
    def __rev_cost_opt(self):
        from Algorithm.GuessFS import guess_na
        """
        这个方法将未来每年的收入作为资产价格，将每年的成本作为执行价格，计算期权价值（现值合计）
        :return:
        """
        from copy import deepcopy
        val = []

        for case in [0.03, 0, -0.03]:
            print('case', case)
            mva = self.__binary_tree(deepcopy(self.fs['rev']), deepcopy(self.rg), deepcopy(self.cr), self.wacc, case)
            try:
                if mva <= 1:
                    val.append(0)
                else:
                    val.append(mva + self.na)
            except Exception as err:
                print(err)
                val.append(0)
        return tuple(val)

    def __binary_tree(self, rev, rg_list, cr_list, r, case, depth: int = 5):
        """
        这个方法帮助收入/成本期权构建一个可迭代的二叉树
        :param rev:
        :param rg_list:
        :param cr_list:
        :param r:
        :param case:
        :param depth:
        :return:
        """

        if len(rg_list) > 1:
            rev *= (1 + rg_list.pop(0))
        else:
            rev *= (1 + 0.01)

        if len(cr_list) > 1:
            cr = cr_list.pop(0)
        else:
            cr = cr_list[0]

        dist = lognorm(s=self.sigma, loc=0, scale=cr + case)
        survival = dist.cdf(1)  # 正常存活的概率
        self.die_prob = max(self.die_prob, 1 - survival)

        val_add = quad(lambda x: (1 - x) * rev * dist.pdf(x), 0, 1)[0]
        # print('成本率=', cr+case, '收入=', rev, '盈利概率=', survival, '增加值=', val_add)

        if depth >= 1:
            future = self.__binary_tree(rev, rg_list, cr_list, r, case, depth - 1)
            val = (val_add + future) * survival / (1 + r)
        else:
            val = val_add / (1 + r) * survival  # 最后一期现金流
            val *= (1 + 0.95 * (1 + 0.01) / (r - 0.01))  # 加上未来永续现金流
        return val

    # @logs
    def get(self):
        self.detail['die_prob'] = self.die_prob
        vals = self.__rev_cost_opt()
        # print(vals)
        return vals, self.detail
