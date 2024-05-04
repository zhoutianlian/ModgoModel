import math
import pickle
import os

from Config.global_V import GlobalValue


class RealEstate():
    def valuation_estate(self, input_for_real_estate):
        dict_demo = {}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimal_real_estate.model")
        file_read = open(path, 'rb')
        model = pickle.load(file_read)
        lsb = input_for_real_estate["realestate_shorttermborrowings"]
        lsd = input_for_real_estate["realestate_shorttermdebenturespayable"]
        lc = input_for_real_estate["realestate_currentportionofnoncurrentliabilitiy"]
        llb = input_for_real_estate["realestate_longtermborrowings"]
        ld = input_for_real_estate["realestate_debenturespayable"]
        ltl = input_for_real_estate["realestate_totalliabilities"]
        ito = input_for_real_estate["realestate_totaloperatingrevenue"]
        natr = input_for_real_estate["realestate_income_business_income_taxes"] * input_for_real_estate["realestate_netprofit"]
        at = input_for_real_estate["realestate_totalasset"]
        demo = math.log(at, 10) - 10
        if demo >= 0:
            demo = 0
        coef = math.pow(10, demo)
        ac = input_for_real_estate["realestate_constructioninprogress"]
        bca = input_for_real_estate["building_construction_area"] * coef
        crr = input_for_real_estate["cpi_reside_rent_y"] * coef
        ltp = input_for_real_estate["land_transaction_price_m"] * coef
        laa = input_for_real_estate["land_acquisition_area_m"] * coef
        red = input_for_real_estate["real_estate_development_enterprises_funds_m"] * coef
        pce = input_for_real_estate["per_consumption_expenditure_reside"] * coef
        pcd = input_for_real_estate["per_capita_disposable_income_reside"] * coef
        sc = input_for_real_estate["equity"]

        a = lsb + lsd + lc + llb + ld
        b = natr
        c = at - ltl
        d = ltl / at
        e = bca
        f = ltp / laa
        g = red
        h = crr
        i = pce
        j = pcd
        k = ito / ac

        list_demo = [a, b, c, d, e, f, g, h, i, j, k]
        result = model.predict(list_demo)
        result = result / (1 + 0.15132256) / 1.2
        mv_avg = result
        mv_max = result * (1 + 0.13)
        mv_min = result * (1 - 0.08)
        price_max = mv_max / sc
        price_avg = mv_avg / sc
        price_min = mv_min / sc
        dict_demo["MV_avg"] = mv_avg.item()
        dict_demo["MV_max"] = mv_max.item()
        dict_demo["MV_min"] = mv_min.item()
        dict_demo["p_avg"] = price_avg.item()
        dict_demo["p_max"] = price_max.item()
        dict_demo["p_min"] = price_min.item()
        score = dict_demo["MV_avg"] / (at - ltl)
        if 1 <= score <= 4:
            dict_demo["score"] = 10
        else:
            dict_demo["score"] = 5
        ans = {GlobalValue.REAL_NAME: dict_demo}
        return ans




