from numpy.random import normal
from copy import deepcopy


__all__ = ['Default', 'Hypo']


class Default:
    """
    基本假设 base
        系统参数
        dgt: 小数保留位数 years: 预测年数 yds: 年化天数 coy: 结转亏损年数 trace: 最大采用历史报表年数 simu: 蒙特卡罗次数
        run: 持续经营状态 tt: 最大预测尝试次数 insol: 承受资不抵债最大年数 defi: 承受亏损最大年数
        均值复归参数
        arc: 均回归因子 src: 慢回归因子 frc: 快回归因子
        风险成本
        rf: 无风险收益率 mrp: 市场风险溢价 ub: 无杠杆beta系数 dic: 目标带息债/全部投入资本 lrp: 流动性风险溢价 srp: 规模风险溢价
        crp: 控制权风险溢价 prp: 政策风险溢价 sprp: 特殊风险溢价 kd: 借款利率 ks: 存款利率 tr: 所得税率
        乘数溢价
        lrm: 流动性风险乘数 srm: 规模风险乘数 cpm: 控制权乘数 prm: 政策风险乘数 sprm: 特殊风险乘数
        财务指标
        gr: 增长率（列表） agr: 市场平均增长率
        cm: 成本率 acm: 行业平均成本率
        sm: 费用率 asm: 行业平均费用率
        pda: 已有固定资产平均折旧年限 cda: 新增固定资产平均折旧年限
        capr: 资本支出销售率 capex: 资本支出（列表）
        divr: 股利净利率 div: 分红（列表）
        rdr: 研发销售率 rd: 研发费用（列表）
        经营效率
        dsi: 存货周转天数 adsi: 行业存货周转天数
        dso: 应收账款周转天数 adso: 行业应收账款周转天数
        dpo: 应付账款周转天数 adpo: 行业应付账款周转天数
        经营目标
        lcp: 最小现金/应收账款比率 mca: 最大现金/资产率 lcash: 最小现金金额
        终值计算
        evop: 行业EV/EBIT乘数 aevop: 市场EV/EBIT乘数 pe: 行业市盈率 ape: 市场市盈率 evic: 行业ev/bvic乘数
        aevic: 市场ev/bvic乘数 pb: 行业市净率 apb: 市场市净率 roic: 市场投资资本报酬率 roe: 市场净资产报酬率
        pgr: 永续增长率 sc: 超额收益收缩系数 ybp: 年破产概率 rbp: 残余破产概率 blr: 破产市值损失率 nb: 净借款（列表）
    情景分析参数
        optm: 乐观情况增量
        pess: 悲观情况增量
    敏感性分析参数 sens
        敏感性分析的参数列表
    蒙特卡罗模拟参数 mont
        正态分布的标准差
    模型评分参数 judg
    市场法假设 mark
        lmt: 绝对离差限制 unit: 离群值计分单位
    期权法假设 optn
    资产法假设 asst
    """
    
    base = dict(dgt=2, years=10, yds=360, coy=5, trace=3, simu=100, alpha=0.10, run=True, tt=20, insol=2, defi=8,
                arc=0.85, src=0.95, frc=0.67,
                rf=0.03, mrp=0.03, ub=1.0, dic=0.2, lrp=0.02, srp=0.02, crp=-0.00, prp=0.0, sprp=0.0,
                lrm=0.7, srm=0.95, crm=1.0, prm=1.0, sprm=1.0, kd=0.12, ks=0.02, tr=0.25,
                rg=[0.05], arg=0.05, cm=0.5, acm=0.5, sm=0.3, asm=0.3, pda=10.0, cda=15.0,
                capr=0.03, capex=None, divr=0.0, div=None, rdr=0.02, rd=None,
                dsi=60.0, adsi=60.0, dso=30.0, adso=30.0, dpo=30.0, adpo=30.0,
                lcp=0.8, mca=0.3, lcash=10000.0,
                evop=24.0, aevop=8.0, pe=40.0, ape=16.0, evic=2.0, aevic=2.0, pb=3.0, apb=3.0, roic=0.05, roe=0.08,
                pgr=0.01, sc=0.95, ybp=0.01, rbp=0.03, blr=0.3, nb=None)

    optm = dict(sprp=-0.01, rg=0.01, arg=0.01, acm=-0.01, asm=-0.01, pda=1.0, cda=1.0,
                capr=-0.01, divr=0.05, rdr=0.01,
                adsi=-5.0, adso=-5.0, adpo=5.0, aevop=1.0, ape=1.0, aevic=0.2, apb=0.3,
                roic=0.01, roe=0.01, pgr=0.005, sc=0.01)

    pess = dict(sprp=0.01, rg=-0.01, arg=-0.01, acm=0.01, asm=0.01, pda=-1.0, cda=-1.0,
                capr=0.01, divr=-0.05, rdr=-0.01,
                adsi=5.0, adso=5.0, adpo=-5.0, aevop=-1.0, ape=-1.0, aevic=-0.2, apb=-0.3,
                roic=-0.01, roe=-0.01, pgr=-0.005, sc=-0.01)

    sens = dict(years=1, sprp=0.01, rg=0.02, acm=0.02, asm=0.02, capr=0.02, divr=0.02, rdr=0.005,
                dsi=5.0, dso=5.0, dpo=5.0, aevop=0.5, ape=1.0, aevic=0.3, apb=0.5,
                roic=0.02, roe=0.02, pgr=0.005, sc=0.01)
    
    mont = dict(sprp=0.01, rg=0.01, acm=0.01, asm=0.01, capr=0.01, divr=0.05, rdr=0.002,
                adsi=5.0, adso=5.0, adpo=5.0, aevop=1.0, ape=1.5, aevic=0.3, apb=0.5,
                roic=0.01, roe=0.015, pgr=0.005, sc=0.01)

    judg = dict(dgr=0.01, evm=1.0, em=1.5, roic=0.015, roe=0.02, bm=0.1, sc=0.02, apv=0.02)

    mark = dict(lmt=2, unit=3.0)

    optn = {"optn-rate": 0.05, "optn-dev": 0.05, "optn-last": 10}

    astb = dict(base=0.0, optm=0.1, pess=-0.1)


