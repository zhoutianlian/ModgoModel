# -*- coding: utf-8 -*-：
from FinMod.FS import *
from Tool.Util import Treat
from Hypothesis.Basement import Hypo as Hp
from Tool.Util import bat_eval, WA
from Tool.Formats import merge_dict
from math import sqrt, log
import numpy as np


__all__ = ['Val', 'ValMini']


class Val(Treat):
    """
    这是一个dcf估值的类
    """
    __detail__ = False

    def __init__(self, fs: FinStm, hypo: Hp, delay: int = 0):
        self.__fs__ = fs
        self.__hypo__ = hypo
        self.__delay__ = delay
        self.__unpack(fs, hypo)

    def __unpack(self, fs, hypo):
        self.__dgt__ = int(hypo['dgt'])
        self.__optm__ = hypo['optm']
        self.__pess__ = hypo['pess']

        # 解包回报率
        rf, mrp, ub, dic, tr, kd = hypo.get_value(['rf', 'mrp', 'ub', 'dic', 'tr', 'kd'])
        lrp, srp, crp, prp, sprp = hypo.get_value(['lrp', 'srp', 'crp', 'prp', 'sprp'])
        ko = lrp + srp + crp + prp + sprp
        de = dic / (1 - dic)
        beta = ub * (1 + de * (1 - tr))
        ku = rf + ub * mrp + ko
        ke = rf + beta * mrp + ko if 'ke' not in hypo else hypo['ke']
        wacc = dic * kd * (1 - tr) + (1 - dic) * ke
        self.__ku__, self.__ke__, self.__kd__, self.__wacc__ = ku, ke, kd, wacc

        # 解包乘数
        self.__evop__, self.__pe__, self.__evic__, self.__pb__ = hypo.get_value(['evop', 'pe', 'evic', 'pb'])

        # 解包其他假设
        self.__pgr__, self.__roic__, self.__roe__ = hypo.get_value(['pgr', 'roic', 'roe'])
        self.__sc__, self.__ybp__, self.__blr__, self.__rbp__ = hypo.get_value(['sc', 'ybp', 'blr', 'rbp'])

        # 解包子模型权重
        self.__dcf_fcff__, self.__dcf_fcfe__, self.__dcf_eva__, self.__dcf_ae__, self.__dcf_apv__ = hypo.get_value(
            ['dcf_fcff', 'dcf_fcfe', 'dcf_eva', 'dcf_ae', 'dcf_apv'])

        # 公司自由现金流模型
        self.__dcf_fcff_pg__, self.__dcf_fcff_em__, self.__dcf_fcff_vd__ = hypo.get_value([
            'dcf_fcff_pg', 'dcf_fcff_em', 'dcf_fcff_vd'])

        # 股权自由现金流模型
        self.__dcf_fcfe_pg__, self.__dcf_fcfe_em__, self.__dcf_fcfe_vd__ = hypo.get_value([
            'dcf_fcfe_pg', 'dcf_fcfe_em', 'dcf_fcfe_vd'])


        # 获取预测数据
        cf = fs.get_predict(['rev', 'cfo', 'ie', 'capex', 'nb', 'op', 'np', 'na', 'loan'])
        self.__year__ = len(cf)
        cash, na, debt = fs.get_now(['cash', 'na', 'loan'])
        self.__na__ = na
        self.__ic__ = na + debt
        self.__nd__ = debt - cash
        survival = fs.get_survival()

        # 计算现金流
        cf = bat_eval(cf,
                      'fcff = cfo - ie * (1 - @tr) + capex',
                      'fcfe = cfo + capex + nb',
                      'ts = -ie * @tr',
                      'apv = fcff + ts',
                      'na0 = @na * (1 + @ke) ** (year - 1)',
                      'ae = np - na0 * @ke',
                      'ic0 = @ic * (1 + @wacc) ** (year - 1)',
                      'nopat = op * (1 - @tr)',
                      'eva = nopat - ic0 * @wacc',
                      'ic = loan + na',
                      tr=tr, na=na, ke=ke, ic=self.__ic__, wacc=wacc)
        # 检修
        # print('========预测现金流========')
        # print(cf)

        cf.loc[:, ['ts']] = cf.loc[:, ['ts']].apply(lambda x: (x + abs(x)) / 2)
        # for index, data in cf.iterrows():
        #     if data['ts'] < 0:
        #         cf.loc[index, 'ts'] = 0.0

        cf['survival'] = survival

        self.__cf__ = cf
        self.__xcf__ = cf.iloc[-1].to_dict()
        self.__run__ = hypo['run']

        # 计算评分指标
        self.__judge()
        judg = hypo['judg']

        xrg_score = [hypo['rg'][self.__year__ - 1],
                     self.__pgr__,
                     judg['dgr']]

        xevop_score = [hypo['evop'],
                       hypo['aevop'],
                       judg['evm']]

        xpe_score = [hypo['pe'],
                     hypo['ape'],
                     judg['em']]

        xroic_score = [self.__xcf__['nopat'] / self.__xcf__['ic'],
                       self.__roic__,
                       judg['roic']]

        xroe_score = [self.__xcf__['np'] / self.__xcf__['na'],
                      self.__roe__,
                      judg['roe']]

        xsc_score = [0.06,
                     0,
                     judg['sc']]

        xapv_score = [hypo['rg'][self.__year__ - 1],
                      self.__pgr__,
                      judg['apv']]

        self.__jt__ = dict(fcff_pg=self.mark(*xrg_score),
                           fcff_em=self.mark(*xevop_score),
                           fcff_vd=self.mark(*xroic_score),
                           fcfe_pg=self.mark(*xrg_score),
                           fcfe_em=self.mark(*xpe_score),
                           fcfe_vd=self.mark(*xroe_score),
                           eva_sc=self.mark(*xsc_score),
                           ae_sc=self.mark(*xsc_score),
                           apv_pg=self.mark(*xapv_score))

    def __fcff_val(self, delay: int = 0):
        self.__fcff__ = self.__cf_pv('fcff', self.__wacc__, delay)
        year = self.__year__ - delay
        self.__fcff__['adj'] = -self.__nd__  # 股权价值=企业价值-净债务
        self.__fcff__['adj_acc'] = dict(nd=self.__nd__)
        pow_jc = pow(self.__jc__['fcff'], 2)

        if self.__xcf__['fcff'] > 0:
            self.__fcff__['pg'] = self.__pgtv_pv('fcff', self.__wacc__, year)
            if self.__dcf_fcff_pg__:
                self.__fcff__['pg']['wt'] = self.__dcf_fcff_pg__
            else:
                self.__fcff__['pg']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcff_pg'], 2)) / 2)

        if self.__xcf__['op'] > 0:
            self.__fcff__['em'] = self.__emtv_pv('op', self.__wacc__, self.__evop__, year)
            if self.__dcf_fcff_em__:
                self.__fcff__['em']['wt'] = self.__dcf_fcff_em__
            else:
                self.__fcff__['em']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcff_em'], 2)) / 2)

        if self.__xcf__['nopat'] > 0:
            self.__fcff__['vd'] = self.__vdtv_pv('nopat', self.__wacc__, self.__roic__, year)
            if self.__dcf_fcff_vd__:
                self.__fcff__['vd']['wt'] = self.__dcf_fcff_vd__
            else:
                self.__fcff__['vd']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcff_vd'], 2)) / 2)

    def __fcfe_val(self, delay: int = 0):
        self.__fcfe__ = self.__cf_pv('fcfe', self.__ke__, delay)
        year = self.__year__ - delay
        self.__fcfe__['adj'] = 0.0
        pow_jc = pow(self.__jc__['fcfe'], 2)

        if self.__xcf__['fcfe'] > 0:
            self.__fcfe__['pg'] = self.__pgtv_pv('fcfe', self.__ke__, year)
            if self.__dcf_fcfe_pg__:
                self.__fcfe__['pg']['wt'] = self.__dcf_fcfe_pg__
            else:
                self.__fcfe__['pg']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcfe_pg'], 2)) / 2)

        if self.__xcf__['np'] > 0:
            self.__fcfe__['em'] = self.__emtv_pv('np', self.__ke__, self.__pe__, year)
            if self.__dcf_fcfe_em__:
                self.__fcfe__['em']['wt'] = self.__dcf_fcfe_em__
            else:
                self.__fcfe__['em']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcfe_em'], 2)) / 2)

        if self.__xcf__['np'] > 0:
            self.__fcfe__['vd'] = self.__vdtv_pv('np', self.__ke__, self.__roe__, year)
            if self.__dcf_fcfe_vd__:
                self.__fcfe__['vd']['wt'] = self.__dcf_fcfe_vd__
            else:
                self.__fcfe__['vd']['wt'] = sqrt((pow_jc + pow(self.__jt__['fcfe_vd'], 2)) / 2)

    def __eva_val(self, delay: int = 0):
        self.__eva__ = self.__cf_pv('eva', self.__wacc__, delay)
        year = self.__year__ - delay
        self.__eva__['adj'] = self.__ic__ - self.__nd__
        self.__eva__['adj_acc'] = dict(ic=self.__ic__, nd=self.__nd__)
        self.__eva__['sc'] = self.__sctv_pv('eva', self.__wacc__, year)
        self.__eva__['sc']['wt'] = sqrt((pow(self.__jc__['eva'], 2) + pow(self.__jt__['eva_sc'], 2)) / 2)

    def __ae_val(self, delay: int = 0):
        self.__ae__ = self.__cf_pv('ae', self.__ke__, delay)
        year = self.__year__ - delay
        self.__ae__['adj'] = self.__na__
        self.__ae__['adj_acc'] = dict(na=self.__na__)
        self.__ae__['sc'] = self.__sctv_pv('ae', self.__ke__, year)
        self.__ae__['sc']['wt'] = sqrt((pow(self.__jc__['ae'], 2) + pow(self.__jt__['ae_sc'], 2)) / 2)

    def __apv_val(self, delay: int = 0):
        fcff = self.__cf_pv('fcff', self.__ku__, delay)
        ts = self.__cf_pv('ts', self.__kd__, delay)
        year = self.__year__ - delay
        fcff['pg'] = self.__pgtv_pv('fcff', self.__ku__, year)
        ts['pg'] = self.__pgtv_pv('ts', self.__kd__, year)
        self.__apv__ = merge_dict(fcff, ts, self.__dgt__)
        self.__apv__['adj'] = 0.0
        self.__apv__['pg']['wt'] = sqrt((pow(self.__jc__['apv'], 2) + pow(self.__jt__['apv_pg'], 2)) / 2)
        self.__apv__['fcff'] = fcff
        self.__apv__['ts'] = ts

    def __cf_pv(self, name: str, r: float, delay: int = 0):
        """
        计算现金流的风险调整值、现金流的现值、现金流风险调整值的现值
        :param name: 现金流名称（dataframe列）
        :param r: 贴现率
        :param delay: 推迟年数
        :return:
        """
        ylr = self.__ybp__ * self.__blr__  # 年清算价值率
        cf = bat_eval(self.__cf__.loc[delay:, ['year', name, 'survival', 'na']],
                      f'fv_cfs_rj = survival * ({name} + @ylr * na)',  # 现金流未来值 风险调整值
                      f'pv_cfs = {name} / (1 + @r) ** (year - @delay)',  # 现金流现值
                      f'pv_cfs_rj = fv_cfs_rj / (1 + @r) ** (year - @delay)',  # 现金流现值 风险调整值
                      r=r,
                      ylr=ylr,
                      delay=delay)

        cf_pv = {'fv_cfs': cf[name].tolist(),  # 现金流未来值 列表
                 'fv_cfs_rj': cf['fv_cfs_rj'].tolist(),  # 现金流未来值 风险调整值 列表
                 'pv_cfs': cf['pv_cfs'].tolist(),  # 现金流现值 列表
                 'pv_cfs_rj': cf['pv_cfs_rj'].tolist(),  # 现金流现值 风险调整值 列表
                 'npv_cf': cf['pv_cfs_rj'].sum(),  # 现金流现值 风险调整值 合计
                 }

        return cf_pv

    def __tv_common(self, name):
        rbp = 1 if not self.__run__ else self.__rbp__
        xcf = self.__xcf__[name]
        return rbp, xcf

    def __pgtv_pv(self, name: str, r: float, year: int):
        rbp, xcf = self.__tv_common(name)
        blr = self.__xcf__['survival'] * (1 - rbp * self.__blr__)
        df = 1 / pow(1 + r, year)

        fv_xv = xcf * (1 + self.__pgr__) / (r - self.__pgr__)
        fv_xv_rj = fv_xv * blr
        pv_xv = fv_xv * df
        pv_xv_rj = pv_xv * blr

        return {'fv_xv': fv_xv,  # 退出价值未来值
                'fv_xv_rj': fv_xv_rj,  # 退出价值未来值 风险调整值
                'pv_xv': pv_xv,  # 退出价值现值
                'pv_xv_rj': pv_xv_rj,  # 退出价值现值 风险调整值
                'xcf': xcf,  # 退出现金流未来值
                'pgr': self.__pgr__,  # 永续增长率
                'r': r,  # 贴现率
                'df': df,  # 贴现因子
                'year': year,  # 退出年
                'survival': self.__xcf__['survival'],  # 累计生存概率
                'rbp': rbp,  # 残余生存概率
                'blr': self.__blr__,  # 破产损失率
                }

    def __emtv_pv(self, name: str, r: float, mult: float, year: int):
        rbp, xcf = self.__tv_common(name)
        blr = self.__xcf__['survival'] * (1 - rbp * self.__blr__)
        df = 1 / pow(1 + r, year)

        fv_xv = xcf * mult
        fv_xv_rj = fv_xv * blr
        pv_xv = fv_xv * df
        pv_xv_rj = pv_xv * blr

        return {'fv_xv': fv_xv,  # 退出价值未来值
                'fv_xv_rj': fv_xv_rj,  # 退出价值未来值 风险调整值
                'pv_xv': pv_xv,  # 退出价值现值
                'pv_xv_rj': pv_xv_rj,  # 退出价值现值 风险调整值
                'xcf': xcf,  # 退出现金流未来值
                'mult': mult,  # 退出价值乘数
                'r': r,  # 贴现率
                'df': df,  # 贴现因子
                'year': year,  # 退出年
                'survival': self.__xcf__['survival'],  # 累计生存概率
                'rbp': rbp,  # 残余生存概率
                'blr': self.__blr__,  # 破产损失率
                }

    def __vdtv_pv(self, name: str, r: float, robv: float, year: int):
        rbp, xcf = self.__tv_common(name)
        blr = self.__xcf__['survival'] * (1 - rbp * self.__blr__)
        df = 1 / pow(1 + r, year)

        fv_xv = xcf * (1 - self.__pgr__ / robv) / (r - self.__pgr__)
        fv_xv_rj = fv_xv * blr
        pv_xv = fv_xv * df
        pv_xv_rj = pv_xv * blr

        return {'fv_xv': fv_xv,  # 退出价值未来值
                'fv_xv_rj': fv_xv_rj,  # 退出价值未来值 风险调整值
                'pv_xv': pv_xv,  # 退出价值现值
                'pv_xv_rj': pv_xv_rj,  # 退出价值现值 风险调整值
                'xcf': xcf,  # 退出现金流未来值
                'pgr': self.__pgr__,  # 永续增长率
                'robv': robv,  # 资本报酬率
                'r': r,  # 贴现率
                'df': df,  # 贴现因子
                'year': year,  # 退出年
                'survival': self.__xcf__['survival'],  # 累计生存概率
                'rbp': rbp,  # 残余生存概率
                'blr': self.__blr__,  # 破产损失率
                }

    def __sctv_pv(self, name: str, r: float, year: int):
        rbp, xcf = self.__tv_common(name)
        blr = self.__xcf__['survival'] * (1 - rbp * self.__blr__)
        df = 1 / pow(1 + r, year)

        fv_xv = xcf * self.__sc__ / (1 + r - self.__sc__)
        fv_xv_rj = fv_xv * blr
        pv_xv = fv_xv * df
        pv_xv_rj = pv_xv * blr

        return {'fv_xv': fv_xv,  # 退出价值未来值
                'fv_xv_rj': fv_xv_rj,  # 退出价值未来值 风险调整值
                'pv_xv': pv_xv,  # 退出价值现值
                'pv_xv_rj': pv_xv_rj,  # 退出价值现值 风险调整值
                'xcf': xcf,  # 退出现金流未来值
                'sc': self.__sc__,  # 等比例收缩系数
                'r': r,  # 贴现率
                'df': df,  # 贴现因子
                'year': year,  # 退出年
                'survival': self.__xcf__['survival'],  # 累计生存概率
                'rbp': rbp,  # 残余生存概率
                'blr': self.__blr__,  # 破产损失率
                }

    def __judge(self):
        self.__jc__ = {}
        judge_cf = {'fcff': 'fcff', 'fcfe': 'fcfe', 'eva': 'nopat', 'ae': 'np', 'apv': 'apv'}

        for cf_name in judge_cf:
            cf = self.__cf__[judge_cf[cf_name]].tolist()
            stable = np.mean(cf) / np.std(cf)
            cf_score = log(stable + 1) if stable > 0 else 0
            self.__jc__[cf_name] = min(cf_score, 5)

    def __scenario(self):
        # 乐观
        optmhypo = self.__hypo__.scenario('optm')
        pesshypo = self.__hypo__.scenario('pess')
        optm_model = Val(self.__fs__, optmhypo, self.__delay__)
        optm_val, optm_detail = optm_model.get(get_detail=True, delay=self.__delay__, scenario=False)
        pess_model = Val(self.__fs__, pesshypo, self.__delay__)
        pess_val, pess_detail = pess_model.get(get_detail=True, delay=self.__delay__, scenario=False)
        # print('========内部情景分析========')
        # print(optm_val, pess_val)
        return optm_detail, pess_detail

    def get(self, get_detail: bool = False, delay: int = 0, scenario: bool = False):
        assert delay < self.__year__, 'Too long delay!'
        assert delay >= 0, 'Illegal delay!'
        self.__fcff_val(delay)
        self.__fcfe_val(delay)
        self.__eva_val(delay)
        self.__ae_val(delay)
        self.__apv_val(delay)

        # if get_detail:
        #     print(self.__fcff__)

        detail = {}
        wa = WA('base', 'optm', 'pess')

        for cf in ['fcff', 'fcfe', 'eva', 'ae', 'apv']:
            name = f'__{cf}__'
            if name in self.__dir__():
                cf_info = self.__getattribute__(name)  # 取出估值info
                cf_pv = cf_info['npv_cf']  # 取出现金流现值合计
                sub_wa = WA('base')  # 设置一个加权均值计算器，只有1个带计算均值base
                sub_vals = list()  # 所有估值结果

                for sub_name in ['pg', 'em', 'vd', 'sc']:  # 遍历子模型
                    if sub_name in cf_info:  # 如果找到了子模型
                        val = cf_info[sub_name]['pv_xv_rj'] + cf_pv + cf_info['adj']  # 计算子模型估值
                        # 估值=退出价值（现值）+期间现金流价值（现值）+对股权价值的调整值
                        cf_info[sub_name]['val'] = val
                        if val > 0:  # 如果估值大于0，则为有效估值，加入到均值计算器
                            sub_vals.append(cf_info[sub_name]['val'])
                            sub_wa.add(cf_info[sub_name]['wt'], sub_vals[-1])
                        # print(cf, sub_name, val)

                # 如果至少一个估值被加入到list
                if len(sub_vals) > 0:
                    sub_wa.cal()  # 计算加权平均估值
                    cf_info['val'] = sub_wa['base']
                    wt_name = f'__dcf_{cf}__'
                    wt = self.__getattribute__(wt_name)
                    if type(wt) is float:
                        avg_wt = wt
                    else:
                        avg_wt = sub_wa.sum_wt() / len(sub_vals)
                    cf_info['wt'] = avg_wt

                    wa.add(avg_wt, cf_info['val'], max(sub_vals), min(sub_vals))

                if get_detail:
                    detail[cf] = cf_info

        if wa.sum_wt() > 0:
            wa.cal()
            base = wa['base']
        else:
            base = False
            detail['base'] = False
        # print('========查看wa========')
        # print(wa)
        if get_detail:
            detail['disc'] = dict(ke=self.__ke__, ku=self.__ku__, kd=self.__kd__, wacc=self.__wacc__)
            detail['survival'] = self.__cf__['survival'].tolist()
            detail.update(wa)

            detail = self.round(detail)
            if scenario:
                detail['optm_detail'], detail['pess_detail'] = self.__scenario()
            return detail['base'], detail
        else:
            return self.round(base)


