from Tool.Util import Treat, WA
from pandas import DataFrame as Df
from Hypothesis.Basement import Hypo
from Config.Rule import Laws
import numpy as np


__all__ = ['Val', 'ValMini']


class Val(Treat):
    def __init__(self, peer_data: Df, fs0: dict, fs1: dict, hypo: Hypo):
        self.__peer__ = peer_data
        self.__unpack(fs0, fs1, hypo)

    def __unpack(self, fs0, fs1, hypo):
        self.__dgt__ = hypo['dgt']
        nd = fs0['loan'] - fs0['cash']

        mult_acc = {'pe': (fs0['np'], 0),
                    'ptp': (fs0['tp'], 0),
                    'pb': (fs0['na'], 0),
                    'prd': (fs0['rd'], 0),
                    'ps': (fs0['rev'], 0),
                    'evs': (fs0['rev'], -nd),
                    'evrd': (fs0['rd'], -nd),
                    'evopda': (fs0['opda'], -nd),
                    'evop': (fs0['op'], -nd),
                    'evnopat': (fs0['op'] + fs0['ie'] * (1 - Laws.int_tr), -nd),
                    'evic': (fs0['loan'] + fs0['na'], -nd),
                    }

        if fs1 is not None:
            acc1 = {'pe1': (fs1['np'], 0),
                    'peg1': ((fs1['rev'] / fs0['rev'] - 1) * 100 * fs0['np'], 0),
                    'ptp1': (fs1['tp'], 0),
                    'pb1': (fs1['na'], 0),
                    'pcf1': (fs1['cfo'], 0),
                    'ps1': (fs1['rev'], 0),
                    'evs1': (fs1['rev'], -nd),
                    'evopda1': (fs1['opda'], -nd),
                    'evop1': (fs1['op'], -nd),
                    'evnopat1': (fs1['op'] + fs1['ie'] * (1 - Laws.int_tr), -nd),
                    'evic1': (fs1['loan'] + fs1['na'], -nd),
                    }

            mult_acc.update(acc1)

        try:
            mult_acc['pcf'] = (fs0['cfo'], 0)
        except KeyError:
            pass
        self.__acc__ = mult_acc
        lrm, srm, crm, prm, sprm = hypo.get_value(['lrm', 'srm', 'crm', 'prm', 'sprm'])
        self.__cp__ = srm * prm * sprm
        self.__lr__ = self.__cp__ * crm
        self.__md__ = self.__lr__ * lrm
        self.__lmt__, self.__unit__ = hypo['mark']['lmt'], hypo['mark']['unit']
        self.__mkt_pe__, self.__mkt_pe1__, self.__mkt_peg1__, self.__mkt_ptp__, self.__mkt_ptp1__, self.__mkt_pb__, \
        self.__mkt_pb1__, self.__mkt_pcf__, self.__mkt_pcf1__, self.__mkt_pd__, self.__mkt_ps__, self.__mkt_ps1__, \
        self.__mkt_evs__, self.__mkt_evs1__, self.__mkt_evopda__, self.__mkt_evopda1__, self.__mkt_evop__, \
        self.__mkt_evnopat__, self.__mkt_evnopat1__, self.__mkt_evic__, self.__mkt_evic1__ = hypo.get_value(
            ['mkt_pe', 'mkt_pe1', 'mkt_peg1', 'mkt_ptp', 'mkt_ptp1', 'mkt_pb', 'mkt_pb1', 'mkt_pcf', 'mkt_pcf1',
             'mkt_pd', 'mkt_ps', 'mkt_ps1', 'mkt_evs', 'mkt_evs1', 'mkt_evopda', 'mkt_evopda1', 'mkt_evop',
             'mkt_evnopat', 'mkt_evnopat1', 'mkt_evic', 'mkt_evic1'])

    def __normal(self):
        detail = {}
        case_dict = {'base': self.__md__,
                     'lr': self.__lr__,
                     'cp': self.__cp__}
        for case in case_dict:
            cols = self.__peer__.columns.tolist()
            for col in ['code', 'ev', 'mv', 'wt']:
                try:
                    cols.remove(col)
                except KeyError:
                    continue

            wa = WA('base', 'optm', 'pess')
            for name in cols:
                series = self.__peer__.loc[:, ['code', 'wt', name]]
                # 剔除离群值
                series = series.query(f'{name} > 0')
                values = series[name].tolist()
                if len(values) >= 5:
                    q1, q2, q3 = np.percentile(values, [25, 50, 75])
                    # 用四分位数和中值之差除以0.675得出半标准差
                    s3, s1 = (q3 - q2) / 0.675, (q1 - q2) / 0.675
                    upper, lower = q2 + s3 * self.__lmt__, q2 + s1 * self.__lmt__
                    series = series.query(f'@lower < {name} < @upper')
                else:
                    continue

                # 如果可比乘数超过5个，则可用计算基准值和上下限
                if len(series) >= 5:
                    mult = series.eval(f'{name} * wt').sum() / series['wt'].sum()
                    high, low = max(series[name]), min(series[name])
                    try:
                        value = self.__getattribute__(f"__mkt_{name}__")
                        if type(value) is float:
                            wt = value
                        else:
                            wt = self.mark(series[name].mad(), 0, self.__unit__)  # 用离群值/计分单位评分0-5分
                    except:
                        wt = self.mark(series[name].mad(), 0, self.__unit__)  # 用离群值/计分单位评分0-5分

                    model_dict = {'mult': mult,
                                  'high': high,
                                  'low': low,
                                  'wt': wt,
                                  }
                    if name in self.__acc__:
                        acc = self.__acc__[name]
                        if acc[0] > 0:
                            val = (acc[0] * mult + acc[1]) * case_dict[case]
                            optm_val = (acc[0] * high + acc[1]) * case_dict[case]
                            pess_val = (acc[0] * low + acc[1]) * case_dict[case]
                            model_dict['base'] = val
                            model_dict['optm'] = optm_val
                            model_dict['pess'] = pess_val
                            wa.add(wt, val, optm_val, pess_val)
                    if case == 'base':
                        detail[name] = model_dict
                else:
                    continue
            wa.cal()
            case_dict[case] = wa['base']
            if case == 'base':
                detail.update(wa)

        detail['lr'] = case_dict['base'] - case_dict['lr']
        detail['cp'] = case_dict['lr'] - case_dict['cp']
        detail = self.round(detail)
        return detail['base'], detail

    def get(self):
        return self.round(self.__normal())


