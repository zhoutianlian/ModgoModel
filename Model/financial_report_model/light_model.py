# -*- coding: utf-8 -*-：
import copy

from Tool.hypothesis.mgr import get_MGR
from Tool.hypothesis.NextNineGrowthRate import get_GR9
from Report.Log import logger

# year 预测报表的年度
# TA	总资产
# Cash	现金
# AR	应收账款
# Inv	存货
# debt	借款
# Dr	借款利率
# AP	应付账款
# L	总负债
#
# Rev	营业收入
# EBIT	营业利润
# EBT	利润总额
# NI	净利润
#
# SC	股本
#
#
# GR	分析：营业收入增长率
# get_MGR(GR)	代入>>公司增长率模型
# MGR	获取：次年营业收入增长率
# get_FutureGR(MGR,year)	代入>>增长缩减模型
# FGR	获取：未来5年营业收入增长率
#
# FFR.Rev	计算：未来5年营业收入
# interstExp	分析：利息支出
# OptCost	分析：营业成本
# OptCostM	分析：营业成本率
# FFR.OptCost	计算：营业成本
# FFR.EBIT	计算：未来5年营业利润
# PftRBT	分析：税前利润率
# FFR.EBT	计算：未来5年利润总额
# IncomeTaxR	分析：所得税率
# FFR.Tax	计算：未来5年所得税
# FFR.NI	计算：未来5年净利润
#
#
# ARDay	分析：应收账款周转天数
# FFR.AR	计算：未来5年应收账款
# ar_decrease	分析：未来5年应收账款的减少
# InvDay	分析：存货周转天数
# FFR.Inv	计算：未来5年存货
# Inv_decrease	分析：未来5年存货的减少
# APDay	分析：应付账款周转天数
# FFR.AP	计算：未来5年应付账款
# ap_increase	分析：未来5年应付账款的增加
#
# cash_increase	分析：现金的增加
# FFR.Cash	计算：未来5年现金
# OthAst	分析：其他资产项目
# FFR.TA	计算：未来5年总资产
# OthLia	分析：其他负债项目
# FFR.L	计算：未来5年总负债
# FFR.E	计算：未来5年股东权益
# FFR.RE	计算：未来5年留存收益
#
#
# equity	分析：股东权益
# DEratio	分析：D/E比率
# EM	分析：权益乘数
# DAratio	分析：资产负债率
# InterestCR	分析：利息覆盖率
# CurrentR	分析：流动比率
# QuickR	分析：速动比率
# CashR	分析：现金比率
# Optperiod	分析：营业周期
# Cashperiod	分析：现金转化周期
# ROE	分析：净资产收益率
# ROA	分析：总资产报酬率
# AssetT	分析：总资产周转率
# ART	分析：应收账款周转率
# InvT	分析：存货周转率
# APT	分析：应付账款周转率
#
#
# output.NI	今年+未来10年净利润
# output.NOPAT	今年+未来10年NOPAT
# output.B	今年+未来10年净资产
# output.A	今年+未来10年总资产
# output.E+debt	今年+未来10年投资资本面值
# output.NetDebt	今年+次年净债务
# output.EBT	今年+次年利润总额
# output.Rev	今年+次年营业总收入
# output.EBIT	今年+次年EBIT
# output.SC	总股本
# output.D/E	D/E比率
# output.Dr	利息率
# output.IncomeTaxR	公司所得税率


