# -*- coding: utf-8 -*-：
from math import log10, sqrt, exp
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from numpy import median

from Tool.Util import Treat, bat_eval, WA

__all__ = ['Val']


class Val(Treat):
    __list__ = ['loan', 'ar', 'ap', 'inv', 'ppe']

    def __init__(self, fs, peer_fs, hypo):
        self.__unpack(fs, peer_fs, hypo)

    def __unpack(self, fs, peer_fs, hypo):
        self.__dgt__ = hypo['dgt']
        peer = bat_eval(peer_fs,
                        'na = ta - tl',
                        'mva = mv - na',
                        'wc = ar - ap',
                        'no = ta - tl - inv - ppe - wc + loan').dropna()

        self.__ys__ = peer['mva']
        self.__xs__ = peer.loc[:, self.__list__]
        self.__wt__ = peer['wt']
        self.__alpha__ = pow(peer['mv'].mean(), 2)

        self.__na__ = fs['na']
        self.__x__ = [fs['loan'], fs['ar'], fs['ap'], fs['inv'], fs['ppe']]
        self.__aba__ = hypo['astb']

        self.__ast_ridge__, self.__ast_lasso__, self.__ast_elast__ = hypo.get_value(
            ["aba_ridge", "aba_lasso", "aba_elast"])

    def __judg(self, test, model, wt=None):
        predict = model.predict([test])[0]
        coef = model.coef_
        coef_optm, coef_pess = self.__interval(coef)
        coef_dict = {key: value for key, value in zip(self.__list__, coef)}
        score = model.score(self.__xs__, self.__ys__) if wt is None else model.score(self.__xs__, self.__ys__, wt)
        model.coef_ = coef_optm
        optm_predict = model.predict([test])[0]

        model.coef_ = coef_pess
        pess_predict = model.predict([test])[0]

        return predict, coef_dict, score, optm_predict, pess_predict

    def __fit(self, model, wt=False):
        """
        该方法执行回归并输出结果
        :param model:
        :param wt:
        :return:
        """
        if wt:
            model.fit(self.__xs__, self.__ys__, self.__wt__)
            mva, coef_dict, r2, mva_optm, mva_pess = self.__judg(self.__x__, model, self.__wt__)
        else:
            model.fit(self.__xs__, self.__ys__,)
            mva, coef_dict, r2, mva_optm, mva_pess = self.__judg(self.__x__, model)
        detail = {'base': mva * exp(r2 - 1) + self.__na__,
                  'optm': mva_optm * exp(r2 - 1) + self.__na__,
                  'pess': mva_pess * exp(r2 - 1) + self.__na__,
                  'mva': mva,
                  'mva_optm': mva_optm,
                  'mva_pess': mva_pess,
                  'loga': log10(model.alpha_),
                  'r2': r2,
                  'coef': coef_dict,
                  'wt': r2 * 5 if r2 > 0 else -1,  # 正常回归时以R值*系数为权重，否则以-1为权重，代表方法无效
                  }

        return detail['base'], detail

    def __ridge(self):
        """
        岭回归
        :return:
        """
        model = RidgeCV(alphas=[k * self.__alpha__ for k in [0.1, 0.2, 0.5, 1, 2, 5, 10]], fit_intercept=False)
        return self.__fit(model, True)

    def __lasso(self):
        """
        Lasso回归
        :return:
        """
        model = LassoCV(alphas=[k * self.__alpha__ for k in [0.001, 0.01, 0.1, 1, 10]], fit_intercept=False)
        return self.__fit(model)

    def __elast(self):
        """
        弹性网回归
        :return:
        """
        model = ElasticNetCV(alphas=[k * self.__alpha__ for k in [0.001, 0.01, 0.1, 1, 10]],
                             l1_ratio=[0.1, 0.5, 0.7, 0.9, 0.95, 0.99], fit_intercept=False)

        val, detail = self.__fit(model)
        detail['l1r'] = model.l1_ratio_
        return val, detail

    def __interval(self, coef):
        """
        这个方法对回归系数进行轻微扰动，得到不同结果
        :param coef:
        :return:
        """
        optm_coef = coef + abs(coef) * self.__aba__['optm']
        pess_coef = coef + abs(coef) * self.__aba__['pess']
        return optm_coef, pess_coef

    def get(self):
        detail = {}
        wa = WA('base', 'optm', 'pess')

        for method, func in zip(('ridge', 'lasso', 'elast'), (self.__ridge, self.__lasso, self.__elast)):
            val, dtl = func()
            pess_val, base_val, optm_val = min(dtl['pess'], val, dtl['optm']), median(
                [dtl['pess'], val, dtl['optm']]), max(
                dtl['pess'], val, dtl['optm'])
            # wa.add(dtl['wt'], val, dtl['optm'], dtl['pess'])
            value = self.__getattribute__(f"__ast_{method}__")
            wt = value if value else dtl['wt']
            wa.add(wt, base_val, optm_val, pess_val)
            detail[method] = dtl

        wa.cal()
        detail.update(wa)
        detail = self.round(detail)
        detail['pess'], detail['base'], detail['optm'] = min(detail['pess'], detail['base'], detail['optm']), median(
            [detail['pess'], detail['base'], detail['optm']]), max(
            detail['pess'], detail['base'], detail['optm'])
        return detail['base'], detail
