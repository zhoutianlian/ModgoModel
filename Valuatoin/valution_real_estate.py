# -*- coding: utf-8 -*-：
import random
import warnings

from Tool.functions.multiplier_news import adjust_result_dict as new_adjust_result
from Tool.functions.multiplier_patent import adjust_result_dict as patent_adjust_result
from Tool.functions.read.read_data_for_real_estate import get_data_for_real_estate
from Tool.functions.save.save_data_for_real_estate_model import save_real_estate_valuation_result
from Tool.functions.listboardtime.listbordtime_forfinmodel import GetListTime
from Tool.hypothesis.wacc import WACC
from Model.valuation_models.valuation_models_factory import ValuationModelsFactory, ValuationModels

warnings.filterwarnings("ignore")


def real_estate_value(vid, *args, **kwargs):
    """
    PC端旧版房地产公司估值
    :param vid:
    :param args: 备用字段
    :param kwargs: 备用字段
    :return:
    """
    # ##获取估值数据#####
    [industry_code, shorttermborrowings, shorttermdebenturespayable,
     currentportionofnoncurrentliabilitiy,
     longtermborrowings, debenturespayable,
     income_business_income_taxes, net_profit,
     totalasset, totalliabilities, totaloperatingrevenue,
     constructioninprogress, sc,
     building_construction_area, cpi_reside_rent_y, land_transaction_price_m, land_acquisition_area_m,
     real_estate_development_enterprises_funds_m, per_consumption_expenditure_reside,
     per_capita_disposable_income_reside, pc, financial_year, cs, re, riskfree_rate, market, ipo] = get_data_for_real_estate(
        vid)
    # ####计算
    # real_estate
    VMF = ValuationModelsFactory()
    REAL_ESTATE = VMF.choose_valuation_model(ValuationModels.REAL_ESTATE)
    input_for_real_estate = {'realestate_shorttermborrowings': shorttermborrowings,
                             'realestate_shorttermdebenturespayable': shorttermdebenturespayable,
                             'realestate_currentportionofnoncurrentliabilitiy': currentportionofnoncurrentliabilitiy,
                             'realestate_longtermborrowings': longtermborrowings, 'equity': sc,
                             "realestate_debenturespayable": debenturespayable,
                             "realestate_income_business_income_taxes": income_business_income_taxes,
                             "realestate_totalasset": totalasset, "realestate_netprofit": net_profit,
                             "realestate_totalliabilities": totalliabilities,
                             "realestate_totaloperatingrevenue": totaloperatingrevenue,
                             "realestate_constructioninprogress": constructioninprogress,
                             "building_construction_area": building_construction_area,
                             "cpi_reside_rent_y": cpi_reside_rent_y,
                             "land_transaction_price_m": land_transaction_price_m,
                             "land_acquisition_area_m": land_acquisition_area_m,
                             "real_estate_development_enterprises_funds_m": real_estate_development_enterprises_funds_m,
                             "per_consumption_expenditure_reside": per_consumption_expenditure_reside,
                             "per_capita_disposable_income_reside": per_capita_disposable_income_reside}
    real_estate_res = REAL_ESTATE.valuation_estate(input_for_real_estate)

    # 综合结果
    # [SS_R, show_in_page]=summary(real_estate_res,{},{},sc)
    SS_R = real_estate_res["var_real_estate"]
    # 使用舆情参数进行调整
    SS_R, news_multiplier = new_adjust_result(vid, SS_R)
    # 使用知识产权参数对结果进行调整
    SS_R, patent_multiplier = patent_adjust_result(vid, SS_R)
    multiplier = {"NewsMultiplier": news_multiplier, "PatentMultiplier": patent_multiplier}
    show_in_page = ["var_real_estate", False, False]

    # 获取上市时间
    listtime = GetListTime(totalasset - totalliabilities, SS_R['MV_avg'], re)

    # 获取上市时间（h5）
    listtime_h5 = listtime.get_h5_time()
    from Config.Type import market_type
    if ipo:
        listtime_ans = list(ipo.items())[0]
    else:
        if market == 5:
            listtime_ans = listtime.get_list_time()
        else:
            listtime_ans = [market_type[market], 0]


    # 获取wacc
    a = {"Dr": 0.06, "IncomeTaxR": 0.25}
    wacc = WACC(re, a, cs)

    # 得到企业成长潜力评分(H5)
    # assets=[pre_1year_asset,pre_2year_asset,pre_3year_asset]
    # gpscore = get_growth_potential_pscore(assets)
    gpscore = random.randint(50, 99)
    # 存储financial samuelson结果######
    save_real_estate_valuation_result(vid, real_estate_res, SS_R, wacc,
                                      listtime_ans, gpscore, listtime_h5, 0, multiplier, ipo)
    return "SUCCESS"

# real_estate_value(4404,'test')
