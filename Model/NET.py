from Tool.Util import Treat
import pandas as pd
import pickle as pk
from keras import backend
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import time
from Algorithm.GuessFS import guess_na, get_asset


__all__ = ['Val', 'ValMini']


class NetVal:
    @staticmethod
    def _df(data):
        try:
            df = pd.DataFrame(data)
            drop_cols = []
            for col in ['_id', '_class', 'businessId', 'id']:
                if col in df.columns:
                    drop_cols.append(col)
            return df.drop(columns=drop_cols)
        except Exception as err:
            print(err)
            return data

    @staticmethod
    def _count(iterable):
        count_dict = {}
        for item in iterable:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1
        return count_dict

    @staticmethod
    def _money(expr):
        change_dict = {'亿': '*100000000',
                       '万': '*10000',
                       '千': '*1000',
                       '百': '*100',
                       '十': '*10',
                       ',': ''}
        for o, s in change_dict.items():
            expr = expr.replace(o, s)

        fx = ''
        while True:
            try:
                money = eval(expr)
                break
            except Exception as err:
                print(err)
                fx = expr[-1] + fx
                expr = expr[:-1]

        return money, fx

    def _tyc_unpack(self, tyc):
        self.license = self._df(tyc['AL'])  # 资质证书
        # self.product = tyc['AppbkInfo']  # 产品
        self.compititor = self._df(tyc['FJP'])  # 竞争对手
        # self.financing = tyc['Financing']  # 融资
        self.brand = self._df(tyc['TM'])  # 商标
        self.patent = self._df(tyc['Patent'])  # 专利
        # self.icp = self.__df(tyc['ICP'])  #
        self.software = self._df(tyc['CR'])  # 软件著作权
        # self.work = tyc['CRW']  # 著作权
        # self.news = tyc['New']  # 动态资讯
        self.owner = self._df(tyc['Holder'])  # 股权
        self.info = tyc['TycEnterpriseInfo'][0] if tyc['TycEnterpriseInfo'] else {}  # 工商信息


class Val(Treat, NetVal):
    # backend.clear_session()
    # config = tf.ConfigProto()
    # config.gpu_options.allow_growth = True
    # sess = tf.Session(config=config)
    # backend.set_session(sess)

    def __init__(self, root, tyc, hypo, *args, **kwargs):
        self.modPath = f'{root}Algorithm/NetworkInfoModel/predict_%s.RandomForest'
        self.assetPath = f'{root}Algorithm/AdjustNetAsset/LRforNetassets.model'
        self.keyinfo = dict()
        self.__unpack(tyc)

    def __unpack(self, tyc):
        self._tyc_unpack(tyc)

    def __ana_license(self):
        self.keyinfo['license_count'] = len(self.license)

    def __ana_product(self):
        pass

    def __ana_competitor(self):
        self.keyinfo['competitor'] = self.compititor['jingpinProduct'].tolist()

    def __ana_financing(self):
        pass

    def __ana_brand(self):
        registered_brand = self.brand.query('status == "商标已注册"')
        brand_type_list = registered_brand['intCls'].tolist()
        brand_dict = self._count(brand_type_list)
        self.keyinfo['brand'] = brand_dict

    def __ana_patent(self):
        try:
            status_list = self.patent['lprs'].tolist()
            status_dict = self._count(status_list)
            self.keyinfo['patent_status'] = status_dict
        except Exception as err:
            print(err)
            pass

    # def __ana_icp(self):
    #     icp_list = self.icp['ym'].to_list()
    #     self.keyinfo['icp'] = icp_list

    def __ana_software(self):
        software_list = self.software['fullname'].tolist()
        self.keyinfo['software'] = software_list

    def __ana_work(self):
        pass

    def __ana_news(self):
        pass

    def __ana_owner(self):
        owner_list = self.owner['name'].tolist()
        self.keyinfo['owner'] = owner_list

    def __ana_info(self):
        # self.__keyinfo__['share'] = self.__money(self.__info__['regCapital'])
        # self.__keyinfo__['capital'] = self.__money(self.__info__['actualCapital'])
        #
        # if self.__info__['socialStaffNum'] is None:
        #     staff_count = 1
        # else:
        #     staff_count = self.__info__['socialStaffNum']
        # self.__keyinfo__['staff_count'] = staff_count
        location = self.info.setdefault('regLocation', "Unknown")
        self.keyinfo['location'] = location

        # manager_list = []
        # for j in self.__info__['staffList']['map']['result']['myArrayList']:
        #     manager = dict(position=j['map']['typeSore'], name=j['map']['name'])
        #     manager_list.append(manager)
        # self.__keyinfo__['manager'] = manager_list

    def get(self):
        pass


