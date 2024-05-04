# -*- coding: utf-8 -*-：
# ZXW
import getopt
import sys
import warnings

from functions.multiplier_news import adjust_result_dict as new_adjust_result
from functions.multiplier_patent import adjust_result_dict as patent_adjust_result
from financial_report_model.light_model import ForcastFR
from functions import indus_code_forA as indc
from functions.read.get_something import get_FFR
from functions.read.read_data_for_businessmodel import read_data
from functions.read.read_data_for_light_val import get_data_for_simplemodel
from functions.save.save_data_for_light_val import save_data
from functions.listboardtime.listbordtime_forsimplemodel import GetListTime
from functions.growthpotentialscore.normal import get_growth_potential_pscore
from functions.forquotation.record_multi_quotation import record_for_multiquotation
from functions.forquotation.rebackup import backup_re_forquotation_abs,backup_re_forquotation_sam
from hypothesis.dlol_re_adjust import dlol_re_adjust
from hypothesis.wacc import WACC
from hypothesis.perpetuity_g import perpetuity_g
from valuation_models.valuation_models_factory import ValuationModelsFactory,ValuationModels
import valuation_models.normal_valuation.summary as s
import CONFIG.globalENV as gl
from CONFIG.global_V import GlobalValue
from business_model.business_model_score import business_model

warnings.filterwarnings("ignore")

# Dr 贷款利率
# AP 应付账款
# debt 贷款
# Cash 现金
# Inv 存货
# AR 应收账款
# TA 总资产
# L 总负债
# SC 股本
# NI 净利润
# EBIT 营业利润
# EBT 总利润
# Rev 营业收入（[当前，前一年，前两年]）

# java 传值