class Hypo(dict):
    """
    包含有各种缺省假设参数
    """
    # 其他全局参数
    def __init__(self):
        super().__init__(**Default.base)
        self['optm'] = Default.optm
        self['pess'] = Default.pess
        self['sens'] = Default.sens
        self['mont'] = Default.mont
        self['judg'] = Default.judg
        self['mark'] = Default.mark
        self['optn'] = Default.optn
        self['astb'] = Default.astb

    def adjust(self, adj_dict):
        for name, adj in adj_dict.items():
            if adj is not None:
                if type(self[name]) is list:
                    self[name] = [item + adj for item in self[name]]
                elif type(self[name]) is tuple:
                    self[name] = tuple([item + adj for item in self[name]])
                elif type(self[name]) is dict:
                    self[name] = {key: value + adj for key, value in self[name].items()}
                else:
                    self[name] = adj if self[name] is None else self[name] + adj

    def deep_update(self, target):
        for name in target:
            if type(target[name]) is dict:
                self[name].update(target[name])
                target[name] = self[name]
        self.update(target)

    def get_copy(self, leave: list = None):
        hypo = deepcopy(self)
        names = ['sens', 'mont', 'mark', 'optn', 'astb']
        if leave is not None:
            for name in leave:
                try:
                    names.remove(name)
                except ValueError:
                    continue
        for name in names:
            if name in hypo:
                hypo.__delitem__(name)
        return hypo

    def scenario(self, case: str):
        assert case in ['optm', 'pess'], f'Case {case} not exit!'
        adj = self[case]
        hypo = self.get_copy()
        for name in adj:
            if self[name] is None:
                continue
            elif type(self[name]) is list:
                hypo[name] = [i + adj[name] for i in hypo[name]]
            else:
                hypo[name] += adj[name]
        hypo.get_copy()
        return hypo

    def sensitive(self):
        adj = self['sens']
        for name in adj:
            hypo1, hypo2 = self.get_copy(), self.get_copy()
            if self[name] is None:
                continue
            elif type(self[name]) is list:
                hypo1[name] = [item + adj[name] for item in hypo1[name]]
                hypo2[name] = [item - adj[name] for item in hypo2[name]]
            else:
                hypo1[name] += adj[name]
                hypo2[name] -= adj[name]
            yield name, hypo1, hypo2, adj[name]
        yield False, None, None, None

    def monte_carlo(self):
        adj = self['mont']
        while True:
            hypo = self.get_copy()
            for name in adj:
                if self[name] is None:
                    continue
                elif type(self[name]) is list:
                    hypo[name] = [normal(item, adj[name]) for item in hypo[name]]
                else:
                    hypo[name] = normal(hypo[name], adj[name])
            yield hypo

    def advance(self):
        hypo = self.get_copy()
        vals = ['cm', 'sm', 'dsi', 'dso', 'dpo', 'evop', 'pe', 'evic', 'pb']
        tars = ['a' + name for name in vals]
        rcs = ['src', 'src', 'arc', 'arc', 'arc', 'arc', 'arc', 'arc', 'arc']
        for val, tar, rc in zip(vals, tars, rcs):
            hypo[val] = self[val] * self[rc] + self[tar] * (1 - self[rc])
        return hypo

    def get_value(self, name_list):
        return tuple([self.get(name) for name in name_list])

    def to_general(self, name_list: list = None):
        name_list = self.keys() if name_list is None else name_list
        return {name: self[name] for name in name_list}