class ValMini(Treat, NetVal):
    import numpy as np
    # backend.clear_session()
    # config = tf.ConfigProto()
    # config.gpu_options.allow_growth = True
    # sess = tf.Session(config=config)
    # backend.set_session(sess)

    def __init__(self, root, tyc, net_input, peer, mkt_mult, hypo, lite):
        self.modPath = f'{root}Algorithm/NetworkInfoModel/predict_%s.RandomForest'
        self.assetPath = f'{root}Algorithm/AdjustNetAsset/LRforNetassets.model'
        self.__unpack(tyc)

        self.mult_adj = hypo['mult_adj']
        self.na = hypo['bottom']
        self.sprm = hypo['sprm']

        self.keyinfo = net_input
        self.keyinfo['pe'] = peer.query('0 < pe < 100')['pe'].median()
        self.keyinfo['ps'] = peer.query('0 < ps < 100')['ps'].median()
        self.__ana_patent()
        self.__ana_info()
        self.mkt_mult = mkt_mult
        self.lite = lite

        self.detail = dict()

    def __unpack(self, tyc):
        self._tyc_unpack(tyc)

    def __ana_license(self):
        self.keyinfo['license_count'] = len(self.license)

    def __ana_product(self):
        pass

    def __ana_competitor(self):
        self.keyinfo['competitor'] = self.compititor['jingpinProduct'].tolist()

    def __ana_financing(self):
        pass

    def __ana_brand(self):
        registered_brand = self.brand.query('status == "商标已注册"')
        brand_type_list = registered_brand['intCls'].tolist()
        brand_dict = self._count(brand_type_list)
        self.keyinfo['brand'] = brand_dict

    def __ana_patent(self):
        try:
            status_list = self.patent['lprs'].tolist()
            status_dict = self._count(status_list)
            self.keyinfo['patent_status'] = status_dict
        except Exception as err:
            print(err)
            pass

    def __ana_icp(self):
        icp_list = self.icp['ym'].tolist()
        self.keyinfo['icp'] = icp_list

    def __ana_software(self):
        software_list = self.software['fullname'].tolist()
        self.keyinfo['software'] = software_list

    def __ana_work(self):
        pass

    def __ana_news(self):
        pass

    def __ana_owner(self):
        owner_list = self.owner['name'].tolist()
        self.keyinfo['owner'] = owner_list

    def __ana_info(self):
        # self.__keyinfo__['share'] = self.__money(self.__info__['regCapital'])
        # self.__keyinfo__['capital'] = self.__money(self.__info__['actualCapital'])
        #
        # if self.__info__['socialStaffNum'] is None:
        #     staff_count = 1
        # else:
        #     staff_count = self.__info__['socialStaffNum']
        # self.__keyinfo__['staff_count'] = staff_count
        location = self.info.setdefault('regLocation', "Unknown")
        self.keyinfo['location'] = location

        # manager_list = []
        # for j in self.__info__['staffList']['map']['result']['myArrayList']:
        #     manager = dict(position=j['map']['typeSore'], name=j['map']['name'])
        #     manager_list.append(manager)
        # self.__keyinfo__['manager'] = manager_list

    def __pb(self, gics1):
        # backend.clear_session()
        staff = int(self.keyinfo['staff']) if self.keyinfo['staff'] else 0

        rev = self.keyinfo['rev']

        try:
            unvalid_pat = self.keyinfo['patent_status']['无效']
        except Exception as err:
            print(err)
            unvalid_pat = 0

        unvalid_pat = 0 if self.np.isinf(unvalid_pat) or self.np.isnan(unvalid_pat) else unvalid_pat

        adjust_asset = get_asset(gics1, staff, self.assetPath)
        na = 0.2 * self.na + 0.8 * adjust_asset

        x_industry = [40, staff, self.na, rev, unvalid_pat]
        x_size = [gics1, 1, 1, rev, unvalid_pat]
        x_operation = [gics1, staff, self.na, 0, unvalid_pat]
        x_all = [gics1, staff, na, rev, unvalid_pat]
        x_list = [x_all, x_industry, x_size, x_operation]

        for i in range(5):
            try:
                model = pk.load(open(self.modPath % 'pb', 'rb'))
                pb_list = model.predict(x_list)
                self.detail['pb'] = pb_list[-1]
                adj_pb_list = [pb * self.mult_adj * self.sprm for pb in pb_list]
                pb_val_list = [pb * self.na for pb in adj_pb_list]
                break
            except Exception as err:
                print(err)
                time.sleep(5)
        else:
            raise TimeoutError
        return tuple(pb_val_list)

    def __ps(self):
        # backend.clear_session()
        staff = int(self.keyinfo['staff']) if self.keyinfo['staff'] else 0

        rev = self.keyinfo['rev']

        profit = self.keyinfo['np']

        peer_ps = self.keyinfo['ps']
        peer_ps = 1 if self.np.isinf(peer_ps) or self.np.isnan(peer_ps) else peer_ps

        x_industry = [staff, self.na, rev, profit, 2.5]
        x_size = [1, 1, rev, profit, peer_ps]
        x_operation = [staff, self.na, 0, 0, peer_ps]
        x_all = [staff, self.na, rev, profit, peer_ps]
        x_list = [x_all, x_industry, x_size, x_operation]

        for i in range(5):
            try:
                model = pk.load(open(self.modPath % 'ps', 'rb'))
                ps_list = model.predict(x_list)
                self.detail['ps'] = ps_list[-1]
                adj_ps_list = [ps * self.mult_adj * self.sprm for ps in ps_list]
                ps_val_list = [ps * rev for ps in adj_ps_list]
                break
            except Exception as err:
                print(err)
                time.sleep(5)
        else:
            raise TimeoutError

        return tuple(ps_val_list)

    def __pe(self):
        # backend.clear_session()
        staff = int(self.keyinfo['staff']) if self.keyinfo['staff'] else 0
        staff = 1 if staff < 1 else staff

        rev = self.keyinfo['rev']

        profit = self.keyinfo['np']

        peer_pe = self.keyinfo['pe']
        peer_pe = 10 if self.np.isinf(peer_pe) or self.np.isnan(peer_pe) else peer_pe

        if profit > 0:
            cap_to_np = self.na / profit
            cap_to_np = 10000 if self.np.isinf(cap_to_np) else cap_to_np

            cap_to_rev = self.na / rev
            cap_to_rev = 10000 if self.np.isinf(cap_to_rev) else cap_to_rev

            x_industry = [staff, self.na, rev, profit, 10, cap_to_np, cap_to_rev]
            x_size = [1, 1, rev, profit, peer_pe, cap_to_np, cap_to_rev]
            x_operation = [staff, self.na, 0, 0, peer_pe, cap_to_np, cap_to_rev]
            x_all = [staff, self.na, rev, profit, peer_pe, cap_to_np, cap_to_rev]

            x_list = [x_all, x_industry, x_size, x_operation]
            for i in range(5):
                try:
                    model = pk.load(open(self.modPath % 'pe', 'rb'))
                    pe_list = model.predict(x_list)
                    self.detail['pe'] = pe_list[-1]
                    adj_pe_list = [pe * self.mult_adj * self.sprm for pe in pe_list]

                    pe_val_list = [pe * profit for pe in adj_pe_list]
                    return tuple(pe_val_list)
                except Exception as err:
                    print(err)
                    time.sleep(5)
            else:
                raise TimeoutError
        else:
            return None

    def get(self):
        gics1 = int(str(self.keyinfo['code'])[:2])
        # pb_res = self.__pb(gics1)
        method_dict = {'pb': self.__pb(gics1), 'ps': self.__ps(), 'pe': self.__pe()}

        # 溢价表
        premium_dict = {}
        for method, val_series in method_dict.items():
            if val_series is None:
                continue
            val = val_series[0]
            mva = val - self.na
            industry_premium = val - val_series[1]
            size_premium = val - val_series[2]
            operation_premium = val - val_series[3]
            undefined_premium = mva - industry_premium - size_premium - operation_premium

            # 为每个溢价添加流动性折价和可信度折价
            industry_premium *= 0.6
            size_premium *= 0.4
            operation_premium *= 0.3
            undefined_premium *= 0.2

            premium_dict[method] = dict(undefined=int(undefined_premium), industry=int(industry_premium),
                                        size=int(size_premium), operation=int(operation_premium))

        case_dict = {}
        for method, premiums in premium_dict.items():
            base_val = int(self.na + premiums['undefined'] + premiums['industry'] + premiums['size'] +
                           premiums['operation'])
            optm_val = int(base_val + 0.03 * abs(premiums['industry']) + 0.06 * abs(premiums['size']) +
                           0.09 * abs(premiums['operation']))
            pess_val = int(base_val - 0.02 * abs(premiums['industry']) - 0.04 * abs(premiums['size']) -
                           0.06 * abs(premiums['operation']))

            case_dict[method] = (max(pess_val, 0), max(base_val, 0), max(optm_val, 0))

        self.detail['net_prem'] = premium_dict
        return case_dict,  self.detail
