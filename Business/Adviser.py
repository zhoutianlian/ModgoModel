from abc import abstractmethod
from sklearn.linear_model import LinearRegression
from Business import Set


__all__ = ['BMAnalyst']


def switch(underwritten, x: list, y: list):
    model = LinearRegression()
    x2 = [pow(item, 2) for item in x]
    model.fit(X=[x, x2], y=y)
    return model.predict([[underwritten, pow(underwritten, 2)]])[0]


class BMAnalyst:
    __base__ = dict(arc=0, src=0, frc=0, 
                    ub=0, dic=0, lrp=0, srp=0, crp=0, prp=0,
                    lrm=0, srm=0, crm=0, prm=0,
                    kd=0, tr=0,
                    rg=0, arg=0, cm=0, acm=0, sm=0, asm=0, pda=0, cda=0,
                    capr=0, divr=0, rdr=0,
                    dsi=0, adsi=0, dso=0, adso=0, dpo=0, adpo=0,
                    lcp=0, mca=0, lcash=0,
                    pgr=0, sc=0, ybp=0, rbp=0, blr=0)

    __optm__ = dict(sprp=0, rg=0, arg=0, acm=0, asm=0, pda=0, cda=0, capr=0, divr=0, rdr=0,
                    adsi=0, adso=0, adpo=0, aevop=0, ape=0, aevic=0, apb=0, roic=0, roe=0, pgr=0, sc=0)

    __pess__ = dict(sprp=0, rg=0, arg=0, acm=0, asm=0, pda=0, cda=0, capr=0, divr=0, rdr=0,
                    adsi=0, adso=0, adpo=0, aevop=0, ape=0, aevic=0, apb=0, roic=0, roe=0, pgr=0, sc=0)

    __mont__ = dict(sprp=0, rg=0, acm=0, asm=0, capr=0, divr=0, rdr=0,
                    adsi=0, adso=0, adpo=0, aevop=0, ape=0, aevic=0, apb=0, roic=0, roe=0, pgr=0, sc=0)

    __optn__ = dict(rate=0, dev=0, last=0)

    __astb__ = dict(base=0, optm=0, pess=0)

    def __init__(self, bm_data: dict):
        self.__bm__ = bm_data
        self.__ana()

    def print(self):
        for item in [self.__base__, self.__optm__, self.__pess__, self.__mont__, self.__optn__, self.__astb__]:
            print(item)

    def __ana(self):
        pff = PFF(self.__bm__)
        pff, pff_detail = pff.advice()
        # swot, swot_detail = SWOT(self.__bm__).advice()
        # pest, pest_detail = PEST(self.__bm__).advice()
        # gem, gem_detail = GEM(self.__bm__).advice()
        # for advice in ['pff', 'swot', 'pest', 'gem']:
        #     for pack in ['base', 'optm', 'pess', 'mont', 'optn', 'astb']:
        #         run('self.__base__ = self.__update(self.__base__, @advice[@pack])')
        #     run('self.__detail__[@advice] = %s_detail' % advice)
        pass

    def advise(self):
        if self.__bm__["market"] in [0]:
            for i in ["lrp", "srp", "crp", "prp"]:
                self.__base__[i] = 0
            for i in ["lrm", "srm", "crm", "prm"]:
                self.__base__[i] = 1
        # print(self.__base__)
        # print(self.__optm__)
        # print(self.__pess__)
        return self.__base__

class Model:
    """
    这是一个商业分析模型的父类
    """

    def __init__(self, bm):
        self.__bm__ = bm
        self.__run()

    @abstractmethod
    def __run(self):
        """
        这是一个运行模型的虚拟方法
        :return:
        """
        pass

    @abstractmethod
    def advice(self):
        """
        这个方法用于返回建议
        :return:
        """
        pass


class PFF(Model):
    """
    波特五力分析
    Porter's Five Force Model
    """

    __competitor__ = {}  # 竞争者威胁
    __entrants__ = {}  # 新进者威胁
    __alternative__ = {}  # 替代品威胁
    __supplier__ = {}  # 对上游议价权
    __customer__ = {}  # 对下游议价权

    def __run(self):
        for name in self.__dir__():
            if '__' + name in self.__bm__:
                self.__getattribute__('__' + name)(self.__bm__[name])

    def __established_years(self, year):
        self.__competitor__['competition_status'] = switch(year, [0, 5, 10, 15, 20], [0.8, ])

    def advice(self):
        return 0, 0


class SWOT(Model):
    """
    SWOT分析
    Strength, Weakness, Opportunity, Threats
    """
    __sth__ = {}  # 优势
    __wkn__ = {}  # 劣势
    __opt__ = {}  # 机遇
    __thr__ = {}  # 挑战

    def __run(self):
        self.__ana_strength__()
        self.__ana_weakness__()
        self.__ana_opportunity__()
        self.__ana_threaten__()

    def __ana_strength__(self):
        if 'continuing_running_years' in self.__bm__ and \
                self.__bm__['continuing_running_years'] >= 10:
            # 持续经营超过5年（且仍然存活），是一种优势
            self.__sth__['long_running'] = self.__bm__['continuing_running_years']

        if 'headquarters_location' in self.__bm__:
            # 坐落在越发达地区，越有优势
            city = self.__bm__['headquarters_location']
            if city in Set.city_class1:
                self.__sth__['perfect_location'] = city
            elif city in Set.city_class2:
                self.__sth__['good_location'] = city
            elif city in Set.city_class3:
                self.__sth__['ok_location'] = city
        pass

    def __ana_weakness__(self):
        if 'continuing_running_years' in self.__bm__ and self.__bm__['continuing_running_years'] < 5:
            # 持续经营小于5年，是一种劣势
            self.__wkn__['short_running'] = self.__bm__['continuing_running_years']

        pass

    def __ana_opportunity__(self):
        pass

    def __ana_threaten__(self):
        pass

    def advice(self):
        pass


class PEST(Model):
    """
    PEST分析
    Political, Economic, Social, Technical, Legal, Environmental
    """
    __pol__ = []  # 政治
    __eco__ = []  # 经济
    __soc__ = []  # 社会
    __tec__ = []  # 技术
    __leg__ = []  # 法律
    __env__ = []  # 环境

    def __run(self):
        self.__ana_political__()
        self.__ana_economic__()
        self.__ana_social__()
        self.__ana_technical__()
        self.__ana_legal__()
        self.__ana_environmental__()

    def __ana_political__(self):
        pass

    def __ana_economic__(self):
        pass

    def __ana_social__(self):
        pass

    def __ana_technical__(self):
        pass

    def __ana_legal__(self):
        pass

    def __ana_environmental__(self):
        pass

    def advice(self):
        pass


class GEM(Model):
    """
    GE矩阵分析
    GE/Mckinsey Matrix
    """
    __mkt__ = []  # 市场引力
    __com__ = []  # 竞争地位

    def __run(self):
        self.__ana_mkt__()
        self.__ana_com__()

    def __ana_mkt__(self):
        pass

    def __ana_com__(self):
        pass

    def advice(self):
        pass


if __name__ == '__main__':
    from Dev.update_mongo import m1 as m
    from FinMod.FS import BM
    my_bm = BM(m)
    BMA = BMAnalyst(my_bm)
    print(BMA.advise())

