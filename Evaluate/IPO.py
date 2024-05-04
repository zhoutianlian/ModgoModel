import Config.Database
from FinMod.FS import FinStm as Fs
from Data.Conn import ConnMongo
from Config.Database import Database as Db, Fields as Fd, Index as Ix
from Report.Log import logger
from numpy import median


__all__ = ['IPOProspect']


class IPOProspect:
    """
    这是一个判断企业需要多久上市及适合哪个市场的算法
    """
    __prospect__ = {}

    def __init__(self, fs: Fs, syn_val, mini: bool=False):
        self.__fs__ = fs

        if not mini:
            self.__start__ = fs.start()
            self.__pe__ = syn_val / fs[self.__start__]['np']
        else:
            self.__start__ = 1
        self.__fx__ = self.get_fx()
        self.mini = mini

    @staticmethod
    def get_fx():
        db_config = Config.Database.ConnDB
        with ConnMongo(**db_config.orig) as conn:
            tb, where, select = Db.fx['tb'], Db.fx['where'], Db.fx['select']
            fx_data = conn(tb).find_new(where={where: {'$in': [Ix.hkd, Ix.gbp, Ix.usd]}}, select=select)
            fx = {d[Fd.fxcode]: d[Fd.fx] for _, d in fx_data.iterrows()}
        return fx

    def year_init(self, _tb):
        return max(self.__start__ - _tb, 0)

    def mark(self, name, init, _tb):
        self.__prospect__[name] = max(init - self.__start__ + _tb, 0)

    def unmark(self, name):
        self.__prospect__[name] = -1

    def astock(self):
        """
        沪深A股
        最近3个会计年度净利润均为正数且累计超过人民币3000万元
        收入最近3个会计年度营业收入累计超过人民币3亿元
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        accum_np = 3e7
        accum_rev = 3e8
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                _rev = [self.__fs__[init + i]['rev'] for i in range(_tb)]
                if min(_np) > 0 and sum(_np) > accum_np and sum(_rev) > accum_rev:
                    self.mark('沪深A股', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('沪深A股')
                return

    def gem(self):
        """
        深市创业板
        净利润最近两年连续盈利，最近两年净利润累计不少于一千万元
        或者最近一年盈利，且净利润不少于五百万元
        最近一期末(净资产)股权不少于2000万元
        :return:
        """
        self.gem1()
        self.gem2()

    def gem1(self):
        """
        深市创业板条件1
        净利润最近两年连续盈利，最近两年净利润累计不少于一千万元
        最近一期末(净资产)股权不少于2000万元
        :return:
        """
        _tb = 2
        init = self.year_init(_tb)
        accum_np = 1e7
        last_na = 2e7
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                _na = self.__fs__[init + _tb - 1]['na']
                if min(_np) > 0 and sum(_np) > accum_np and _na > last_na:
                    self.mark('深市创业板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('深市创业板')
                return

    def gem2(self):
        """
        深市创业板条件2
        最近一年盈利，且净利润不少于五百万元
        最近一期末(净资产)股权不少于2000万元
        :return:
        """
        _tb = 1
        init = self.year_init(_tb)
        last_np = 5e6
        lasp_na = 2e7
        while True:
            try:
                _np = self.__fs__[init + _tb - 1]['np']
                _na = self.__fs__[init + _tb - 1]['na']
                if _np > last_np and _na > lasp_na:
                    self.mark('深市创业板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('深市创业板')
                return

    def star(self):
        """
        沪市科创板
        至少符合下列标准中的一项：
        （一）预计市值不低于人民币 10 亿元，最近两年净利润均为正且累计净利润不低于人民币 5000 万元，
        或者预计市值不低于人民币 10 亿元，最近一年净利润为正且营业收入不低于人民币 1 亿元；
        （二）预计市值不低于人民币 15 亿元，最近一年营业收入不低于人民币 2 亿元，
        且最近三年累计研发投入占最近三年累计营业收入的比例不低于 15%；
        （三）预计市值不低于人民币 20 亿元，最近一年营业收入不低于人民币 3 亿元，
        且最近三年经营活动产生的现金流量净额累计不低于人民币 1 亿元；
        （四）预计市值不低于人民币 30 亿元，且最近一年营业收入不低于人民币 3 亿元；
        （五）预计市值不低于人民币 40 亿元， 主要业务或产品需经国家有关部门批准，市场空间大，目前已取得阶段性成果。
        :return:
        """
        self.star1()
        self.star2()
        self.star3()
        self.star4()
        # self.__STAR5()
        
    def star1(self):
        """
        沪市科创板
        预计市值不低于人民币 10 亿元，最近两年净利润均为正且累计净利润不低于人民币 5000 万元，
        或者预计市值不低于人民币 10 亿元，最近一年净利润为正且营业收入不低于人民币 1 亿元；
        :return: 
        """
        _tb = 2
        init = self.year_init(_tb)
        accum_np = 5e7
        last_rev = 1e8
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                _rev = self.__fs__[init + _tb - 1]['rev']
                if (min(_np) > 0 and sum(_np) > accum_np) or (_np[-1] > 0 and _rev > last_rev):
                    self.mark('沪市科创板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('沪市科创板')
                return

    def star2(self):
        """
        沪市科创板
        预计市值不低于人民币 15 亿元，最近一年营业收入不低于人民币 2 亿元，
        且最近三年累计研发投入占最近三年累计营业收入的比例不低于 15%；
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_rev = 2e8
        rd_rev = 0.15
        while True:
            try:
                _rev = [self.__fs__[init + i]['rev'] for i in range(_tb)]
                _rd = [self.__fs__[init + i]['rd'] for i in range(_tb)]
                if _rev[-1] > last_rev and sum(_rd) / sum(_rev) > rd_rev:
                    self.mark('沪市科创板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('沪市科创板')
                return

    def star3(self):
        """
        沪市科创板
        预计市值不低于人民币 20 亿元，最近一年营业收入不低于人民币 3 亿元，
        且最近三年经营活动产生的现金流量净额累计不低于人民币 1 亿元；
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_rev = 3e8
        accum_cfo = 1e8
        while True:
            try:
                _rev = self.__fs__[init + _tb - 1]['rev']
                _cfo = [self.__fs__[init + i]['cfo'] if 'cfo' in self.__fs__[init] else 0 for i in range(_tb)]
                if _rev[-1] > last_rev and sum(_cfo) > accum_cfo:
                    self.mark('沪市科创板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('沪市科创板')
                return

    def star4(self):
        """
        沪市科创板
        预计市值不低于人民币 30 亿元，且最近一年营业收入不低于人民币 3 亿元；
        :return:
        """
        _tb = 1
        init = self.year_init(_tb)
        last_rev = 3e8
        while True:
            try:
                _rev = self.__fs__[init + _tb - 1]['rev']
                if _rev > last_rev:
                    self.mark('沪市科创板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('沪市科创板')
                return

    def neeq(self):
        """
        新三板
        :return:
        """
        _tb = 2
        init = self.year_init(_tb)
        while True:
            try:
                _rev = [self.__fs__[init + i]['rev'] for i in range(_tb)]
                if min(_rev) > 0:
                    self.mark('新三板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('新三板')
                return

    def hkex(self):
        """
        香港主板
        市值大于1亿港币
        盈利（净利润）近一年2000w港币，之前两年合计3000w港币
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_np = 2e7 * self.__fx__[Ix.hkd]
        accum_np = 3e7 * self.__fx__[Ix.hkd]
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                if _np[-1] > last_np and sum(_np[:-1]) > accum_np:
                    self.mark('香港主板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('香港主板')
                return

    def hkg(self):
        """
        香港创业板
        市值不能小于4600w港币
        :return:
        """
        pass

    def nyse(self):
        """
        纽交所主板
        市值不小于1亿美元
        公司必须在最近3个财政年度里连续赢利，且在最后一年不少于250万美元、前两年每年不少于200万美元
        或在最后一年不少于450万美元，3年累计不少于650万美元；
        :return:
        """
        self.nyse1()
        self.nyse2()

    def nyse1(self):
        """
        纽交所主板
        公司必须在最近3个财政年度里连续赢利，且在最后一年不少于250万美元、前两年每年不少于200万美元
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_np = 25e5 * self.__fx__[Ix.usd]
        each_np = 2e6 * self.__fx__[Ix.usd]
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                if min(_np) > 0 and _np[-1] > last_np and min(_np[:-1]) > each_np:
                    self.mark('纽交所主板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('纽交所主板')
                return

    def nyse2(self):
        """
        纽交所主板
        或在最后一年不少于450万美元，3年累计不少于650万美元；
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_np = 45e5 * self.__fx__[Ix.usd]
        accum_np = 65e5 * self.__fx__[Ix.usd]
        while True:
            try:
                _np = [self.__fs__[init + i]['np'] for i in range(_tb)]
                if _np[-1] > last_np and sum(_np) > accum_np:
                    self.mark('纽交所主板', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('纽交所主板')
                return

    def nasdaq(self):
        """
        纳斯达克
        股东权益达1500万美元；
        一个财政年度或者近3年里的两年中拥有100万美元的税前收入；
        每股至少5美元；
        :return:
        """
        _tb = 3
        init = self.year_init(_tb)
        last_na = 15e6 * self.__fx__[Ix.usd]
        each_tp = 1e6 * self.__fx__[Ix.usd]
        while True:
            try:
                _tp = [self.__fs__[init + i]['tp'] for i in range(_tb)]
                _na = self.__fs__[init + _tb - 1]['na']
                if (median(_tp) > each_tp or _tp[2] > each_tp) and _na > last_na:
                    self.mark('纳斯达克', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('纳斯达克')
                return

    def lse(self):
        """
        伦交所
        总股本不少于2500万英镑
        :return:
        """
        _tb = 1
        init = self.year_init(_tb)
        last_na = 25e6 * self.__fx__[Ix.gbp]
        while True:
            try:
                _na = self.__fs__[init]['na']
                if _na > last_na:
                    self.mark('伦交所', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('伦交所')
                return

    def aim(self):
        """
        英国AIM市场
        两年的主营业务盈利纪录
        :return:
        """
        _tb = 2
        init = self.year_init(_tb)
        while True:
            try:
                nps = [self.__fs__[init + i]['op'] for i in range(_tb)]
                if min(nps) > 0:
                    self.mark('英国AIM市场', init, _tb)
                    return
                else:
                    init += 1
                    continue
            except Exception as err:
                self.unmark('英国AIM市场')
                return

    def get(self):
        if self.mini:
            self.astock()
            self.nyse()
            self.neeq()
        else:
            self.astock()
            self.gem()
            self.star()
            self.nyse()
            self.nasdaq()
            self.lse()
            self.aim()
            self.neeq()
        return self.__prospect__
