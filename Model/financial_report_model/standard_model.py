# -*- coding: utf-8 -*-：
import xlwt
from Tool.hypothesis.mgr import get_MGR
# from Hypothesis.Shrink import get_FutureGR
from Tool.hypothesis.NextNineGrowthRate import get_GR9

import copy
import numpy as np


class ForcastFR:
    def __init__(self,inputs,year=10):
        self.__year=year
        self.__FFR={}
        self.__output={}
        inputs1=inputs['inputs1']
        inputs2=inputs['inputs2']
        ###################预测报表#########################
        ########################################################################检测inputs1的输入长度
        # target_len=len(inputs1['Cash'])
        # for key in inputs1.keys():
        #     if len(inputs1[key])!=target_len:
        #         print ("ERROR IN INPUT %s"%key)
        #         return
        ###################################################################假设
        #######营业收入增长率GR,FGR
        GR=inputs1['GR']
        if inputs2['plan5_gr']==[None]:
        # if inputs['Rev_adj']==[]:
            MGR=get_MGR(GR[-2:],inputs2['Indus_code'],inputs1)##一个值
            # MGR=0.252
            FGR = [MGR]
            FGR.extend(get_GR9(GR[0], GR[1], MGR, inputs2['Indus_code']))
        else:
            temp=inputs2['plan5_gr'][0]
            FGR=[temp,temp,temp,temp]
            FGR.extend(get_GR9(FGR[0], FGR[1], FGR[2], inputs2['Indus_code'])[:6])
        self.__GR=FGR

        ###########毛利率(不含营业税)GPM1##############
        FGPM1=[]
        a=inputs1['GPM1']
        step=float(inputs2['plan5_mpr'][0])/5
        for e in range(5):
            a+=step
            FGPM1.append(a)
        for e in range(5):
            FGPM1.append(a)

        ###########毛利率(含营业税)GPM2##############

        FGPM2=[]
        a=inputs1['GPM2']
        for e in range(5):
            a+=step
            FGPM2.append(a)
        for e in range(5):
            FGPM2.append(a)

        #########费用率ExpM##################

        FExpM=[]
        a=inputs1['ExpM']
        step=float(inputs2['plan5_OptExpM'][0])/5
        for e in range(5):
            a+=step
            FExpM.append(a)
        for e in range(5):
            FExpM.append(a)

        ##########非经常损益占比NIPLM################

        FNIPLM=[]
        a=inputs1['NIPLM']
        for e in range(self.__year):
            FNIPLM.append(a)
        ##########所得税率 Trate################

        FTrate=[]
        a=inputs1['Trate']
        for e in range(self.__year):
            FTrate.append(a)
        ##########少数股东权益占比 MEM################

        FMEM=[]
        a=inputs1['MEM']
        for e in range(self.__year):
            FMEM.append(a)


        ##########折旧率 DAR################
        FDAR=[]
        a=inputs1['DAR']
        for e in range(self.__year):
            FDAR.append(a)
        ##########借款利息率 Brate################
        FBrate=[]
        a=inputs2['debtRate'][0]
        if a==0:
            a=0.07
        for e in range(self.__year):
            FBrate.append(a)
        ##########存款利息率 Drate################

        FDrate=[]
        a=inputs1['Drate']
        for e in range(self.__year):
            FDrate.append(a)

        #########应收账款周转天数 ARDay##################

        FARDay=[]
        a=inputs1['ARDay']
        step=float(inputs2['plan5_arday'][0])/5
        for e in range(5):
            a+=step
            FARDay.append(a)
        for e in range(5):
            FARDay.append(a)
        #########预付款项周转天数 PPDay##################

        FPPDay=[]
        a=inputs1['PPDay']
        for e in range(self.__year):
            FPPDay.append(a)
        #########存货周转天数 InvDay##################

        FInvDay=[]
        a=inputs1['InvDay']
        step=float(inputs2['plan5_invday'][0])/5
        for e in range(5):
            a+=step
            FInvDay.append(a)
        for e in range(5):
            FInvDay.append(a)
        #########应付账款周转天数 APDay##################

        FAPDay=[]
        a=inputs1['APDay']
        step=float(inputs2['plan5_apday'][0])/5
        for e in range(5):
            a+=step
            FAPDay.append(a)
        for e in range(5):
            FAPDay.append(a)
        #########应记负债周转天数 ALDay##################

        FALDay=[]
        a=inputs1['ALDay']
        for e in range(self.__year):
            FALDay.append(a)
        #########应交税费周转天数 ATDay##################

        FATDay=[]
        a=inputs1['ATDay']
        for e in range(self.__year):
            FATDay.append(a)



        ###############################################################################财报数据（无循环部分）
        FRev=[]  #####营业收入
        FBTS=[]  #####营业税金及附加
        FGP=[]   #####毛利润
        FOptCst=[]   ######经营费用
        FNIPL=[]     ####非经常损益
        FEBITDA=[]   #####息税折旧摊销前利润
        FAR=[]    #####应收票据和应收账款
        FLTI=[]     #####长期投资
        FDTA=[]    ####递延所得税资产
        FOthR=[]     ###其他应收款
        FGW=[]    ####商誉
        FAL=[]   ####应记负债
        FDTL=[]   ####递延所得税负债
        FOthP=[]  #######其他应付款
        FOthLia=[]  #####其它负债
        FCost=[]      ############营业成本
        FPP=[]        #############预付款项
        FInv=[]       ##################存货
        FOthAst=[]      ###########其他资产
        FAP=[]    ########应付票据和应付账款

        frev=inputs1['Rev']
        fdtl=inputs1['DTL']
        fothast=inputs1['OthAst']
        # fcontributed_capital=inputs1['Contributed_Capital'][-1]
        FDT=[]  ########递延所得税·没有说明，默认为0
        for e in range(self.__year):
            fdt=0
            frev*=(1+FGR[e])
            fbts=frev*(FGPM1[e]-FGPM2[e])
            fgp=frev*FGPM2[e]
            foptcst=frev*FExpM[e]
            fnipl=frev*FNIPLM[e]
            febitda=fgp+fnipl-foptcst
            far=frev*FARDay[e]/360
            flti=inputs1['LTI']
            fdta=inputs1['DTA']
            fothr=inputs1['OthR']
            fgw=inputs1['GW']
            fal=foptcst*FALDay[e]/360
            fdtl+=fdt
            fothp=inputs1['OthP']
            fothlia=inputs1['OthLia']
            # if e<5:
            #     capital_from_investor=inputs2['plan5_efIncome'][0]/5
            #
            # else:
            #     capital_from_investor=0
            # fcontributed_capital+=capital_from_investor
            fcost=frev-fgp-fbts
            fpp=fcost*FPPDay[e]/360
            finv=fcost*FInvDay[e]/360
            fothast+=fnipl
            fap=fcost*FAPDay[e]/360

            FRev.append(frev)
            FBTS.append(fbts)
            FGP.append(fgp)
            FOptCst.append(foptcst)
            FNIPL.append(fnipl)
            FEBITDA.append(febitda)
            FAR.append(far)
            FLTI.append(flti)
            FDTA.append(fdta)
            FOthR.append(fothr)
            FGW.append(fgw)
            FAL.append(fal)
            FDTL.append(fdtl)
            FOthP.append(fothp)
            FOthLia.append(fothlia)
            # Capital_from_investor.append(capital_from_investor)
            # FContributed_Capital.append(fcontributed_capital)
            FDT.append(fdt)
            FCost.append(fcost)
            FPP.append(fpp)
            FInv.append(finv)
            FOthAst.append(fothast)
            FAP.append(fap)



        CapExp=[]   #########资本性支出
        CExpM=[]   ######资本性支出占营业收入
        sum=0

        for e in  range(self.__year):
            if e<5:
                capexp=-inputs2['plan5_fixExp'][0]/5-inputs2['plan5_ingExp'][0]/5
                cexpm=capexp/FRev[e]
                sum+=cexpm
            else:
                cexpm=sum/5
                capexp=FRev[e]*cexpm

            CapExp.append(capexp)
            CExpM.append(cexpm)
        ############################################################################DA模块
        FDA=self.Amortization(CapExp,inputs1['CA'],inputs1['DA'])

        ########################################################################DA模块结束
        FCA=[]        ##########资本性资产
        fca=inputs1['CA']
        for e in range(self.__year):

            fca=fca-FDA[e]-CapExp[e]
            FCA.append(fca)

        Inv_decrease=[]    #########存货的减少
        Optrd=[]      ###########经营性应收项目的减少
        FEBIT=[]        ##########息税前利润
        for e in range(self.__year):
            if e==0:
                Inv_decrease.append(inputs1['Inv']-FInv[e])
                Optrd.append(inputs1['AR']+inputs1['PP']-FAR[e]-FPP[e])
            else:
                Inv_decrease.append(FInv[e-1]-FInv[e])
                Optrd.append(FAR[e-1]+FPP[e-1]-FAR[e]-FPP[e])
            febit=FEBITDA[e]-FDA[e]


            FEBIT.append(febit)
        #############################################################################各种原计划
        Plan_Dividend=[]         #########用户输入的分红计划
        Plan_Capital_from_investor=[]      ##########用户输入的股权融资计划
        Plan_borrow=[]                     ###########用户输入的债权融资计划
        Capital_from_investor=[]      #############股权融资
        FContributed_Capital=[]        ########实缴资本
        FBorrow=[]                   ##########债权融资
        # for e in range(5):
        #     Plan_Dividend.append(inputs2['plan5_dcExp'][0])
        #     Plan_Capital_from_investor.append(inputs2['plan5_efIncome'][0])
        #     Plan_borrow.append(inputs2['plan5_debtIncome'][0]-inputs2['plan5_debtExp'][0])

        #########真实
        FCash=[]       ############现金和现金等价物
        FTA=[]         ##########资产总计
        FDebt=[]    #############借款和应付债券
        FAT=[]            ###############应交税费
        FL=[]            ############负债合计
        FRE=[]            ###########留存收益
        FPES=[]           ##########母公司股东权益合计
        FME=[]           ###################少数股东权益合计
        FE=[]             #########股东权益合计

        FInsExp=[]        ############利息支出
        FInsIncome=[]        ############利息收入
        FEBT=[]          ###########利润总额
        FTax=[]         ##########所得税费用
        FNI=[]        ##########净利润
        FPNI=[]         ###########归属于母公司股东的净利润
        FMPL=[]          ##########少数股东损益

        Optpi=[]        ############经营性应付项目的增加
        Cash_increase=[]      ############现金和现金等价物增加净额
        DM=[]                ##########分红率
        CashRatio=[]          ############现金比率
        Cash_floor=[]               ############现金余额下线
        pre_Cash=[]               ##############自动借还款前现金流
        pre_Amount=[]          ############自动借还款前期末余额
        auto_borrow=[]          ###########应借款金额
        CS=[]           ###########资本结构
        CS_dif=[]        ############据目标资本结构差值
        FRE1=[]

        remain_fe_amount=inputs2['plan5_efIncome'][0]*5
        remain_fb_amount=(inputs2['plan5_debtIncome'][0]-inputs2['plan5_debtExp'][0])*5
        for e in range(self.__year):
            ###########################################################################预计
            if e==0:
                oldre=inputs1['RE']
                olddebt=inputs1['Debt']
                if olddebt==0 and FBrate[0]!=0:
                    olddebt=inputs1['Cash']*FBrate[0]
                oldcash=inputs1['Cash']
                oldequity=inputs1['E']
                oldap=inputs1['AP']
                oldal=inputs1['AL']
                oldat=inputs1['AT']
                oldme=inputs1['ME']
                plan_borrow=inputs2['plan5_debtIncome'][0]-inputs2['plan5_debtExp'][0]
                plan_capital_from_investor=inputs2['plan5_efIncome'][0]
                oldcontributedc=inputs1['Contributed_Capital']
                oldre=inputs1['RE']

            else:
                oldre=FRE[e-1]
                olddebt=FDebt[e-1]
                oldcash=FCash[e-1]
                oldequity=FE[e-1]
                oldap=FAP[e-1]
                oldal=FAL[e-1]
                oldat=FAT[e-1]
                oldme=FME[e-1]
                oldre=FRE[e-1]
                oldcontributedc=FContributed_Capital[e-1]
                if 5-len(FBorrow)>0:
                    a=(inputs2['plan5_debtIncome'][0]-inputs2['plan5_debtExp'][0])*5
                    # print (type(FBorrow[0]))
                    b=np.sum(FBorrow).item()
                    plan_borrow=(a-b)/(5-len(FBorrow))
                    plan_capital_from_investor=(inputs2['plan5_efIncome'][0]*5-np.sum(Capital_from_investor).item())/(5-len(Capital_from_investor))
                else:
                    plan_borrow=0
                    plan_capital_from_investor=0

            if e<5:
                plan_dividend=-inputs2['plan5_dcExp'][0]/5
            else:
                plan_dividend=0
            pInsExp=olddebt*FBrate[e]                  ############y利息支出
            pInsIncome=oldcash*FDrate[e]             ########利息收入
            pEBT=FEBIT[e]+pInsIncome-pInsExp            #######EBT
            pTax=pEBT*FTrate[e]                        ####所得税
            pNI=pEBT-pTax                              ####净利润
            # pMPL=pNI*FMEM[e]                    ###########少数股东损益
            # pPNI=pNI-pMPL                                ############归属于母公司股东的净利润
            pAT=pTax*FATDay[e]/360                #############应交税费
            # pre=oldre+pPNI+plan_dividend             ############留存收益
            # pContributed_c=oldcontributedc+plan_capital_from_investor  ################实缴资本
            # pPES=pre+pContributed_c            ###############母公司权益合计
            # pME=oldme+pMPL                  ############少数股东权益
            # pEquity=pPES+pME             ##########所有者权益
            pOptpi=FAP[e]+FAL[e]+pAT-oldap-oldal-oldat       ############经营性应付项目的增加


            pDebt=olddebt+plan_borrow      ##########债务
            pcashincrease=pNI-FNIPL[e]+FDA[e]+FDT[e]+Inv_decrease[e]+Optrd[e]+pOptpi+CapExp[e]+plan_capital_from_investor+plan_borrow+plan_dividend   #########现金的增加
            pcash=pcashincrease+oldcash    #####现金
            pcurlia=pDebt+FAP[e]+FAL[e]+pAT+FOthP[e]      #######流动负债
            pcashratio=pcash/pcurlia           ######现金比率
            icr=FEBITDA[e]/pInsExp            ###########利息覆盖率
            ########################################################################################################################################预计结束
            ########################################################################################################################################分析开始
            target_cashratio=1                             ######现金比率（目标）
            trend=max(0,target_cashratio-pcashratio)        ########趋近
            financeamount=pcurlia*trend                    #########预计应融资金额
            equityamount=financeamount/(1+inputs2['target_CS'][0])         ###########股权融资金额
            debtamount=financeamount-equityamount           #######债权融资金额
            equity_add=max(0,equityamount+plan_dividend) #plan_dividend 流出的现金流，本身为负  #########还需要股权融资

            if e<5:
                if icr >5:
                    capital_from_investor=max(equity_add,remain_fe_amount/(5-e))
                    if debtamount>0:
                        borrow=max(debtamount,remain_fb_amount/(5-e))
                    else:
                        borrow=remain_fb_amount/(5-e)
                else:
                    capital_from_investor=financeamount
                    borrow=0

            else:
                if icr>5:
                    capital_from_investor=equity_add
                    borrow=debtamount
                else:
                    capital_from_investor=financeamount
                    borrow=0
            remain_fb_amount-=borrow
            remain_fe_amount-=capital_from_investor
            ########################################################################################################################################分析结束
            ######################################################################################################################################构建开始
            fDebt=olddebt+borrow          ############借款和应付债券
            finsexp=(fDebt+olddebt)/2*FBrate[e]   #########利息支出
            fcontributed_capital=oldcontributedc+capital_from_investor  ###############实缴资本
            cash=pcash
            count=0
            while True:
                finsincome=cash*FDrate[e]
                febt=FEBIT[e]+finsincome-finsexp
                ftax=febt*FTrate[e]
                fni=febt-ftax
                fat=ftax*FATDay[e]/360
                foptpi=FAP[e]+FAL[e]+fat-oldat-oldap-oldal

                # fmpl=fni*FMEM[e]
                # fpni=fni-fmpl
                fcashincrease=fni-FNIPL[e]+FDA[e]+FDT[e]+Inv_decrease[e]+Optrd[e]+foptpi+CapExp[e]+capital_from_investor+borrow+plan_dividend
                newcash=oldcash+fcashincrease
                if count>100 or (count>5 and newcash-cash<1):
                    # print (count)
                    cash=newcash
                    break
                else:
                    cash=newcash
                count+=1
            fta=cash+FAR[e]+FPP[e]+FInv[e]+FLTI[e]+FCA[e]+FDTA[e]+FOthR[e]+FGW[e]+FOthAst[e]
            fl=fDebt+FAP[e]+FAL[e]+fat+FDTL[e]+FOthP[e]+FOthLia[e]
            fmpl=fni*FMEM[e]
            fpni=fni-fmpl
            fre=oldre+fpni+plan_dividend
            fpes=fre+fcontributed_capital
            fme=oldme+fmpl
            fequity=fpes+fme


            fre1=fpes-fcontributed_capital





            Capital_from_investor.append(capital_from_investor)
            FBorrow.append(float(borrow))
            FDebt.append(fDebt)
            FInsExp.append(finsexp)
            FContributed_Capital.append(fcontributed_capital)
            FCash.append(cash)
            FInsIncome.append(finsincome)
            FEBT.append(febt)
            FTax.append(ftax)
            FNI.append(fni)
            FAT.append(fat)
            Optpi.append(foptpi)
            Cash_increase.append(fcashincrease)
            FTA.append(fta)
            FL.append(fl)
            FMPL.append(fmpl)
            FPNI.append(fpni)
            FE.append(fequity)
            FME.append(fme)
            FPES.append(fpes)
            FRE.append(fre)
            FRE1.append(fre1)
            Plan_Dividend.append(plan_dividend)


        self.__FFR={}
        self.__adFR={}

        self.__FFR['a_cashandcashequivalents']=FCash
        self.__FFR['a_notesreceivablenaccountsreceivable']=FAR
        self.__FFR['a_prepayment']=FPP
        self.__FFR['a_inventory']=FInv
        self.__FFR['a_longterm_investment']=FLTI
        self.__FFR['a_capitalasset']=FCA
        self.__FFR['a_deferredincometaxassets']=FDTA
        self.__FFR['a_otherreceivable']=FOthR
        self.__FFR['a_goodwill']=FGW
        self.__FFR['a_otherasset']=FOthAst
        self.__FFR['a_totalasset']=FTA
        self.__FFR['l_borrowingsanddebenturespayable']=FDebt
        self.__FFR['l_notespayablenaccountspayable']=FAP
        self.__FFR['l_accruedliabilities']=FAL
        self.__FFR['l_taxespayable']=FAT
        self.__FFR['l_deferredincometaxliabilities']=FDTL
        self.__FFR['l_otheraccountspayable']=FOthP
        self.__FFR['l_otherliabilities']=FOthLia
        self.__FFR['l_totalliabilities']=FL
        self.__FFR['e_paidincapital']=FContributed_Capital
        self.__FFR['e_retainedprofits']=FRE
        self.__FFR['e_totalequityattributabletoshareholdersoftheparent']=FPES
        self.__FFR['e_minorityinterests']=FME
        self.__FFR['e_totalshareholdersequity']=FE
        self.__FFR['is_operatingrevenue']=FRev
        self.__FFR['is_operatingcosts']=FCost
        self.__FFR['is_businesstaxesnsurcharges']=FBTS
        self.__FFR['is_grossprofit']=FGP
        self.__FFR['is_operatingexpenses']=FOptCst
        self.__FFR['is_nonrecurringpl']=FNIPL
        self.__FFR['is_ebitda']=FEBITDA
        self.__FFR['is_da']=FDA
        self.__FFR['is_ebit']=FEBIT
        self.__FFR['is_interestexpenses']=FInsExp
        self.__FFR['is_interestincome']=FInsIncome
        self.__FFR['is_incomebeforetax']=FEBT
        self.__FFR['is_incometax']=FTax
        self.__FFR['is_netprofit']=FNI
        self.__FFR['is_netincomeattributedtoshareholders']=FPNI
        self.__FFR['is_plofminorityinterests']=FMPL
        self.__FFR['deferredincometax']=FDT
        self.__FFR['decreaseininventories']=Inv_decrease
        self.__FFR['decreaseinoperatingreceivables']=Optrd
        self.__FFR['increaseinoperatingpayables']=Optpi
        self.__FFR['capitalexpenditures']=CapExp
        self.__FFR['cashreceivedfrominvestments']=Capital_from_investor
        self.__FFR['borrowings']=FBorrow
        self.__FFR['cashdividends']=Plan_Dividend
        self.__FFR['netincreaseincashandcashequivalents']=Cash_increase
        # self.__FFR['借款利息率']=FBrate
        # self.__FFR['存款利息率']=FDrate
        # self.__FFR['所得税率']=FTrate
        # self.__FFR['应交税费周转天数']=FATDay
        # self.__FFR['费用率'] = FExpM

        # #用来输出excel的预计财报
        # f = xlwt.Workbook() #创建工作簿
        # sheet1 = f.add_sheet(u'sheet1',cell_overwrite_ok=True)
        # count=0
        # for key,value in self.__FFR.items():
        #     sheet1.write(count,0,key)
        #     for e in range(len(value)):
        #         sheet1.write(count,e+1,value[e])
        #     count+=1
        # f.save('test_1_month.xls')
        ##########输出数据
        self.__output['NI']=copy.deepcopy(FNI)

        self.__output['NI'].insert(0,inputs1['NI'])
        self.__output['NOPAT']=[]
        for e in range(self.__year+1):
            if e==0:
                self.__output['NOPAT'].append(inputs1['EBIT']*(1-inputs1['Trate']))
            else:
                self.__output['NOPAT'].append(FEBIT[e-1]*(1-FTrate[e-1]))
        self.__output['B']=copy.deepcopy(FE)
        self.__output['B'].insert(0,inputs1['E'])
        self.__output['A']=copy.deepcopy(FTA)
        self.__output['A'].insert(0,inputs1['TA'])
        self.__output['E+debt']=[]
        for e in range(self.__year+1):
            if e==0:
                self.__output['E+debt'].append(inputs1['Debt']+inputs1['E'])
            else:
                self.__output['E+debt'].append(FDebt[e-1]+FE[e-1])

        self.__output['NetDebt']=[inputs1['Debt']-inputs1['Cash'],FDebt[0]-FCash[0]]
        self.__output['EBT']=[inputs1['EBT'],FEBT[0]]
        self.__output['Rev']=[inputs1['Rev'],FRev[0]]
        self.__output['EBIT']=[inputs1['EBIT']+inputs1['InsExp'],FInsExp[0]+FEBIT[0]]

        self.__output['SC']=inputs1['SC']       #####股本
        self.__output['D/E']=inputs1['Debt']/inputs1['E']
        self.__output['Dr']=FBrate[0]
        self.__output['IncomeTaxR']=FTrate[0]
        if self.__output['NI'][0]/self.__output['Rev'][0]>0.01 and self.__output['NI'][0]/self.__output['Rev'][0]<0.3:
            self.__output['sPE']=True

        else:
            self.__output['sPE']=False

        if self.__output['NI'][1]/self.__output['Rev'][1]>0.01 and self.__output['NI'][1]/self.__output['Rev'][1]<0.3:
            self.__output['sPEp']=True
        else:
            self.__output['sPEp']=False
        temp1=[inputs1['L']]
        temp1.extend(inputs1['L_rest'])
        temp2=[inputs1['TA']]
        temp2.extend(inputs1['TA_rest'])


        if np.average(temp1)/np.average(temp2)<0.7:
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

        self.__output['GR']=GR[-1]
        self.__output['L']=inputs1['L']


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
















    #############折旧摊销部分##########################
    def Amortization(self,CapExp,origin_fix,origin_DA):
        if origin_fix==0:
            ans=CapExp
            return ans
        # print (origin_fix,origin_DA,CapExp[0])
        DA=[]
        origin_year=origin_fix/origin_DA
        da_year=[]
        a=origin_year*2
        yearlength=len(CapExp)
        while a>0:
            da_year.append(a)
            a-=1
        for e in range(yearlength+1):       ###十一（0+10）年每年 都有资本性支出
            temp=[]

            if e==0:
                count =0
                while origin_fix-origin_DA>0 and count <yearlength:
                    temp.append(origin_DA)
                    origin_fix-=origin_DA
                    count+=1
                if len(temp)<yearlength:
                    temp.append(origin_fix)
            else:
                count=0
                amount=-CapExp[e-1]

                while da_year[count]>1 and count+e<yearlength+1:
                    da=amount/da_year[count]
                    temp.append(da)
                    amount-=da
                    count+=1
                if count+e<yearlength+1:
                    temp.append(amount)
            DA.append(temp)
        ans=[] # 长度为10
        count=1
        for e in range(1,yearlength+1):

            if e+len(DA[0])<11:
                sum_da=0
            else:
                sum_da=DA[0][-count]
                count+=1
            for ele in DA[1:]:
                if len(ele)<e:
                    continue
                else:
                    sum_da+=ele[-e]
            ans.insert(0,sum_da)
        return ans







