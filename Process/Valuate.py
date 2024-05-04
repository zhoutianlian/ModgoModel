from Algorithm.Complete import periodic_hypo
from Model import *
from Report.Log import logger
from copy import deepcopy
from Config import Traceback
from pandas import Series as Sr, DataFrame as Df
import numpy as np

__all__ = ['dcf_valuator', 'dcf_valuator_mini', 'mkt_valuator', 'mkt_valuator_mini', 'aba_valuator',
           'opt_valuator', 'opt_valuator_mini', 'net_valuator', 'net_valuator_mini']


# @logs
def dcf_valuator(fs_orig, orig_hypo, mode: int):
    """
    这是一个执行收入法估值的方法，可以根据模式调用基准估值、情景分析、敏感性分析或蒙特卡罗模拟
    :param fs_orig:
    :param orig_hypo:
    :param mode:
    :return:
    """
    hypo = orig_hypo.get_copy()
    fs = fs_orig.get_copy()
    fs.start()
    # 计算一般性估值结果
    base_fs, base_val, detail = dcf_simulator(fs, hypo, detail=True, scenario=True)
    # 剔除流动性折价的计算结果
    logger(1, '剔除流动性折价')
    lr_hypo = orig_hypo.get_copy()
    lr_hypo['lrp'] = 0
    lr_hypo['lrm'] = 1
    lr = base_val - dcf_simulator(fs, lr_hypo)
    detail['lr'] = lr

    # 剔除控制权
    logger(1, '剔除控制权溢价')
    cp_hypo = orig_hypo.get_copy()
    cp_hypo['lrp'] = 0
    cp_hypo['lrm'] = 1
    cp_hypo['crp'] = 0
    cp_hypo['crm'] = 1
    cp = base_val - lr - dcf_simulator(fs, cp_hypo)
    detail['cp'] = cp

    # 计算可追溯估值
    logger(1, '计算可追溯估值')
    ke_list = deepcopy(Traceback.ke)
    traceback = []
    for ke in ke_list:
        tb_hypo = orig_hypo.get_copy()
        tb_hypo['ke'] = ke
        traceback.append((ke, dcf_simulator(fs, tb_hypo)))
    detail['traceback'] = traceback
    logger(1, '可追溯估值计算结束')

    if not base_val:
        return base_fs, base_val, detail

    if mode == 1:
        models = ['fcff', 'fcfe', 'eva', 'ae', 'apv']
        base_detail = {key: detail[key].setdefault('val', np.nan) for key in models}
        optm_detail = {key: detail['optm_detail'][key].setdefault('val', 0) for key in models}
        pess_detail = {key: detail['pess_detail'][key].setdefault('val', 0) for key in models}
        wt = {key: detail[key].setdefault('wt', 0) for key in models}
        model_vals = Df([base_detail, optm_detail, pess_detail, wt], index=['base', 'optm', 'pess', 'wt']).T
        model_vals = model_vals.dropna(how='any')
        sum_wt = model_vals.wt.sum()
        base_val = model_vals.eval('base * wt').sum() / sum_wt
        optm_val = model_vals.eval('optm * wt').sum() / sum_wt
        pess_val = model_vals.eval('pess * wt').sum() / sum_wt

        # print('======情景分析======')
        # print(model_vals)
        pess_val, base_val, optm_val = min(pess_val, base_val, optm_val), np.median([pess_val, base_val, optm_val]), max(
            pess_val, base_val, optm_val)
        detail['base'] = base_val
        detail['optm'] = optm_val
        detail['pess'] = pess_val

        logger(1, '情景分析结束')

    elif mode == 2:
        logger(1, '调用敏感性分析')
        der_dict = {}
        hypo = orig_hypo.get_copy(['sens'])
        hypo_gen = hypo.sensitive()
        while True:
            name, hypo1, hypo2, dx = next(hypo_gen)
            if not name:
                logger(1, '敏感性分析结束')
                break
            else:
                logger(1, '对%s的敏感性分析' % name)
                val1, val2 = dcf_simulator(fs, hypo1), dcf_simulator(fs, hypo2)
                if val1 > 0 and val2 > 0:
                    der_d = (val2 - base_val) / dx
                    der_u = (val1 - base_val) / dx
                else:
                    der_u = der_d = False
                der_dict[name] = (der_d, der_u)
        detail['der'] = der_dict

    elif mode == 3:
        logger(1, '调用蒙特卡罗模拟')
        result_list = []
        hypo = orig_hypo.get_copy(['mont'])
        hypo_gen = hypo.monte_carlo()
        times = hypo['simu']
        while times > 0:
            if times % 10 == 0:
                logger(0, '剩余%s次' % times)
            rand_hypo = next(hypo_gen)
            rand_val = dcf_simulator(fs, rand_hypo)
            if rand_val > 0:
                result_list.append(rand_val)
                times -= 1
        results = Sr(result_list)
        detail['optm'] = results.quantile(1 - hypo['alpha'])
        detail['pess'] = results.quantile(hypo['alpha'] / 2)
        detail['base'] = results.median()
        detail['mean'] = results.mean()
        detail['std'] = results.std()
        detail['mad'] = results.mad()
        detail['skew'] = results.skew()
        detail['kurt'] = results.kurt()
        detail['dist'] = result_list
        logger(1, '蒙特卡罗模拟结束')

    # print(base_val)
    return base_fs, base_val, detail


