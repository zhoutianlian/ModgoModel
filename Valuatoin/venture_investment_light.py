# -*- coding: utf-8 -*-：
import warnings

from Config.global_V import GlobalValue
from Tool.functions.read.read_data_for_businessmodel import read_data
from Tool.functions.save.save_data_for_VC import save_VC_result, get_score
from Tool.functions.read.read_data_for_VC import get_data
from Tool.functions.vc_round_two import get_Amount_plan
from Tool.functions.listboardtime.listbordtime_forvcmodel import GetListTime
from Tool.functions.growthpotentialscore.ventureinvestment import get_growth_potential_pscore
from Report.Log import logger
from Model.valuation_models.valuation_models_factory import ValuationModelsFactory, ValuationModels
from Model.valuation_models.venture_investment.summary import get_summary_result
from Model.business_model.business_model_score import business_model

warnings.filterwarnings("ignore")


def value(vid, *args, **kwargs):
    """
    PC端旧版风险投资模型
    :param vid:
    :param args: 备用字段
    :param kwargs: 备用字段
    :return:
    """
    [finance_plan, predict, company_scal, var_mulpA, indus_DEratio, indus_ROE, indus_re, indus_dtol,
     indus_turnover, indus_code, financialreport_year, market, ipo] = get_data(vid)

    # 使用商业模型
    try:
        for e in indus_code:
            if indus_code[e] >= 0.5:
                main_industry = e
                break
        flag = 0
        business_model_input = read_data(vid, flag)
        financial_report_data = {}
        ventureinvestment_light = 2
        business_model(vid, ventureinvestment_light, financial_report_data, business_model_input, main_industry)
    except:
        pass

    # 计算融资轮次（轮次间隔）
    remain_round = min(max(2, 6 - finance_plan['now_round']), finance_plan['Exit_year'] * 2)
    interval = finance_plan['Exit_year'] / remain_round

    # 模拟分配金额计划(最多只能有两个非零整数)
    amount_plan = get_Amount_plan(remain_round)

    # 使用各个方法进行估值
    VMF = ValuationModelsFactory()
    SAM = VMF.choose_valuation_model(ValuationModels.VI_SAM)
    NOR = VMF.choose_valuation_model(ValuationModels.VI_NOR)
    ans_normal = NOR.get_VC2(predict, finance_plan, var_mulpA, indus_DEratio, indus_re, amount_plan,
                             GlobalValue.MUTILPLIER,
                             interval,
                             remain_round)
    ans_samuelson = {}
    if company_scal['L'] != 0:
        ans_samuelson = SAM.get_samuelson_results(predict, finance_plan, company_scal, indus_DEratio, indus_dtol,
                                                  indus_re,
                                                  indus_turnover, amount_plan, GlobalValue.MUTILPLIER, interval,
                                                  remain_round)
    summary_result = get_summary_result(ans_normal, ans_samuelson)
    # 如果结果失效，则返回估值失败的信号
    if summary_result == False:
        logger(2, 'False')
        exit()
    # 添加评分
    summary_result = get_score(summary_result, company_scal["TA"], company_scal["L"])
    # # 使用舆情参数进行调整
    # summary_result, news_multiplier = new_adjust_result(VID, summary_result)
    # # 使用知识产权参数对结果进行调整
    # summary_result, patent_multiplier = patent_adjust_result(VID, summary_result)
    # multiplier = {"NewsMultiplier": news_multiplier, "PatentMultiplier": patent_multiplier}
    # 获得上市时间
    listtime = GetListTime(company_scal['TA'] - company_scal['L'], summary_result['avg'], indus_re)

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

    # 得到企业成长潜力评分(H5)
    gpscore = get_growth_potential_pscore(summary_result, indus_re)

    # 存数据库
    save_VC_result(vid, ans_normal, ans_samuelson, summary_result, listtime_ans, gpscore, listtime_h5, 0, ipo)

    return "SUCCESS"

    # 报价系统
    # flag=0
    # if flag==0:
    #     # 多公司报价记录
    #     data_for_multi_quotation = {'pid': PID, 'p_avg': summary_result['MV_avg']/campany_scal['Contributed_Capital'],
    #                             'MV_avg': summary_result['MV_avg'],
    #                             'indus': indus_code,'valuation_route': GlobalValue.VALUROUTE_VI,
    #                             'fr_year': financialreport_year,
    #                             'fr_month': 12,
    #                             'usr': usr_identity}
    #
    #     record_for_multiquotation(data_for_multi_quotation)
    #     #re备用
    #     backup_re_forquotation_vi(predict,finance_plan,var_mulpA,var_mulp3,indus_DEratio,amount_plan,interval,remain_round,
    #                           campany_scal,indus_dtol,indus_turnover,PID)

# value(4237,'test')