def value(VID,ENV):
      gl.set_name(ENV)
      # 从数据库得到值
      [Dr,AP,debt,Cash,Inv,AR,TA,L,SC,NI,EBIT,EBT,Rev,indus_code,pc_A,pc_3,pc_pbp,
       pc_pep,pc_evsp,exitY,bestY,exitYpc,TVpc,perpetuity_g_basic,perpetuity_eva_pc,
       perpetuity_ri_pc,M_pc,perpetuity_g_pc,perpetuity_ed_pc,CS,Rev_adjustment,flag,
       re,financialreport_year,usr_identity,riskfree_rate,code_list]=get_data_for_simplemodel(VID)

      # 财报预测
      Input={'Indus_code':indus_code,'TA':TA,'Cash':Cash,'AR':AR,'Inv':Inv,'debt':debt,'Dr':Dr,'AP':AP,'L':L,'Rev':Rev,'EBIT':EBIT,'EBT':EBT,'NI':NI,'SC':SC,'Rev_adj':Rev_adjustment}
      A=ForcastFR(Input)
      a=A.Output()
      a["riskfree_rate"] = riskfree_rate
      FFR=A.FFR()
      GR=A.FGR()
      FFR = get_FFR(GR, FFR)
      # 调用商模
      try:
            for e in indus_code:
                  if indus_code[e] >= 0.5:
                        main_industry = e
                        break
            business_model_input = read_data(VID, flag)
            financial_report_data = {'Rev': Rev[-1], 'NI': NI, 'Totalcost': a['Optcost']}

            light = 0
            business_model(VID, light, financial_report_data, business_model_input, main_industry)
      except:
            pass
      VMF=ValuationModelsFactory()
      # 兜底算法
      if L>=0:
            C=VMF.choose_valuation_model(ValuationModels.NOR_COST)
            Cost_R=C.get_output(Input)
      else:
            Cost_R = {'MV_max': (TA - L) * 1.2, 'MV_avg': TA - L, 'MV_min': (TA - L) * 0.8,
                      'p_max': (TA - L) * 1.2 / SC,
                      'p_avg': (TA - L) / SC, 'p_min': (TA - L) * 0.8 / SC}
      capital_market = business_model_input["capital_market"]
      re = dlol_re_adjust(re, NI, FFR, Rev, capital_market)
      # Wacc
      wacc=WACC(re,a,CS)
      # Samuelson 期权法
      try:
            SAM=VMF.choose_valuation_model(ValuationModels.NOR_SAM_LITE)
            sam_input_norlite={'asset':TA,'sales3':Rev[2],'sales2':Rev[1],'sales1':Rev[0],'debt':debt,'liabi':L,
                         'wacc':wacc['wacc_avg'],'interestrate':riskfree_rate,'induscode':indus_code,
                         'SC':SC}
            samuelson_result=SAM.valuation_samuelson(sam_input_norlite)
      except:
            samuelson_result = {GlobalValue.SAM_NAME: False}
      # for_market 市场法
      pc={'pc_A': pc_A,'pc_3': pc_3, 'pc_pbp': pc_pbp, 'pc_pep': pc_pep, 'pc_evsp': pc_evsp}
      args = {"capital_market": capital_market, "indus_code": indus_code}
      M=VMF.choose_valuation_model(ValuationModels.NOR_MKT)
      M.compute(a, pc, indus_code, Cost_R, args, code_list)
      market_R, peer_list = M.get_result()
      Mkt_output=M.get_outPut()
      # 市场法传出参数
      MVIC_NOPAT=Mkt_output['EV_NOPAT']  ##EV/NOPAT
      std_MVIC_NOPAT=Mkt_output['std_EV_NOPAT']
      m_MVIC_NOPAT=Mkt_output['m_EV_NOPAT']
      range_std=Mkt_output['range_std']
      para_from_apv = {}
      if Input['EBT']==0 and Input['debt']==0:
            NO_R={}
            RI_R={}
            EV_R={}
            APV_R = {}
      else:
            # 绝对估值法
            # forNopat
            [perpetuity_g_a,perpetuity_g_b,perpetuity_g_c]=perpetuity_g(perpetuity_g_basic)  #写死
            forN={'perpetuity_g_c':perpetuity_g_c,'perpetuity_g_b':perpetuity_g_b,'perpetuity_g_a':perpetuity_g_a,'MVIC/NOPAT':MVIC_NOPAT,'std_MVIC/NOPAT':std_MVIC_NOPAT,'m_MVIC/NOPAT':m_MVIC_NOPAT,
                  'exitY':exitY,'bestY':bestY,'exitYpc':exitYpc,'TVpc':TVpc,'perpetuity_g_pc':perpetuity_g_pc,'perpetuity_ed_pc':perpetuity_ed_pc,'range_std':range_std,'M_pc':M_pc}
            NO=VMF.choose_valuation_model(ValuationModels.NOR_NOPAT)
            NO_R=NO.get_output(a,wacc,forN,Cost_R)
            # for_ri
            forRi={'exitY':exitY,'bestY':bestY,'exitYpc':exitYpc,'TVpc':TVpc,'perpetuity_ri_pc':perpetuity_ri_pc}
            RI=VMF.choose_valuation_model(ValuationModels.NOR_RIM)
            RI_R=RI.get_output(a, wacc, forRi, Cost_R)
            # for_eva
            forEva={ 'exitY':exitY,'bestY':bestY,'exitYpc':exitYpc,'TVpc':TVpc,'perpetuity_eva_pc':perpetuity_eva_pc}
            EV=VMF.choose_valuation_model(ValuationModels.NOR_EVA)
            EV_R=EV.get_output(a, wacc, forEva, Cost_R)
            # for_apv
            forApv = {'bestY': bestY, 'exitYpc': exitYpc, 'TVpc': TVpc, "perpetuity_g_b": perpetuity_g_b,
                      "risk_free": riskfree_rate, "rc": 0.30, "t": 3.00}
            APV = VMF.choose_valuation_model(ValuationModels.NOR_APV)
            APV_R, para_from_apv = APV.get_output(a, wacc, forApv, Cost_R)

      # summary 选择汇总算法
      abs_R={'AE':RI_R,'EVA':EV_R,'NOPAT':NO_R, "APV":APV_R}
      [SS_R,selected, proportion, scal]=s.summary(abs_R,market_R,samuelson_result,SC)
      # 使用舆情参数进行调整
      SS_R, news_multiplier = new_adjust_result(VID, SS_R)
      # 使用知识产权参数对结果进行调整
      SS_R, patent_multiplier = patent_adjust_result(VID, SS_R)
      multiplier = {"NewsMultiplier": news_multiplier, "PatentMultiplier": patent_multiplier}
      # 得到据上市时间
      listtime = GetListTime(TA - L, NI, FFR['E'], SS_R['MV_avg'], re, FFR['NI'], FFR['Rev'], Rev[-1])
      listtime_ans = listtime.get_list_time()

      # 获取上市时间（h5）
      listtime_h5 = listtime.get_h5_time()

      # 得到企业成长潜力评分(H5)
      gpscore = get_growth_potential_pscore(GR)

      # 存数据
      # 1.存各种系统内固定好的参数
      para=[pc_A,pc_3,pc_pbp,pc_pep,pc_evsp,exitY,bestY,exitYpc,TVpc,perpetuity_g_basic,perpetuity_eva_pc,perpetuity_ri_pc,M_pc,perpetuity_g_pc,perpetuity_ed_pc]
      # 2.存市场法算出的参数
      if type(range_std)!=bool:
            market_para=[range_std.item(),MVIC_NOPAT.item(),std_MVIC_NOPAT.item(),m_MVIC_NOPAT.item()]
      else:
            market_para=[None,None,None,None]

      save_data(str(VID),abs_R,market_R,samuelson_result,SS_R,wacc,a,para,FFR,flag,market_para,listtime_ans,gpscore,listtime_h5,proportion,scal, peer_list,para_from_apv,multiplier)

      # 报价系统
      # if flag == 0:
      #       # 多公司报价记录
      #       data_for_multi_quotation={'pid':PID,'p_avg':SS_R['p_avg'],'MV_avg':SS_R['MV_avg'],'indus':indus_code,
      #                           'valuation_route':GlobalValue.VALUROUTE_LITE,'fr_year':financialreport_year,'fr_month':12,
      #                           'usr':9}
      #       record_for_multiquotation(data_for_multi_quotation)
      #       # re备用va
      #       backup_re_forquotation_abs(a,forN,forRi,forEva,forApv,Cost_R,CS,PID,flag,abs_R)
      #       backup_re_forquotation_sam(ValuationModels.NOR_SAM_LITE,sam_input_norlite,a,CS,PID,flag)

#
# if __name__ == '__main__':
#       value(170,'develop')
