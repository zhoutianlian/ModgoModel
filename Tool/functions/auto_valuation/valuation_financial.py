# -*- coding: utf-8 -*-：
import sys
import getopt
import warnings

from functions.multiplier_news import adjust_result_dict as new_adjust_result
from functions.multiplier_patent import adjust_result_dict as patent_adjust_result
from functions.read.read_data_for_financial import get_data_for_financial
from functions.read.get_something import get_hypothesis
from functions.save.save_data_for_financial_model import save_financial_valuation_result
from functions.indus_code_forA import retrack_Ainsudcode
from functions.listboardtime.listbordtime_forfinmodel import GetListTime
from functions.growthpotentialscore.financial import get_growth_potential_pscore
from functions.forquotation.record_multi_quotation import record_for_multiquotation
from hypothesis.wacc import WACC
from valuation_models.valuation_models_factory import ValuationModelsFactory,ValuationModels
from valuation_models.financial_valuation.summary import summary
from CONFIG.global_V import GlobalValue
import CONFIG.globalENV as gl

warnings.filterwarnings("ignore")

# java 传值

def financial_value(VID,ENV):
    gl.set_name(ENV)
    # ##获取估值数据#####
    [industry_code, pre_1year_asset, pre_2year_asset, pre_3year_asset, liability, sc, pc, financial_year, intangibleasset, minority_interest, lt_equity_investment2,usr_identity,code_list]\
        = get_data_for_financial(VID)
    # 处理数据
    new_code = retrack_Ainsudcode("indus_gr_decision_tree", industry_code)
    # ####计算
    # samuelson结果 pre_1year_asset 今年,pre_2year_asset 去年,pre_3year_asset 前年
    VMF = ValuationModelsFactory()
    SAM = VMF.choose_valuation_model(ValuationModels.FIN_SAM)
    sam_input_for_fin = {'gics_code': industry_code, 'pre_1year_asset': pre_1year_asset, 'pre_2year_asset':pre_2year_asset,
               'pre_3year_asset':pre_3year_asset,'liability':liability,'equity':sc}
    financial_samuelson_res = SAM.valuation_samuelson(sam_input_for_fin)
    try:
    # asset
        ASS = VMF.choose_valuation_model(ValuationModels.FIN_ASS)
        asset_input_for_fin = {"totalasset": pre_1year_asset, "intangibleasset": intangibleasset, "liability": liability,
                               "minority_interest": minority_interest, "lt_equity_investment2": lt_equity_investment2, 'equity':sc}
        financial_asset_res = ASS.valuation_asset(asset_input_for_fin)
    except:
        financial_asset_res = {GlobalValue.ASS_NAME: False}
    # 市场法
    M=VMF.choose_valuation_model(ValuationModels.FIN_MKT)
    financial_mkt_res=M.get_result(pre_1year_asset-liability,industry_code,pc,sc,code_list)


    # 综合结果
    SS_R, selected, proportion, scal=summary(financial_asset_res,financial_mkt_res,financial_samuelson_res,sc)
    # 使用舆情参数进行调整
    SS_R, news_multiplier = new_adjust_result(VID, SS_R)
    # 使用知识产权参数对结果进行调整
    SS_R, patent_multiplier = patent_adjust_result(VID, SS_R)
    multiplier = {"NewsMultiplier": news_multiplier, "PatentMultiplier": patent_multiplier}
    # propotion = SS_R[1]
    # SS_R = SS_R[0]
    # 获取上市时间

    cs, re, riskfree_rate = get_hypothesis(new_code)
    listtime = GetListTime(pre_1year_asset-liability, SS_R['MV_avg'], re)
    listtime_ans = listtime.get_list_time()

    # 获取上市时间（h5）
    listtime_h5=listtime.get_h5_time()

    # 获取wacc
    a = {"Dr": 0.06, "IncomeTaxR": 0.25}
    wacc = WACC(re, a, cs)

    # 得到企业成长潜力评分(H5)
    assets=[pre_1year_asset,pre_2year_asset,pre_3year_asset]
    gpscore = get_growth_potential_pscore(assets)
    flag=0
    # ####存储financial samuelson结果######
    save_financial_valuation_result(VID,re,financial_asset_res,financial_samuelson_res,financial_mkt_res,SS_R,wacc,selected,
                                    listtime_ans,gpscore,listtime_h5,flag,proportion,scal,multiplier)

    # 报价系统
    # flag = 0
    # if flag == 0:
    #     data_for_multi_quotation = {'pid': PID, 'p_avg': SS_R['p_avg'], 'MV_avg': SS_R['MV_avg'], 'indus': industry_code,
    #                             'valuation_route': GlobalValue.VALUROUTE_FIN, 'fr_year': financial_year, 'fr_month': 12,
    #                             'usr': usr_identity}
    #
    #     record_for_multiquotation(data_for_multi_quotation)

# if __name__ == '__main__':
#     financial_value(470,'test')