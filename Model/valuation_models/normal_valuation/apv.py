import math
import numpy as np
from scipy import stats

from Tool.functions.base_protect import BaseProtect as bp
from Tool.functions.is_result_legal import result_legal


class APV:
    def __compute(self, output, wacc, forapv, cost_result):
        # 通用计算 准备数据
        fcff_list = []
        a_fcffc = 0
        a_fcffb = 0
        a_fcffa = 0
        s_fcff_b = []
        nb_fcff_c = []
        nb_fcff_b = []
        nb_fcff_a = []
        for y in range(len(output['NOPAT'])): # 10+1
            grc = 0
            grb = forapv["perpetuity_g_b"][y]
            gra = grb * 2
            dfc = 1.0/math.pow((1+wacc['re_min']), y)
            dfb = 1.0/math.pow((1+wacc['re_avg']), y)
            dfa = 1.0/math.pow((1+wacc['re_max']), y)
            fcff = output["NOPAT"][y]
            nopatc = fcff * dfc
            nopatb = fcff * dfb
            nopata = fcff * dfa
            fcffc = nopatc
            fcffb = nopatb
            fcffa = nopata
            a_fcffc += fcffc
            a_fcffb += fcffb
            a_fcffa += fcffa
            c_fcffc = (fcff * (1 + grc)) / (wacc["re_min"] - grc)
            c_fcffb = (fcff * (1 + grb)) / (wacc["re_avg"] - grb)
            c_fcffa = (fcff * (1 + gra)) / (wacc["re_max"] - gra)
            s_fcffc = c_fcffc * dfc
            s_fcffb = c_fcffb * dfb
            s_fcffa = c_fcffa * dfa
            nb_fcffc = a_fcffc + s_fcffc
            nb_fcffb = a_fcffb + s_fcffb
            nb_fcffa = a_fcffa + s_fcffa
            fcff_list.append(fcff)
            s_fcff_b.append(s_fcffb)
            nb_fcff_c.append(nb_fcffc)
            nb_fcff_b.append(nb_fcffb)
            nb_fcff_a.append(nb_fcffa)

        sum_tax = []
        to_i_tax = 0
        from_i_tax_list = []
        # 借款预期税收收益
        if output["Dr"] < 0.06:
            output["Dr"] = 0.06
        for y in range(len(output['NOPAT'])): # 10+1
            c_tax = output["Debt"][y] * output["IncomeTaxR"] * output["Dr"]
            PV = c_tax / math.pow(1 + output["Dr"], y)
            to_i_tax += c_tax
            from_i_tax = c_tax / (output["Dr"] * math.pow(1 + output["Dr"], y))
            sum_tax.append(to_i_tax + from_i_tax)
            from_i_tax_list.append(from_i_tax)
        # 预期破产成本与净影响
        d2_list = []
        Nd2_list = []
        rp_list = []
        rc_coef_list = []
        stdev_gr = np.std(output["GR_APV"], ddof=1)
        for y in range(len(output['NOPAT'])): # 10+1
            if y == 0:
                a = output["Debt"][y] / output["L"]
                rl = (output["Dr"] + forapv["risk_free"]) * a
                d2 = (np.log(output["A"][y]/output["L"]) + (rl - stdev_gr * stdev_gr / 2) * forapv["t"]) / (stdev_gr * math.sqrt(forapv["t"]))
                Nd2 = stats.norm.cdf(d2)
                rp = 1 - Nd2
                rc_coef = rp * forapv["rc"]
            else:
                d2 = d2_list[y-1]
                Nd2 = Nd2_list[y-1]
                rp = rp_list[y-1]
                rc_coef = rc_coef_list[y-1]
            d2_list.append(d2)
            Nd2_list.append(Nd2)
            rp_list.append(rp)
            rc_coef_list.append(rc_coef)

        tv_b_list = []
        big_tv_c_list = []
        big_tv_b_list = []
        big_tv_a_list = []
        for y in range(len(output['NOPAT'])): # 10+1
            tv_c = nb_fcff_c[y] + sum_tax[y]
            tv_b = nb_fcff_b[y] + sum_tax[y]
            tv_a = nb_fcff_a[y] + sum_tax[y]
            tvb_c = tv_c * (1 - rc_coef_list[y])
            tvb_b = tv_b * (1 - rc_coef_list[y])
            tvb_a = tv_a * (1 - rc_coef_list[y])
            big_tv_c = max(output["NetDebt"][0], tvb_c)
            big_tv_b = max(output["NetDebt"][0], tvb_b)
            big_tv_a = max(output["NetDebt"][0], tvb_a)
            big_tv_c_list.append(big_tv_c)
            big_tv_b_list.append(big_tv_b)
            big_tv_a_list.append(big_tv_a)
            tv_b_list.append(tv_b)
        # 子模型评分
        submod = {}
        submod["fix_gr"] = {}
        SM_b_list = []
        for y in range(len(output['NOPAT'])): # 10+1
            submod["fix_gr"][y] = {}
            TV = s_fcff_b[y] + from_i_tax_list[y]
            a = bool(y > 0 and (fcff_list[y] != 0, output["A"][y] > 0, output["E+debt"][y] > 0, TV > 0))
            SM_c = big_tv_c_list[y] / fcff_list[0]
            SM_b = big_tv_b_list[y] / fcff_list[0]
            SM_a = big_tv_a_list[y] / fcff_list[0]
            s_TVM = TV / tv_b_list[y]
            if y > 0:
                sensi_exitY = abs((SM_b - SM_b_list[y-1]) / SM_b)
                sensi_Hy = abs((SM_a - SM_c) / (2 * SM_b))
                sensi_score = sensi_exitY + sensi_Hy
                exitYps = math.pow(y-forapv["bestY"], 2) * forapv["exitYpc"]
                s_TVM_score = s_TVM * forapv["TVpc"]
                submod["fix_gr"][y]["score"] = a / (sensi_score*sensi_score + exitYps*exitYps + s_TVM_score*s_TVM_score)
                submod["fix_gr"][y]["SC"] = output["SC"]
                submod["fix_gr"][y]["TVM"] = s_TVM
                submod["fix_gr"][y]["MV_avg"] = big_tv_b_list[y]
                submod["fix_gr"][y]["MV_min"] = big_tv_c_list[y]
                submod["fix_gr"][y]["MV_max"] = big_tv_a_list[y]
                submod["fix_gr"][y]["p_avg"] = submod["fix_gr"][y]["MV_avg"] / submod["fix_gr"][y]["SC"]
                submod["fix_gr"][y]["p_min"] = submod["fix_gr"][y]["MV_min"] / submod["fix_gr"][y]["SC"]
                submod["fix_gr"][y]["p_max"] = submod["fix_gr"][y]["MV_max"] / submod["fix_gr"][y]["SC"]
                for key, value in submod.items():
                    # if key > 0:
                    for a, b in value.items():
                        if a > 0:
                            [b['MV_max'], b['MV_avg'], b['MV_min']] = \
                                bp(b['MV_max'], b['MV_avg'], b['MV_min'], cost_result['MV_max'],
                                   cost_result['MV_avg'], cost_result['MV_min'])
                            # ###阈值判断 错误值检验
                            # submod["model_first"].pop(0)
                            if not result_legal('apv' + "fix_gr", submod["fix_gr"][y]):
                                submod["fix_gr"][y]['score'] = 0
                            ####评分调整
                            if b['MV_max'] == cost_result['MV_max'] and b['MV_avg'] == cost_result['MV_avg'] and \
                                    b['MV_min'] == cost_result['MV_min']:
                                b['score'] = 0.000001
            SM_b_list.append(SM_b)

        score_list = []
        for key, value in submod["fix_gr"].items():
            if key > 0:
                if value["score"] > 100:
                    value["score"] = 100
                score_list.append(value["score"])
        score = max(score_list)
        year = score_list.index(score) + 1
        self.__apv_value = {}
        self.__apv_value["fix_gr"] = submod["fix_gr"][year]
        for key, value in self.__apv_value["fix_gr"].items():
            if key in ["score", "TVM"]:
                self.__apv_value["fix_gr"][key] = round(self.__apv_value["fix_gr"][key], 6)
            else:
                self.__apv_value["fix_gr"][key] = round(self.__apv_value["fix_gr"][key], 2)
        self.__apv_value["fix_gr"]["ExitY"] = year
        for i in self.__apv_value["fix_gr"].keys():
            if type(self.__apv_value["fix_gr"][i]) is np.float64:
                self.__apv_value["fix_gr"][i] = self.__apv_value["fix_gr"][i].item()
        # self.__apv_value["model_first"]["score"] = self.__apv_value["model_first"]["score"].item()
        # self.__apv_value["model_first"]["p_avg"] = self.__apv_value["model_first"]["p_avg"].item()
        # self.__apv_value["model_first"]["p_min"] = self.__apv_value["model_first"]["p_min"].item()
        # self.__apv_value["model_first"]["p_max"] = self.__apv_value["model_first"]["p_max"].item()
        self.para = {}
        self.para["rp"] = rp_list[0]
        self.para["stdev_gr"] = stdev_gr
    def get_output(self, output, wacc, forapv, cost_result):
        self.__compute(output, wacc, forapv, cost_result)

        return self.__apv_value, self.para