class ValMini(Treat):

    def __init__(self, peer_data, fs_data, mkt_mult, hypo):
        self.peer = peer_data
        self.fs = fs_data
        self.__unpack(mkt_mult, hypo)
        self.dr = 0.7
        self.detail = dict()

    def __unpack(self, mkt_mult, hypo):
        self.mkt = mkt_mult
        self.sprm = hypo['sprm']
        self.mult_adj = hypo['mult_adj']
        self.na = hypo['bottom']

    def __pe(self):
        print('市盈率模型...')
        # self.detail['peer_pes'] = self.peer['pe'].tolist()
        peer = self.drop_abnormal(self.peer, 'pe', bottom=0)['pe']
        self.detail['peer_pes'] = peer.to_list()
        pe_range = peer.min(), peer.median(), peer.max()
        adj_pe_range = [(pe * 0.7 + self.mkt['pe'] * 0.3) * (1 + self.mult_adj) for pe in pe_range]
        self.detail['pe_range'] = adj_pe_range

        if self.fs['np'] > 0:
            pe_val_range = [self.fs['np'] * adj_pe * self.sprm for adj_pe in adj_pe_range]
            # pe_val_range = [max(self.na, val) for val in pe_val_range]
            return tuple(pe_val_range)
        else:
            return None

    def __pb(self):
        print('市净率模型...')

        # self.detail['peer_pbs'] = self.peer['pb'].tolist()
        self.detail['guess_na'] = self.na
        peer = self.drop_abnormal(self.peer, 'pb', bottom=0)['pb']
        self.detail['peer_pbs'] = peer.to_list()
        pb_range = peer.min(), peer.median(), peer.max()
        adj_pb_range = [(pb * 0.7 + self.mkt['pb'] * 0.3) * (1 + self.mult_adj) for pb in pb_range]
        self.detail['pb_range'] = adj_pb_range
        pb_val_range = [int(self.na * 0.5 * adj_pb * self.sprm) for adj_pb in adj_pb_range]
        # pb_val_range = [max(self.na, val) for val in pb_val_range]
        return tuple(pb_val_range)

    def __ps(self):
        print('市销率模型...')
        # self.detail['peer_pss'] = self.peer['ps'].tolist()
        peer = self.drop_abnormal(self.peer, 'ps', bottom=0)['ps']
        self.detail['peer_pss'] = peer.to_list()
        ps_range = peer.min(), peer.median(), peer.max()
        adj_ps_range = [(ps * 0.7 + self.mkt['ps'] * 0.3) * (1 + self.mult_adj) for ps in ps_range]
        self.detail['ps_range'] = adj_ps_range
        ps_val_range = [int(self.fs['rev'] * adj_ps * self.sprm) for adj_ps in adj_ps_range]
        # ps_val_range = [max(self.na, val) for val in ps_val_range]
        return tuple(ps_val_range)

    def get(self):
        result = {'pe': self.__pe(),
                  'pb': self.__pb(),
                  'ps': self.__ps()}
        return result, self.detail