# @logs
def dcf_valuator_mini(fs, rg_list, npm_list, ke, bottom):
    dcf_model = DCF.ValMini(fs, rg_list, npm_list, ke, bottom)
    return dcf_model.get()


# @logs
def dcf_simulator(orig_fs, orig_hypo, detail: bool = False, scenario: bool = False):
    fs = orig_fs.get_copy()
    hypo = orig_hypo.get_copy()
    hypo['years'] = int(hypo['years'])
    # 调用后续增长率模型
    if len(hypo['rg']) < hypo['years']:
        hypo = periodic_hypo(hypo)

    for i in range(hypo['years']):
        # print('第', i, '次预测')
        hypo = fs.forecast(hypo)
        if not hypo['run']:
            break

    # 检修
    # import pandas as pd
    # print('========预测的报表========')
    # print(pd.DataFrame(fs).T)

    dcf_model = DCF.Val(fs, hypo)
    if detail:
        val, detail = dcf_model.get(get_detail=True, scenario=scenario)
        # 计算未来历年估值
        delay_list = [val]
        for delay in range(1, hypo['years']):
            try:
                delay_list.append(dcf_model.get(delay=delay))
            except Exception as err:
                print(err)
                break
        detail['delay'] = delay_list
        return fs, val, detail
    else:
        val = dcf_model.get()
        return val


# @logs
def mkt_valuator(peer_data: Df, fs0, fs1, orig_hypo):
    """
    这是一个执行市场法估值的方法，
    :param peer_data: DataFrame 包含列名:
    code, ev, mv, wt,
    pe, pe1, peg1, ptp, ptp1, pb, pb1, pcf, pcf1, prd, pd, ps, ps1,
    evs, evs1, evrd, evopda, evopda1, evop, evop1, evnopat, evnopat1, evic, evic1,
    :param fs0: dict
    cash, ar, inv, ppe, oa, ta,
    loan, ap, ol, tl,
    share, re, na,
    rev, cogs, gp, sga, rd, opada, da, op, ie, tp, tax, np,
    dap, rec_reduce, pay_raise, inv_reduce, cfo,
    capex, cfi,
    nb, div, cff, tcf
    :param fs1: 同上
    :param orig_hypo:
    hypo['mark']: lmt: 绝对离差限制
    :return:
    """
    hypo = orig_hypo.get_copy(['mark'])
    mkt_model = MKT.Val(peer_data, fs0, fs1, hypo)
    val, detail = mkt_model.get()
    return val, detail


# @logs
def mkt_valuator_mini(peer_data, fs, mkt_mult, mult_adj, bottom):
    """
    这是一个服务于Mini估值的市场法
    :param peer_data:
    :param fs:
    :param mkt_mult:
    :param mult_adj:
    :param bottom: 保底
    :return:
    """
    hypo = {'sprm': 0.6, 'mult_adj': mult_adj, 'bottom': bottom}
    mkt_model = MKT.ValMini(peer_data, fs, mkt_mult, hypo)
    return mkt_model.get()


# @logs
def opt_valuator(fs, peer_ratio, orig_hypo):
    """
    这是一个运行期权估值法的管理器
    :param fs:
    :param peer_ratio:
    :param orig_hypo:
    :return:
    """
    hypo = orig_hypo.get_copy(['optn'])
    opt_model = opt_test.Val(fs, peer_ratio, hypo)
    val, detail = opt_model.get()
    return val, detail


# @logs
def opt_valuator_mini(fs, rg_list, npm_list, wacc, bottom):
    npm_list = [min(0.9, i) for i in npm_list]
    opt_model = opt_test.ValMini(fs, rg_list, npm_list, wacc, bottom)
    return opt_model.get()


# @logs
def aba_valuator(fs, peer_bal, orig_hypo):
    """
    这是一个允许资产基础法的管理器
    :param fs:
    :param peer_bal:
    :param orig_hypo:
    :return:
    """
    hypo = orig_hypo.get_copy(['astb'])
    aba_model = ABA.Val(fs, peer_bal, hypo)
    val, detail = aba_model.get()
    return val, detail


# @logs
def net_valuator(root, fs0, tyc, *args, **kwargs):
    hypo = dict()
    net_model = NET.Val(root, tyc, *args, **kwargs)
    return net_model.get()


# @logs
def net_valuator_mini(root, tyc, net_input, peer, mkt_mult, mult_adj, bottom, lite=False):
    """
    这是基于天眼查的快速网信估值算法
    :param root:
    :param net_input:
    :param peer:
    :param tyc:
    :param mkt_mult:
    :param mult_adj:
    :param bottom:
    :param lite:
    :return:
    """
    hypo = dict(sprm=0.6, mult_adj=mult_adj, bottom=bottom)
    net_model = NET.ValMini(root, tyc, net_input, peer, mkt_mult, hypo, lite)
    return net_model.get()
