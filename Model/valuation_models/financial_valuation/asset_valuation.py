import pickle
import os
import math
import numpy as np

from Config.global_V import GlobalValue


class AssetFin():
    # asset_input_for_fin = {"totalasset": pre_1year_asset, "intangibleasset": intangibleasset, "liability": liability,
    #              "minority_interest": minority_interest, "lt_equity_investment2": lt_equity_investment2, "equity":sc}

    def valuation_asset(self, ass_input_for_fin):

        dict_demo = {}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimal_bank.model")
        file_read = open(path, 'rb')
        model = pickle.load(file_read)
        ta = ass_input_for_fin["totalasset"]
        ia = ass_input_for_fin["intangibleasset"]
        tl = ass_input_for_fin["liability"]
        mi = ass_input_for_fin["minority_interest"]
        lei = ass_input_for_fin["lt_equity_investment2"]
        sc = ass_input_for_fin["equity"]
        a = 1
        b = math.log(ta - ia - tl - mi - lei)
        c = 2.85
        d = math.log(lei)
        e = math.log(mi)
        f = math.log(ia)
        list_demo = [a, b, c, d, e, f]
        result = model.predict(list_demo)
        result = np.exp(result)

        if result<=1:
            e = 0
            f = 0
            list_demo = [a, b, c, d, e, f]
            result = model.predict(list_demo)
            result = np.exp(result)

        mv_avg = result.item()
        mv_max = (result * (1 + 0.16)).item()
        mv_min = (result * (1 - 0.06)).item()
        price_max = mv_max / sc
        price_avg = mv_avg / sc
        price_min = mv_min / sc
        dict_demo["MV_avg"] = mv_avg
        dict_demo["MV_max"] = mv_max
        dict_demo["MV_min"] = mv_min
        dict_demo["p_avg"] = price_avg
        dict_demo["p_max"] = price_max
        dict_demo["p_min"] = price_min
        if mv_avg > 0 and mv_max > 0 and mv_min > 0:
            ans = {GlobalValue.ASS_NAME: dict_demo}
        else:
            ans = {GlobalValue.ASS_NAME: False}
        return ans




