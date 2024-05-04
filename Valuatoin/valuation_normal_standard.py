# -*- coding: utf-8 -*-：
from Config.global_V import GlobalValue
from Model.valuation_models.normal_valuation.summary import summary
from Model.valuation_models.valuation_models_factory import ValuationModels,ValuationModelsFactory
from Model.financial_report_model.standard_model import ForcastFR
from Tool.functions.processs_standard_data import process_data
from Tool.functions import indus_code_forA as indc
from Tool.functions.read.read_data_for_standard_var import get_cplx_data
from Tool.functions.save.save_data_for_standard_var import save_data
from Tool.functions.listboardtime.listbordtime_forsimplemodel import GetListTime
from Tool.functions.growthpotentialscore.normal import get_growth_potential_pscore
from Tool.hypothesis.wacc import WACC
from Tool.hypothesis.perpetuity_g import perpetuity_g
from Model.business_model.business_model_score import business_model


def value(PID):
    [adinfo_data, year_FR, month_FR, indus_code, CS, re, pc_A, pc_3, pc_pbp, pc_pep, pc_evsp, exitY, bestY, exitYpc,
     TVpc, perpetuity_g_basic, perpetuity_eva_pc,perpetuity_ri_pc, M_pc, perpetuity_g_pc, perpetuity_ed_pc,
     fr_year, fr_month, usr_identity, RISK_FREE] = get_cplx_data(PID)

    # 行业上溯：
    new_code = indc.retrack_Ainsudcode(indus_code)
    adinfo_data['Indus_code']=new_code
    # 财报预测
    # 数据处理
    if not month_FR['year']:
        d = process_data(year_FR, adinfo_data)
    else:
        d = process_data(year_FR, adinfo_data, month_FR)

    A = ForcastFR(d)
    a = A.Output()
    FFR = A.FFR()
    GR = A.FGR()

    # 调用商模
    try:
        for e in new_code:
            if new_code[e] >= 0.5:
                main_industry = e
                break

        if not month_FR['year']:
            financial_report_data = {'Rev': d['inputs1']['Rev'], 'NI': d['inputs1']['NI'],
                                     'saleexp': year_FR['销售费用'][-1],
                                     'Totalcost': d['inputs1']['Cost']}
        else:
            month = month_FR['end_month'][0]
            coefficent = (12 - month) / 12
            financial_report_data = {'Rev': d['inputs1']['Rev'], 'NI': d['inputs1']['NI'],
                                     'saleexp': month_FR['销售费用'][-1] +
                                                year_FR['销售费用'][-1] * coefficent,
                                     'Totalcost': d['inputs1']['Cost']}
        standard = 1
        business_model(PID, standard, financial_report_data, main_industry)
    except:
        pass

    VMF = ValuationModelsFactory()

    # 兜底算法
    if d['inputs1']['L']>=0:
        inputs_forcost = {'NI': d['inputs1']['NI'], 'Rev': year_FR['营业总收入'], 'AR': d['inputs1']['AR'],
                      'Inv': d['inputs1']['Inv'],
                      'AP': d['inputs1']['AP'], 'Cash': d['inputs1']['Cash'], 'TA': d['inputs1']['TA'],
                      'L': d['inputs1']['L'],
                      'SC': d['inputs1']['SC']}

        C = VMF.choose_valuation_model(ValuationModels.NOR_COST)
        Cost_R = C.get_output(inputs_forcost)
    else:
        Cost_R = {'MV_max': (d['inputs1']['TA'] - d['inputs1']['L']) * 1.2, 'MV_avg': d['inputs1']['TA'] - d['inputs1']['L'],
                  'MV_min': (d['inputs1']['TA'] - d['inputs1']['L']) * 0.8,
                  'p_max': (d['inputs1']['TA'] - d['inputs1']['L']) * 1.2 / d['inputs1']['SC'],
                  'p_avg': (d['inputs1']['TA'] - d['inputs1']['L']) / d['inputs1']['SC'],
                  'p_min': (d['inputs1']['TA'] - d['inputs1']['L']) * 0.8 / d['inputs1']['SC']}
    # [re,riskless]=get_re(a,new_code)

    # Wacc
    # re=0.15
    wacc = WACC(re, a, CS)
    try:
        # Samuelson
        SAM = VMF.choose_valuation_model(ValuationModels.NOR_SAM_STANDARD)
        sam_input_norstandard={'asset3':d['inputs1']['TA'],'asset2':d['inputs1']['TA_rest'][1],
                           'asset1':d['inputs1']['TA_rest'][0],'debt':d['inputs1']['Debt'],
                           'liabi': d['inputs1']['L'],'wacc':wacc['wacc_avg'],'interestrate':RISK_FREE,
                           'induscode':indus_code,'SC':d['inputs1']['SC']}
        samuelson_result = SAM.valuation_samuelson(sam_input_norstandard)
    except:
        samuelson_result = {GlobalValue.SAM_NAME: False}
    # for_market 市场法
    pc = {'pc_A': pc_A, 'pc_3': pc_3, 'pc_pbp': pc_pbp, 'pc_pep': pc_pep, 'pc_evsp': pc_evsp}

    M = VMF.choose_valuation_model(ValuationModels.NOR_MKT)
    M.compute(a, pc, indus_code, new_code, Cost_R)
    market_R = M.get_result()
    Mkt_output = M.get_outPut()
    # 市场法传出参数
    MVIC_NOPAT = Mkt_output['EV_NOPAT']  # EV/NOPAT
    std_MVIC_NOPAT = Mkt_output['std_EV_NOPAT']
    m_MVIC_NOPAT = Mkt_output['m_EV_NOPAT']
    range_std = Mkt_output['range_std']
    if d['inputs1']['EBT'] == 0 and d['inputs1']['debt'] == 0:
        NO_R = {}
        RI_R = {}
        EV_R = {}
    else:
        # 绝对估值法
        # for_nopat
        [perpetuity_g_a, perpetuity_g_b, perpetuity_g_c] = perpetuity_g(perpetuity_g_basic)  # 写死
        forN = {'perpetuity_g_c': perpetuity_g_c, 'perpetuity_g_b': perpetuity_g_b, 'perpetuity_g_a': perpetuity_g_a,
                'MVIC/NOPAT': MVIC_NOPAT, 'std_MVIC/NOPAT': std_MVIC_NOPAT, 'm_MVIC/NOPAT': m_MVIC_NOPAT,
                'exitY': exitY, 'bestY': bestY, 'exitYpc': exitYpc, 'TVpc': TVpc, 'perpetuity_g_pc': perpetuity_g_pc,
                'perpetuity_ed_pc': perpetuity_ed_pc, 'range_std': range_std, 'M_pc': M_pc}
        NO = VMF.choose_valuation_model(ValuationModels.NOR_NOPAT)
        NO_R = NO.get_output(a, wacc, forN, Cost_R)
        # for_ri
        forRi = {'exitY': exitY, 'bestY': bestY, 'exitYpc': exitYpc, 'TVpc': TVpc, 'perpetuity_ri_pc': perpetuity_ri_pc}
        RI = VMF.choose_valuation_model(ValuationModels.NOR_RIM)
        RI_R = RI.get_output(a, wacc, forRi, Cost_R)
        # for_eva
        forEva = {'exitY': exitY, 'bestY': bestY, 'exitYpc': exitYpc, 'TVpc': TVpc,
                  'perpetuity_eva_pc': perpetuity_eva_pc}

        EV = VMF.choose_valuation_model(ValuationModels.NOR_EVA)
        EV_R = EV.get_output(a, wacc, forEva, Cost_R)

        # for_apv
        forApv = {'bestY': bestY, 'exitYpc': exitYpc, 'TVpc': TVpc, "perpetuity_g_b": perpetuity_g_b,
                  "risk_free": RISK_FREE, "rc": 0.30, "t": 3.00}
        APV = VMF.choose_valuation_model(ValuationModels.NOR_APV)
        APV_R = APV.get_output(a, wacc, forApv, Cost_R)

    # summary 选择汇总算法
    abs_R = {'rim': RI_R, 'eva': EV_R, 'nopat': NO_R}

    [SS_R, selected, proportion] = summary(abs_R, market_R,samuelson_result, d['inputs1']['SC'])

    # 得到距离上市时间
    listtime=GetListTime(d['inputs1']['E'], d['inputs1']['NI'], FFR['e_totalshareholdersequity'],
                           SS_R['MV_avg'], re, FFR['is_netprofit'], FFR['is_operatingrevenue'], d['inputs1']['Rev'])
    listtime_ans = listtime.get_list_time()

    # 获取上市时间（h5）
    listtime_h5 = listtime.get_h5_time()

    # 得到企业成长潜力评分(H5)
    gpscore=get_growth_potential_pscore(GR)

    # 存数据
    # 1.存各种系统内固定好的参数
    para = [pc_A, pc_3, pc_pbp, pc_pep, pc_evsp, exitY, bestY, exitYpc, TVpc, perpetuity_g_basic, perpetuity_eva_pc,
            perpetuity_ri_pc, M_pc, perpetuity_g_pc, perpetuity_ed_pc]
    # 2.存市场法算出的参数
    if type(range_std) != bool:
        market_para = [range_std.item(), MVIC_NOPAT.item(), std_MVIC_NOPAT.item(), m_MVIC_NOPAT.item()]
    else:
        market_para = [None, None, None, None]

    save_data(PID, abs_R, market_R,samuelson_result, SS_R, wacc, para, FFR, selected, GR, market_para,listtime_ans,
              gpscore,listtime_h5,proportion)

    # 报价系统
    # flag = 0
    # if flag == 0:
    #     # 多公司报价记录
    #     data_for_multi_quotation = {'pid': PID, 'p_avg': SS_R['p_avg'], 'MV_avg': SS_R['MV_avg'], 'indus': indus_code,
    #                                 'valuation_route': GlobalValue.VALUROUTE_CMPLX, 'fr_year': fr_year, 'fr_month': fr_month,
    #                                 'usr':usr_identity}
    #     record_for_multiquotation(data_for_multi_quotation)
    #     # re备用
    #     backup_re_forquotation_abs(a, forN, forRi, forEva, Cost_R, CS, PID, flag, abs_R)
    #     backup_re_forquotation_sam(ValuationModels.NOR_SAM_LITE, sam_input_norstandard, a, CS, PID, flag)


# value(99,'test')
