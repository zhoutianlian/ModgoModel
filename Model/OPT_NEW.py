from math import log, sqrt, exp, pow, pi
from numpy import median, inf
import sympy

#
# class Val:
#     def __init__(self, fs, peer_ratio, hypo):
#         # 资本成本
#         self.dgt = int(hypo['dgt'])
#
#         lrp, srp, crp, prp, sprp = hypo.get(['lrp', 'srp', 'crp', 'prp', 'sprp'])
#         ko = lrp + srp + crp + prp + sprp
#
#         dic, tr, kd = hypo.get(['dic', 'tr', 'kd'])
#
#         if 'ke' in hypo:
#             ke = hypo['ke']
#         else:
#             rf, mrp, ub = hypo.get(['rf', 'mrp', 'ub'])
#             de = dic / (1 - dic)
#             beta = ub * (1 + de * (1 - tr))
#             ke = rf + beta * mrp + ko
#         self.ke = log(1 + ke)
#
#         # 其他
#         self.arg = log(1 + peer_ratio.eval('rg * wt').sum() / peer_ratio['wt'].sum())  # 行业平均增长率
#         self.rg = log(1 + hypo['rg'])
#         self.pgr = log(1 + hypo['pgr'])  # 公司增长率，永续增长率
#
#         self.acr = peer_ratio['cr']  # 行业平均成本率
#         self.cr = fs['cogs'] / fs['rev']  # 公司成本率
#         self.wt = peer_ratio['wt']
#         self.sigma = peer_ratio['ub'] * 0.3
#         self.year = hypo['year']
#         self.ta = fs['ta']
#         self.tl = fs['tl']
#         self.rf = log(1 + hypo['rf'])
#
#     def __ast_lia_opt(self):
#         """
#         资产负债期权，资产面值服从伊藤过程
#         :return:
#         """
#         pgr = self.pgr
#         a0 = self.ta
#         l0 = self.tl
#
#         t = self.year
#         rf = self.rf
#         ke = self.ke
#
#         min_rg = min(self.rg, self.arg, self.pgr)
#         median_rg = median([self.rg, self.arg, self.pgr])
#         max_rg = max(self.rg, self.arg, self.pgr)
#
#         median_s = self.sigma
#         min_s = abs(median_s * min_rg / median_rg)
#
#         max_s = abs(median_s * max_rg / median_rg)
#
#         x = sympy.Symbol('x')
#
#         def min_val_(x_):
#             # 退出年资产价值分布
#             a = exp(log(a0) + (min_rg - pow(min_s, 2) / 2) * t +
#                     median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(min_s, 2)))
#             return max(a - l0 * exp(rf * t), 0)
#         min_val = sympy.integrate(min_val_(x), (x, -inf, inf)) * exp(-ke * t)
#
#         def median_val_(x_):
#             # 退出年资产价值分布
#             a = exp(log(a0) + (median_rg - pow(median_s, 2) / 2) * t +
#                     median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(median_s, 2)))
#             return max(a - l0 * exp(rf * t), 0)
#         median_val = sympy.integrate(median_val_(x), (x, -inf, inf)) * exp(-ke * t)
#
#         def max_val_(x_):
#             # 退出年资产价值分布
#             a = exp(log(a0) + (max_rg - pow(max_s, 2) / 2) * t +
#                     median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(max_s, 2)))
#             return max(a - l0 * exp(rf * t), 0)
#         max_val = sympy.integrate(max_val_(x), (x, -inf, inf)) * exp(-ke * t)
#
#         return min_val, median_val, max_val


a0

def min_val_(x_):
    # 退出年资产价值分布
    a = exp(log(a0) + (min_rg - pow(min_s, 2) / 2) * t +
            median_s * sqrt(t) / sqrt(2 * pi) * exp(-pow(x_, 2) / 2 / pow(min_s, 2)))
    return max(a - l0 * exp(rf * t), 0) * exp(-ke * t)