class ValMini(Treat):
    def __init__(self, fs, rg_list, npm_list, ke, bottom):
        self.rev = fs['rev']
        self.npm = npm_list
        self.ke = ke
        self.na = bottom
        self.__unpack(rg_list)
        self.detail = dict()

    def __unpack(self, rg_list):
        """
        借用这个方法保障不出现令人怀疑或失望的预测值
        :param rg_list:
        :return:
        """
        for j in range(len(rg_list)):
            if rg_list[j] > 0.5:
                rg_list[j] = 0.5 + (0.5 - rg_list[j]) * 0.25
            elif rg_list[j] > 0.3:
                rg_list[j] = rg_list[j]
            elif rg_list[j] > 0.1:
                rg_list[j] = (0.3 - rg_list[j]) * 0.25 + rg_list[j]
            elif rg_list[j] > 0.05:
                rg_list[j] = (0.1 - rg_list[j]) * 0.5 + rg_list[j]
            elif rg_list[j] > 0.01:
                rg_list[j] = (0.05 - rg_list[j]) * 0.75 + rg_list[j]
            else:
                rg_list[j] = 0.01
        self.__rg__ = rg_list

    def __h_model(self, spke: float = 0):
        ke = self.ke + spke
        rev = self.rev

        cash_flow = []
        np_npv = 0
        df = 1
        for rg, npm in zip(self.__rg__, self.npm):
            df /= (1 + ke)  # 贴现率递推
            rev *= (1 + rg)  # 收入未来值
            profit = rev * npm  # 利润未来值
            cash_flow.append(profit)  # 利润计入列表
            np_npv += profit * df  # 利润贴现并加入净现值
        tv_npv = rev * df * self.npm[-1] * (1 + 0.01) / (ke - 0.01)  # 计算终值

        if spke == 0:
            self.detail['ke'] = ke
            self.detail['rg'] = self.__rg__[0]
            self.detail['cfs'] = cash_flow
            self.detail['cf_npv'] = np_npv
            self.detail['tv_npv'] = tv_npv
            self.detail['tv_npm'] = self.npm[-1]
        return np_npv + tv_npv

    def get(self):
        return tuple([self.__h_model(x) for x in [0.01, 0, -0.01]]), self.detail