class ForcastFR:
    def __init__(self,inputs,year=10):
        self.__year=year
        self.__FFR={}
        self.__output={}
        ###################预测报表#########################
        #######模型
        GR=[]
        if len(inputs['Rev'])!=3:
            logger(2, "ERROR IN INPUT REV")
            return
        for e in range(len(inputs['Rev'])-1):
            GR.append(float(inputs['Rev'][e+1])/float(inputs['Rev'][e])-1)
        # MGR = get_MGR(GR, inputs['Indus_code'], inputs)  ##一个值
        # # MGR=0.252
        # FGR = get_FutureGR(MGR, self.__year)  ##长度为year的list
        if inputs['Rev_adj']==[]:
            MGR = get_MGR(inputs)  ##一个值
            # MGR=0.252
            FGR = [MGR]
            FGR.extend(get_GR9(GR[0],GR[1],MGR, inputs['Indus_code']))  ##长度为year的list
        else:
            FGR = list(inputs['Rev_adj'])
            FGR.extend(get_GR9(FGR[0], FGR[1],FGR[2], inputs['Indus_code'])[:7])
        self.__GR=FGR
        ######分析值
        interstExp=float(inputs['debt'])*inputs['Dr']
        OptCost=float(inputs['Rev'][-1])-inputs['EBIT']-interstExp
        OptCostM=float(OptCost)/inputs['Rev'][-1]
        PftRBT=float(inputs['EBT'])/inputs['Rev'][-1]
        if inputs['EBT']==0:
            IncomeTaxR=0.25
        else:
            IncomeTaxR=1-float(inputs['NI'])/inputs['EBT']

        #########限制税率范围-》允许利润总额<净利润
        if IncomeTaxR>0.25:
            IncomeTaxR=0.25
        elif IncomeTaxR<0.15:
            IncomeTaxR=0.15

        ARDay=float(inputs['AR'])/inputs['Rev'][-1]*360
        InvDay=float(inputs['Inv'])/(inputs['Rev'][-1]-inputs['EBIT'])*360
        APDay=float(inputs['AP'])/(inputs['Rev'][-1]-inputs['EBIT'])*360
        OthAst=float(inputs['TA'])-inputs['Cash']-inputs['AR']-inputs['Inv']
        OthLia=float(inputs['L'])-inputs['debt']-inputs['AP']
        self.__FFR["ARDay"] = ARDay
        self.__FFR["InvDay"] = InvDay
        self.__FFR["APDay"] = APDay
        self.__FFR["interstExp"] = interstExp
        self.__FFR["OthAst"] = OthAst
        self.__FFR["OthLia"] = OthLia

        ##财报值
        self.__FFR['Rev']=[]
        self.__FFR['OptCost']=[]
        self.__FFR['EBIT']=[]
        self.__FFR['EBT']=[]
        self.__FFR['Tax']=[]
        self.__FFR['NI']=[]
        self.__FFR['AR']=[]
        self.__FFR['Inv']=[]
        self.__FFR['AP']=[]
        self.__FFR['Cash']=[]
        self.__FFR['TA']=[]
        self.__FFR['L']=[]
        self.__FFR['E']=[]
        self.__FFR['RE']=[]

        rev=inputs['Rev'][-1]
        last_ar=inputs['AR']
        last_inv=inputs['Inv']
        last_ap=inputs['AP']
        cash=inputs['Cash']
        equity = inputs['TA'] - inputs['L']
        DEratio = float(inputs['debt']) / equity
        for e in range(self.__year):
            rev=float(rev)*(1+FGR[e])
            optcost=OptCostM*rev
            ebit=rev-interstExp-optcost
            ebt=rev*PftRBT
            tax=ebt*IncomeTaxR
            ni=ebt-tax
            ar=ARDay*rev/360
            ar_decrease=last_ar-ar
            last_ar=ar
            inv=(rev-ebit)*InvDay/360
            inv_decrease=last_inv-inv
            last_inv=inv
            ap=(rev-ebit)*APDay/360
            ap_increase=ap-last_ap
            last_ap=ap
            cash_increase=ni+ar_decrease+inv_decrease+ap_increase
            cash=cash+cash_increase
            ta=OthAst+ar+cash+inv
            l=equity*DEratio+OthLia+ap
            equity=ta-l
            re=equity-inputs['SC']

            self.__FFR['Rev'].append(rev)
            self.__FFR['OptCost'].append(optcost)
            self.__FFR['EBIT'].append(ebit)
            self.__FFR['EBT'].append(ebt)
            self.__FFR['Tax'].append(tax)
            self.__FFR['NI'].append(ni)
            self.__FFR['AR'].append(ar)
            self.__FFR['Inv'].append(inv)
            self.__FFR['AP'].append(ap)
            self.__FFR['Cash'].append(cash)
            self.__FFR['TA'].append(ta)
            self.__FFR['L'].append(l)
            self.__FFR['E'].append(equity)
            self.__FFR['RE'].append(re)
        ####指标分析
        equity=inputs['TA']-inputs['L']
        if equity!=0:
            EM=float(inputs['TA'])/equity
            ROE=float(inputs['NI'])/equity

        else:
            DEratio=EM=ROE=False
        if inputs['TA']!=0:
            ROA=(float(inputs['EBT'])+interstExp)/inputs['TA']
            DAratio=float(inputs['L'])/inputs['TA']
            AssetT=float(inputs['Rev'][-1])/inputs['TA']
        else :
            ROA=DAratio=AssetT=False
        if interstExp!=0:
            InterestCR=(float(inputs['EBIT'])+interstExp)/interstExp
        else:
            InterestCR=False
        if inputs['AP']!=0:
            CurrentR=(float(inputs['Cash'])+inputs['AR']+inputs['Inv'])/inputs['AP']
            QuickR=(float(inputs['Cash'])+inputs['AR'])/inputs['AP']
            CashR=(float(inputs['Cash']))/inputs['AP']
        else:
            CurrentR=QuickR=CashR=False
        Optperiod=InvDay+ARDay
        Cashperiod=Optperiod-APDay



        ART=ARDay/360
        InvT=InvDay/360
        APT=APDay/360
        ##########输出数据
        self.__output["cash"] = cash
        self.__output['NI']=copy.deepcopy(self.__FFR['NI'])

        self.__output['NI'].insert(0,inputs['NI'])
        self.__output['NOPAT']=[]
        for e in range(self.__year+1):
            if e==0:
                self.__output['NOPAT'].append((1-IncomeTaxR)*(interstExp+inputs['EBIT']))
            else:
                self.__output['NOPAT'].append((1-IncomeTaxR)*(interstExp+self.__FFR['EBIT'][e-1]))
        self.__output['B']=copy.deepcopy(self.__FFR['E'])
        self.__output['B'].insert(0,equity)
        self.__output['A']=copy.deepcopy(self.__FFR['TA'])
        self.__output['A'].insert(0,inputs['TA'])
        self.__output['E+debt']=[]
        for e in range(self.__year+1):
            if e==0:
                self.__output['E+debt'].append(inputs['debt']+equity)
            else:
                self.__output['E+debt'].append(inputs['debt']+self.__FFR['E'][e-1])

        self.__output['NetDebt']=[inputs['debt']-inputs['Cash'],inputs['debt']-self.__FFR['Cash'][0]]
        self.__output['EBT']=[inputs['EBT'],self.__FFR['EBT'][0]]
        self.__output['Rev']=[inputs['Rev'][-1],self.__FFR['Rev'][0]]
        self.__output['EBIT']=[inputs['EBIT']+interstExp,interstExp+self.__FFR['EBIT'][0]]

        self.__output['SC']=inputs['SC']
        self.__output['D/E']=DEratio
        self.__output['Dr']=inputs['Dr']
        self.__output['IncomeTaxR']=IncomeTaxR
        self.__output["Debt"]=[]
        for e in range(self.__year + 1):
            self.__output["Debt"].append(self.__output["B"][e] * self.__output["D/E"])
        if self.__output['NI'][0]/self.__output['Rev'][0]>0.01 and self.__output['NI'][0]/self.__output['Rev'][0]<0.3:
            self.__output['sPE']=True

        else:
            self.__output['sPE']=False

        if self.__output['NI'][1]/self.__output['Rev'][1]>0.01 and self.__output['NI'][1]/self.__output['Rev'][1]<0.3:
            self.__output['sPEp']=True
        else:
            self.__output['sPEp']=False

        if inputs['L']/inputs['TA']<0.7:
            self.__output['sPB']=True
            self.__output['sPBp']=True
        else:
            self.__output['sPB']=False
            self.__output['sPBp']=False

        if self.__output['EBIT'][0]/self.__output['Rev'][0]>0.02:
            self.__output['sEV_EBIT']=True
            self.__output['sEV_NOPAT']=True
        else:
            self.__output['sEV_EBIT']=False
            self.__output['sEV_NOPAT']=False

        self.__output['sEV_S']=True
        self.__output['sEV_Sp']=True

        self.__output['GR']=GR[1]
        self.__output["GR_APV"] = GR
        self.__output['L']=inputs['L']
        self.__output['Optcost'] = OptCost

    def FFR(self):
        # for key in self.__FFR.keys():
        #     if type(self.__FFR[key])==float:
        #         self.__FFR[key]=round(self.__FFR[key],6)
        #     if type(self.__FFR[key])==list:
        #         for e in range(len(self.__FFR[key])):
        #             if type(self.__FFR[key][e])==float:
        #                 self.__FFR[key][e]=round(self.__FFR[key][e],6)
        return self.__FFR

    def Output(self):
        # for key in self.__output.keys():
        #     if type(self.__output[key])==float:
        #         self.__output[key]=round(self.__output[key],6)
        #     if type(self.__output[key])==list:
        #         for e in range(len(self.__output[key])):
        #             if type(self.__output[key][e])==float:
        #                 self.__output[key][e]=round(self.__output[key][e],6)

        return self.__output

    def FGR(self):
        return self.__GR

