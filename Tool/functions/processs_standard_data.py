# -*- coding: utf-8 -*-：
import numpy as np

from Tool.functions.errorinfo import wirte_error

# inputs1:年报
# inputs2：杂七杂八信息
# inputs3:月报


def process_YearFR(inputs1):
    target_len = len(inputs1['短期金融投资'])
    ans={}
    ans1 = {}
    LIST_ITEMS=['Cash','AR','PP','Inv','LTI','CA','DTA','OthR','GW','TA','OthAst','Debt','AP','AL','AT','DTL','OthP','L',
                'OthLia','Contributed_Capital','RE','PES','E','ME','Rev','Cost','BTS','GP','OptCst','NIPL','EBITDA','DA',
                'EBIT','InsExp','InsIncome','EBT','Tax','NI','PNI','MPL','SC']
    for e in LIST_ITEMS:
        ans1[e]=[]


    for e in range(target_len):
        ans1['Cash'].append(inputs1['短期金融投资'][e] + inputs1['货币资金'][e])
        ans1['AR'].append(inputs1['应收票据'][e] + inputs1['应收账款'][e])
        ans1['PP'].append(inputs1['预付款项'][e])
        ans1['Inv'].append(inputs1['存货'][e])
        ans1['LTI'].append(inputs1['长期金融投资'][e] + inputs1['长期股权投资'][e])
        ans1['CA'].append(
            inputs1['投资性房地产'][e] + inputs1['固定资产'][e] + inputs1['在建工程'][e] + inputs1['无形资产'][e] + inputs1['开发支出'][e] +
            inputs1['长期待摊费用'][e])
        ans1['DTA'].append(inputs1['递延所得税资产'][e])
        ans1['OthR'].append(inputs1['其他应收款'][e])
        ans1['GW'].append(inputs1['商誉'][e])
        ans1['TA'].append(inputs1['流动资产合计'][e] + inputs1['非流动资产合计'][e])
        ans1['OthAst'].append(
            ans1['TA'][e] - ans1['Cash'][e] - ans1['AR'][e] - ans1['PP'][e] - ans1['Inv'][e] - ans1['LTI'][e] -
            ans1['CA'][e] - ans1['DTA'][e] - ans1['OthR'][e] - ans1['GW'][e])
        ans1['Debt'].append(inputs1['短期借款'][e] + inputs1['一年以内到期的非流动负债'][e] + inputs1['长期借款'][e] + inputs1['应付债券'][e])
        ans1['AP'].append(inputs1['应付票据'][e] + inputs1['应付账款'][e])
        ans1['AL'].append(inputs1['预收款项'][e] + inputs1['应付职工薪酬'][e])
        ans1['AT'].append(inputs1['应交税费'][e])
        ans1['DTL'].append(inputs1['递延所得税负债'][e])
        ans1['OthP'].append(inputs1['其他应付款'][e])
        ans1['L'].append(inputs1['流动负债合计'][e] + inputs1['非流动负债合计'][e])
        ans1['OthLia'].append(
            ans1['L'][e] - ans1['Debt'][e] - ans1['AP'][e] - ans1['AL'][e] - ans1['AT'][e] - ans1['DTL'][e] -
            ans1['OthP'][e])
        ans1['Contributed_Capital'].append(inputs1['股本'][e] + inputs1['资本公积'][e])
        ans1['RE'].append(inputs1['母公司股东的权益合计'][e] - inputs1['股本'][e] - inputs1['资本公积'][e])
        ans1['PES'].append(inputs1['母公司股东的权益合计'][e])
        ans1['E'].append(ans1['TA'][e] - ans1['L'][e])
        ans1['ME'].append(ans1['E'][e] - inputs1['母公司股东的权益合计'][e])
        ans1['Rev'].append(inputs1['营业总收入'][e])
        ans1['Cost'].append(inputs1['营业成本'][e])
        ans1['BTS'].append(inputs1['营业税金及附加'][e])
        ans1['GP'].append(ans1['Rev'][e] - ans1['Cost'][e] - ans1['BTS'][e])
        temp1 = inputs1['利息支出'][e] - inputs1['利息收入'][e]
        temp2 = inputs1['财务费用'][e] - temp1
        temp3 = inputs1['当期固定资产折旧'][e] + inputs1['当期无形资产摊销'][e] + inputs1['当期长期待摊费用摊销'][e]
        ans1['OptCst'].append(inputs1['销售费用'][e] + inputs1['管理费用'][e] + temp2 - temp3)
        ans1['NIPL'].append(
            inputs1['利润总额'][e] - inputs1['营业总收入'][e] + inputs1['营业成本'][e] + inputs1['营业税金及附加'][e] + inputs1['销售费用'][e] +
            inputs1['管理费用'][e] + inputs1['财务费用'][e])
        ans1['EBITDA'].append(ans1['GP'][e] + ans1['NIPL'][e] - ans1['OptCst'][e])
        ans1['DA'].append(temp3)
        ans1['EBIT'].append(ans1['EBITDA'][e] - ans1['DA'][e])
        ans1['InsExp'].append(inputs1['利息支出'][e])
        ans1['InsIncome'].append(inputs1['利息收入'][e])
        ans1['EBT'].append(ans1['EBIT'][e] + ans1['InsIncome'][e] - ans1['InsExp'][e])
        ans1['Tax'].append(inputs1['利润总额'][e] - inputs1['净利润'][e])
        ans1['NI'].append(inputs1['净利润'][e])
        ans1['PNI'].append(inputs1['归属于母公司股东的净利润'][e])
        ans1['MPL'].append(inputs1['净利润'][e] - inputs1['归属于母公司股东的净利润'][e])
        ans1['SC'].append(inputs1['股本'][e])

    for key,value in ans1.items():
        ans[key]=value[-1]
    ans['L_rest']=ans1['L'][:-2]
    ans['TA_rest']=ans1['TA'][:-2]
    #各项指标初始化
    INDEXS = ['GR', 'GPM1', 'GPM2', 'ExpM', 'NIPLM', 'Trate', 'MEM', 'DAR', 'Drate', 'ARDay', 'PPDay', 'InvDay',
              'APDay', 'ALDay', 'ATDay']
    for e in INDEXS:
        ans[e] = False
    #利润表相关指标

    #营业收入增长率GR
    len_rev = 2
    ans['GR'] = []
    while len_rev>0:  #####ans1['Rev']:...-2,-1,0
        if ans1['Rev'][-(len_rev+1)]==0:
            wirte_error('process_standard_data:近三年营业收入含0')
        ans['GR'].append(float(ans1['Rev'][-len_rev]) / ans1['Rev'][-(len_rev+1)] - 1)
        len_rev-=1

    ###########毛利率(不含营业税)GPM1
    ans['GPM1'] = 1 - ans1['Cost'][-1] / ans1['Rev'][-1]

    ###########毛利率(含营业税)GPM2
    ans['GPM2'] = 1 - (ans1['Cost'][-1] + ans1['BTS'][-1]) / ans1['Rev'][-1]

    #########费用率ExpM
    ans['ExpM'] = ans1['OptCst'][-1] / ans1['Rev'][-1]

    ##########非经常损益占比NIPLM
    NIPLM = []
    for e in range(target_len):
        if ans1['Rev'][e]==0:
            continue
        NIPLM.append(ans1['NIPL'][e] / ans1['Rev'][e])
    ans['NIPLM']=np.average(NIPLM).item()

    ##########借款利息率 Brate
    # Brate = []
    # for e in range(target_len - 1):
    #     Brate.append(ans1['InsExp'][e + 1] / ((ans1['Debt'][e] + ans1['Debt'][e + 1]) / 2))

    ##########所得税率 Trate
    if ans1['EBT'][-1]==0:
        ans['Trate']=0.25
    else:
        ans['Trate'] = ans1['Tax'][-1] / ans1['EBT'][-1]


    ##########少数股东权益占比 MEM
    MEM = []
    for e in range(target_len):
        if ans1['NI'][e]==0:
            continue
        MEM.append(ans1['MPL'][e] / ans1['NI'][e])
    if MEM==[]:
        wirte_error('process_standard_data:输入数据中所有净利润都为0')
    ans['MEM'] = np.average(MEM).item()

    #资产负债表相关 指标
    ##########折旧率 DAR
    for e in  range(target_len-1):
        if ans1['CA'][-(2+e)]!=0:
            ans['DAR'] = ans1['DA'][-(1+e)] / ans1['CA'][-(2+e)]
            break
    ##########存款利息率 Drate
    if (ans1['Cash'][-1] + ans1['Cash'][-2])!=0:
        ans['Drate'] =ans1['InsIncome'][-1] / ((ans1['Cash'][-1] + ans1['Cash'][-2]) / 2)
    else:
        ans['Drate']=0.03

    #########应收账款周转天数 ARDay
    ans['ARDay'] =(ans1['AR'][-1] + ans1['AR'][-2]) / ans1['Rev'][-1] * 360 / 2


    #########预付款项周转天数 PPDay,存货周转天数 InvDay,应付账款周转天数 APDay
    for e in range(target_len-1):
        if ans1['Cost'][-(1+e)]!=0:
            ans['PPDay'] = (ans1['PP'][-(2+e)] + ans1['PP'][-(e+1)]) / ans1['Cost'][-(1+e)] * 360 / 2
            ans['InvDay'] = (ans1['Inv'][-(2+e)] + ans1['Inv'][-(e+1)]) / ans1['Cost'][-(e+1)] * 360 / 2
            ans['APDay'] = (ans1['AP'][-(2+e)] + ans1['AP'][-(e+1)]) / ans1['Cost'][-(e+1)] * 360 / 2
            break
    #########应记负债周转天数 ALDay
    for e in range(target_len-1):
        if ans1['OptCst'][-(1+e)]!=0:
            ans['ALDay'] = (ans1['AL'][-(2+e)] + ans1['AL'][-(e+1)]) / ans1['OptCst'][-(e+1)] * 360 / 2
            break

    #########应交税费周转天数 ATDay
    temptax=False
    if ans1['Tax'][-1]==0: #利润总额=净利润（国家亏损免交税政策） 纳税额按最近一年为正的利润总额的25%算
        for e in range(target_len-1):
            if inputs1['利润总额'][-(e+1)]>0:
                temptax=inputs1['利润总额'][-(e+1)]*0.25
                ans['ATDay']=(ans1['AT'][-(e+2)] + ans1['AT'][-(e+1)]) / temptax * 360 / 2
                break
    else:
        temptax=ans1['Tax'][-1]
        ans['ATDay'] = (ans1['AT'][-2] + ans1['AT'][-1]) / temptax * 360 / 2

    for e in INDEXS:
        if ans[e]==False:
            wirte_error('Error when process standard data '+e)

    return ans

def process_addinfo_year(inputs1,inputs2):
    ans2 = {}
    ans2['plan5_fixExp'] = []
    ans2['plan5_ingExp'] = []
    ans2['plan5_efIncome'] = []
    ans2['plan5_dcExp'] = []
    ans2['plan5_debtIncome'] = []
    ans2['plan5_debtExp'] = []
    ans2['plan5_mpr'] = []
    ans2['plan5_OptExpM'] = []
    ans2['plan5_TaxRate'] = []
    ans2['plan5_invday'] = []
    ans2['plan5_arday'] = []
    ans2['plan5_apday'] = []
    for key in ans2.keys():
        if inputs2[key] == [None]:
            ans2[key].append(0)
        else:
            ans2[key].append(inputs2[key][0])
    if inputs2['re'] == [None]:
        ans2['re'] = get_re(inputs2['Indus_code'])
    else:
        ans2['re'] = inputs2['re']
    if inputs2['debtRate'] == [None]:
        # a=inputs1['利息支出'][-1]/((inputs1['短期借款'][-2]+inputs1['长期借款'][-2]+inputs1['应付债券'][-2])+(inputs1['短期借款'][-1]+inputs1['长期借款'][-1]+inputs1['应付债券'][-1]))*2
        if ((inputs1['短期借款'][-2] + inputs1['长期借款'][-2] + inputs1['应付债券'][-2]) + (
                    inputs1['短期借款'][-1] + inputs1['长期借款'][-1] + inputs1['应付债券'][-1]))==0:
            ans2['debtRate']=[0.07]
        else:
            ans2['debtRate'] = [inputs1['利息支出'][-1] / ((inputs1['短期借款'][-2] + inputs1['长期借款'][-2] + inputs1['应付债券'][-2]) + (
                    inputs1['短期借款'][-1] + inputs1['长期借款'][-1] + inputs1['应付债券'][-1])) * 2]
    else:
        ans2['debtRate'] = inputs2['debtRate']
    ans2['plan5_gr'] = inputs2['plan5_gr']
    ans2['Indus_code'] = inputs2['Indus_code']
    ans2['target_CS'] = [sum(
        [ans2['plan5_debtIncome'][0], inputs1['短期借款'][-1], inputs1['应付票据'][-1], inputs1['长期借款'][-1],
         inputs1['应付债券'][-1]]) / (ans2['plan5_efIncome'][0] + inputs1['母公司股东的权益合计'][-1])]
    
    return ans2

#########最后一个月报是最新月报
def process_MonthFR(inputs1,inputs3):

    month = inputs3['end_month'][0]
    coefficent = (12 - month) / 12
    ans3 = {}
    ############资产负债表相关财报数据
    ans3['Cash']=inputs3['短期金融投资'][-1] + inputs3['货币资金'][-1]
    ans3['AR']=inputs3['应收票据'][-1] + inputs3['应收账款'][-1]
    ans3['PP']=inputs3['预付款项'][-1]
    ans3['Inv']=inputs3['存货'][-1]
    ans3['LTI']=inputs3['长期金融投资'][-1] + inputs3['长期股权投资'][-1]
    ans3['CA']=inputs3['投资性房地产'][-1] + inputs3['固定资产'][-1] + inputs3['在建工程'][-1] + inputs3['无形资产'][-1] + inputs3['开发支出'][
            -1] +inputs3['长期待摊费用'][-1]
    ans3['DTA']=inputs3['递延所得税资产'][-1]
    ans3['OthR']=inputs3['其他应收款'][-1]
    ans3['GW']=inputs3['商誉'][-1]
    ans3['TA']=inputs3['流动资产合计'][-1] + inputs3['非流动资产合计'][-1]
    ans3['TA_rest'] = []
    for e in range(len(inputs1['流动资产合计'])-1):
        ans3['TA_rest'].append(inputs1['流动资产合计'][e]*coefficent + inputs1['非流动资产合计'][e]*coefficent+
                              inputs1['流动资产合计'][e+1]*(1-coefficent) + inputs1['非流动资产合计'][e+1]*(1-coefficent))
    ans3['OthAst']=ans3['TA'] - ans3['Cash'] - ans3['AR'] - ans3['PP'] - ans3['Inv'] - ans3['LTI'] -\
                   ans3['CA'] - ans3['DTA'] - ans3['OthR'] - ans3['GW']
    ans3['Debt']=inputs3['短期借款'][-1] + inputs3['一年以内到期的非流动负债'][-1] + inputs3['长期借款'][-1] + inputs3['应付债券'][-1]
    ans3['AP']=inputs3['应付票据'][-1] + inputs3['应付账款'][-1]
    ans3['AL']=inputs3['预收款项'][-1] + inputs3['应付职工薪酬'][-1]
    ans3['AT']=inputs3['应交税费'][-1]
    ans3['DTL']=inputs3['递延所得税负债'][-1]
    ans3['OthP']=inputs3['其他应付款'][-1]
    ans3['L']=inputs3['流动负债合计'][-1] + inputs3['非流动负债合计'][-1]
    ans3['L_rest']=[]
    for e in range(len(inputs1['流动负债合计'])-1):
        ans3['L_rest'].append(inputs1['流动负债合计'][e]*coefficent + inputs1['非流动负债合计'][e]*coefficent+
                              inputs1['流动负债合计'][e+1]*(1-coefficent) + inputs1['非流动负债合计'][e+1]*(1-coefficent))


    ans3['OthLia']=ans3['L'] - ans3['Debt'] - ans3['AP'] - ans3['AL'] - ans3['AT'] - ans3['DTL'] -ans3['OthP']
    ans3['Contributed_Capital']=inputs3['股本'][-1] + inputs3['资本公积'][-1]
    ans3['RE']=inputs3['母公司股东的权益合计'][-1] - inputs3['股本'][-1] - inputs3['资本公积'][-1]
    ans3['PES']=inputs3['母公司股东的权益合计'][-1]
    ans3['E']=ans3['TA']- ans3['L']
    ans3['ME']=ans3['E'] - inputs3['母公司股东的权益合计'][-1]
    ans3['SC'] = inputs3['股本'][-1]
    ##################利润表及其他财报数据

    #######################各项指标初始化
    INDEXS = ['GR', 'GPM1', 'GPM2', 'ExpM', 'NIPLM', 'Trate', 'MEM', 'DAR', 'Drate', 'ARDay', 'PPDay', 'InvDay',
              'APDay', 'ALDay', 'ATDay']
    for e in INDEXS:
        ans3[e] = False

    if len(inputs3['营业总收入'])==1: #一张月报
        ans3['Rev'] = inputs3['营业总收入'][-1] + inputs1['营业总收入'][-1] * coefficent
        ans3['Cost'] = inputs3['营业成本'][-1] + inputs1['营业成本'][-1] * coefficent
        ans3['BTS'] = inputs3['营业税金及附加'][-1] + inputs1['营业税金及附加'][-1] * coefficent
        ans3['GP'] = ans3['Rev'] - ans3['Cost'] - ans3['BTS']
        temp1 = inputs3['利息支出'][-1] + inputs1['利息支出'][-1] * coefficent \
                - inputs3['利息收入'][-1] - inputs1['利息收入'][-1] * coefficent
        temp2 = inputs3['财务费用'][-1] + inputs1['财务费用'][-1] * coefficent - temp1
        temp3 = inputs3['当期固定资产折旧'][-1] + inputs1['当期固定资产折旧'][-1] * coefficent \
                + inputs3['当期无形资产摊销'][-1] + inputs1['当期无形资产摊销'][-1] * coefficent \
                + inputs3['当期长期待摊费用摊销'][-1] + inputs1['当期长期待摊费用摊销'][-1] * coefficent
        ans3['OptCst'] = inputs3['销售费用'][-1] + inputs1['销售费用'][-1] * coefficent \
                         + inputs3['管理费用'][-1] + inputs1['管理费用'][-1] * coefficent + temp2 - temp3
        ans3['NIPL'] = inputs3['利润总额'][-1] + inputs1['利润总额'][-1] * coefficent - ans3['Rev'] + ans3['Cost'] + ans3[
            'BTS'] + \
                       inputs3['销售费用'][-1] + inputs1['销售费用'][-1] * coefficent + \
                       inputs3['管理费用'][-1] + inputs1['管理费用'][-1] * coefficent \
                       + inputs3['财务费用'][-1] + inputs1['财务费用'][-1] * coefficent
        ans3['EBITDA'] = ans3['GP'] + ans3['NIPL'] - ans3['OptCst']
        ans3['DA'] = temp3
        ans3['EBIT'] = ans3['EBITDA'] - ans3['DA']
        ans3['InsExp'] = inputs3['利息支出'][-1] + inputs1['利息支出'][-1] * coefficent
        ans3['InsIncome'] = inputs3['利息收入'][-1] + inputs1['利息收入'][-1] * coefficent
        ans3['EBT'] = ans3['EBIT'] + ans3['InsIncome'] - ans3['InsExp']
        ans3['NI'] = inputs3['净利润'][-1] + inputs1['净利润'][-1] * coefficent
        ans3['Tax'] = ans3['EBT'] - ans3['NI']

        ans3['PNI'] = inputs3['归属于母公司股东的净利润'][-1] + inputs1['归属于母公司股东的净利润'][-1] * coefficent
        ans3['MPL'] = inputs3['净利润'][-1] + inputs1['净利润'][-1] * coefficent \
                      - inputs3['归属于母公司股东的净利润'][-1] - inputs1['归属于母公司股东的净利润'][-1] * coefficent

        #资产负债表相关 指标
        ##########折旧率 DAR 需年化
        ca=inputs1['投资性房地产'][-1] + inputs1['固定资产'][-1] + inputs1['在建工程'][-1] + inputs1['无形资产'][-1] +\
                       inputs1['开发支出'][-1] +\
                       inputs1['长期待摊费用'][-1]
        da=inputs3['当期固定资产折旧'][-1] + inputs3['当期无形资产摊销'][-1] + inputs3['当期长期待摊费用摊销'][-1]

        if ca==0:
            for e in range(len(inputs1['投资性房地产'])-1):
                ca=inputs1['投资性房地产'][-(e+2)] + inputs1['固定资产'][-(e+2)] + inputs1['在建工程'][-(e+2)] + \
                   inputs1['无形资产'][-(e+2)] +inputs1['开发支出'][-(e+2)] +inputs1['长期待摊费用'][-(e+2)]
                da=inputs1['当期固定资产折旧'][-(e+1)] + inputs1['当期无形资产摊销'][-(e+1)] + inputs1['当期长期待摊费用摊销'][-(e+1)]
                if  ca!=0:
                    ans3['DAR']=da/ca
                    break
        else:
            ans3['DAR'] =da/ca * 12 / month

        ##########存款利息率 Drate 需年化
        if ((ans3['Cash'] + inputs1['短期金融投资'][-1] + inputs1['货币资金'][-1]) / 2)==0:
            ans3['Drate']=0.03
        else:
            ans3['Drate'] = pow(
            inputs3['利息收入'][-1] / ((ans3['Cash'] + inputs1['短期金融投资'][-1] + inputs1['货币资金'][-1]) / 2) + 1, 12 / 5) - 1

        #########应收账款周转天数 ARDay
        if inputs3['营业总收入'][-1]!=0:
            ans3['ARDay'] = (ans3['AR'] + inputs1['应收票据'][-1] + inputs1['应收账款'][-1]) / inputs3['营业总收入'][-1] * 180

        else:
            if  inputs1['营业总收入'][-1]==0:
                wirte_error('process_standard_data_单月报:近三年营业收入含0')
            ans3['ARDay'] = (inputs1['应收票据'][-2] + inputs1['应收账款'][-2] + inputs1['应收票据'][-1] +
                             inputs1['应收账款'][-1]) / inputs1['营业总收入'][-1] * 180

        #########预付款项周转天数 PPDay,存货周转天数 InvDay,应付账款周转天数 APDay
        if inputs3['营业成本'][-1]!=0:
            ans3['PPDay'] = (ans3['PP'] + inputs1['预付款项'][-1]) / inputs3['营业成本'][-1] * 180
            ans3['InvDay'] = (ans3['Inv'] + inputs1['存货'][-1]) / inputs3['营业成本'][-1] * 180
            ans3['APDay'] = (ans3['AP'] + inputs1['应付票据'][-1] + inputs1['应付账款'][-1]) / inputs3['营业成本'][-1] * 180
        else:
            for e in range(len(inputs1['营业成本'])-1):
                if inputs1['营业成本'][-(e+1)]!=0:
                    ans3['PPDay'] = (inputs1['预付款项'][-(e+2)] + inputs1['预付款项'][-(e+1)]) / \
                                    inputs1['营业成本'][-(e+1)] * 180
                    ans3['InvDay'] = (inputs1['存货'][-(e+2)] + inputs1['存货'][-(e+1)]) / inputs1['营业成本'][-(e+1)] * 180
                    ans3['APDay'] = (inputs1['应付票据'][-(e+2)] + inputs1['应付账款'][-(e+2)] + inputs1['应付票据'][-(e+1)]
                                     + inputs1['应付账款'][-(e+1)]) / inputs1['营业成本'][-(e+1)] * 180
                    break


        #########应记负债周转天数 ALDay
        optcst = inputs3['销售费用'][-1] + inputs3['管理费用'][-1] \
                 + (inputs3['财务费用'][-1] - inputs3['利息支出'][-1] + inputs3['利息收入'][-1]) \
                 - (inputs3['当期固定资产折旧'][-1] + inputs3['当期无形资产摊销'][-1] + inputs3['当期长期待摊费用摊销'][-1])
        if optcst!=0:
            ans3['ALDay'] = (ans3['AL'] + inputs1['预收款项'][-1] + inputs1['应付职工薪酬'][-1]) / optcst * 180
        else:
            for e in range(len(inputs1['当期无形资产摊销'])-1):
                optcst = inputs1['销售费用'][-(e+1)] + inputs1['管理费用'][-(e+1)] \
                         + (inputs1['财务费用'][-(e+1)] - inputs1['利息支出'][-(e+1)] + inputs1['利息收入'][-(e+1)]) \
                         - (inputs1['当期固定资产折旧'][-(e+1)] + inputs1['当期无形资产摊销'][-(e+1)] +
                            inputs1['当期长期待摊费用摊销'][-(e+1)])
                if optcst!=0:
                    ans3['ALDay']=(inputs1['预收款项'][-(e+1)] + inputs1['应付职工薪酬'][-(e+1)]+inputs1['预收款项'][-(e+2)] +
                               inputs1['应付职工薪酬'][-(e+2)])/optcst
                    break

        #########应交税费周转天数 ATDay
        if  (inputs3['利润总额'][-1] - inputs3['净利润'][-1])==0:
            for e in range(len(inputs1['利润总额'])-1):
                if inputs1['利润总额'][-(e + 1)] > 0:
                    temptax = inputs1['利润总额'][-(e + 1)] * 0.25
                    ans3['ATDay']=(inputs1['应交税费'][-(e + 1)]+inputs1['应交税费'][-(e + 2)])/temptax * 180
                    break
        else:
            temptax=(inputs3['利润总额'][-1] - inputs3['净利润'][-1])
            ans3['ATDay'] = (ans3['AT'] + inputs1['应交税费'][-1]) / temptax * 180

        ###############################################################################利润表相关指标
        #######营业收入增长率GR
        ans3['GR'] = []
        if 0 in inputs1['营业总收入'][-3:]:
            wirte_error('process_standard_data_单月报:近三年营业收入含0')
        ans3['GR'].append((inputs1['营业总收入'][-1] * (1 - coefficent) + inputs1['营业总收入'][-2] * coefficent) / (
                inputs1['营业总收入'][-2] * (1 - coefficent) + inputs1['营业总收入'][-3] * coefficent) - 1)
        ans3['GR'].append((inputs3['营业总收入'][-1] + inputs1['营业总收入'][-1] * coefficent) / (
                inputs1['营业总收入'][-1] * (1 - coefficent) + inputs1['营业总收入'][-2] * coefficent) - 1)

        ###########毛利率(不含营业税)GPM1

        ans3['GPM1'] = 1 - ans3['Cost'] / ans3['Rev']

        ###########毛利率(含营业税)GPM2
        ans3['GPM2'] = 1 - (ans3['Cost'] + ans3['BTS']) / ans3['Rev']

        #########费用率ExpM
        ans3['ExpM'] = ans3['OptCst'] / ans3['Rev']

        ##########非经常损益占比NIPLM

        ans3['NIPLM'] = ans3['NIPL'] / ans3['Rev']

        ##########借款利息率 Brate
        # Brate = []
        # for e in range(target_len - 1):
        #     Brate.append(ans31['InsExp'][e + 1] / ((ans31['Debt'][e] + ans31['Debt'][e + 1]) / 2))

        ##########所得税率 Trate
        if ans3['EBT']==0:
            ans3['Trate']=0.25
        else:
            ans3['Trate'] = ans3['Tax'] / ans3['EBT']

        ##########少数股东权益占比 MEM
        if ans3['NI']==0:
            for e in range(inputs1['净利润']-1):
                ni=inputs1['净利润'][-(1+e)]*(1-coefficent) + inputs1['净利润'][-(2+e)] * coefficent
                if ni !=0:
                    mpl=inputs1['净利润'][-(1+e)]*(1-coefficent) + inputs1['净利润'][-(2+e)] * coefficent \
                      - inputs1['归属于母公司股东的净利润'][-(1+e)]*(1-coefficent) - \
                        inputs1['归属于母公司股东的净利润'][-(2+e)] * coefficent
                    ans3['MEM']=mpl/ni
                    break
        else:
            ans3['MEM'] = ans3['MPL'] / ans3['NI']
    else:#################两张月报
        ans3['Rev'] = inputs3['营业总收入'][-1] + inputs1['营业总收入'][-1] - inputs3['营业总收入'][-2]
        ans3['Cost'] = inputs3['营业成本'][-1] + inputs1['营业成本'][-1] -inputs3['营业成本'][-2]
        ans3['BTS'] = inputs3['营业税金及附加'][-1] + inputs1['营业税金及附加'][-1] -inputs3['营业税金及附加'][-2]
        ans3['GP'] = ans3['Rev'] - ans3['Cost'] - ans3['BTS']
        temp1 = inputs3['利息支出'][-1] + inputs1['利息支出'][-1] -inputs3['利息支出'][-2] \
                - inputs3['利息收入'][-1] - inputs1['利息收入'][-1] + inputs3['利息收入'][-2]
        temp2 = inputs3['财务费用'][-1] + inputs1['财务费用'][-1] -inputs3['财务费用'][-2] - temp1
        temp3 = inputs3['当期固定资产折旧'][-1] + inputs1['当期固定资产折旧'][-1] -inputs3['当期固定资产折旧'][-2] \
                + inputs3['当期无形资产摊销'][-1] + inputs1['当期无形资产摊销'][-1] -inputs3['当期无形资产摊销'][-2] \
                + inputs3['当期长期待摊费用摊销'][-1] + inputs1['当期长期待摊费用摊销'][-1] -inputs3['当期长期待摊费用摊销'][-2]
        ans3['OptCst'] = inputs3['销售费用'][-1] + inputs1['销售费用'][-1] -inputs3['销售费用'][-2] \
                         + inputs3['管理费用'][-1] + inputs1['管理费用'][-1] -inputs3['管理费用'][-2] + temp2 - temp3
        ans3['NIPL'] = inputs3['利润总额'][-1] + inputs1['利润总额'][-1] -inputs3['利润总额'][-2] - ans3['Rev'] + ans3['Cost'] + ans3[
            'BTS'] + \
                       inputs3['销售费用'][-1] + inputs1['销售费用'][-1] -inputs3['销售费用'][-2] + \
                       inputs3['管理费用'][-1] + inputs1['管理费用'][-1] -inputs3['管理费用'][-2] \
                       + inputs3['财务费用'][-1] + inputs1['财务费用'][-1] -inputs3['财务费用'][-2]
        ans3['EBITDA'] = ans3['GP'] + ans3['NIPL'] - ans3['OptCst']
        ans3['DA'] = temp3
        ans3['EBIT'] = ans3['EBITDA'] - ans3['DA']
        ans3['InsExp'] = inputs3['利息支出'][-1] + inputs1['利息支出'][-1] -inputs3['利息支出'][-2]
        ans3['InsIncome'] = inputs3['利息收入'][-1] + inputs1['利息收入'][-1] -inputs3['利息收入'][-2]
        ans3['EBT'] = ans3['EBIT'] + ans3['InsIncome'] - ans3['InsExp']
        ans3['NI'] = inputs3['净利润'][-1] + inputs1['净利润'][-1] -inputs3['净利润'][-2]
        ans3['Tax'] = ans3['EBT'] - ans3['NI']

        ans3['PNI'] = inputs3['归属于母公司股东的净利润'][-1] + inputs1['归属于母公司股东的净利润'][-1] -inputs3['归属于母公司股东的净利润'][-2]
        ans3['MPL'] = inputs3['净利润'][-1] + inputs1['净利润'][-1] -inputs3['净利润'][-2] \
                      - inputs3['归属于母公司股东的净利润'][-1] - inputs1['归属于母公司股东的净利润'][-1] -inputs3['归属于母公司股东的净利润'][-2]

        #########################################################################################资产负债表相关 指标
        ##########折旧率 DAR
        if (inputs3['投资性房地产'][-2] + inputs3['固定资产'][-2] + inputs3['在建工程'][-2] + inputs3['无形资产'][-2] +
                       inputs3['开发支出'][-2] +
                       inputs3['长期待摊费用'][-2])==0:
            ans3['DAR']=0.02
        else:
            ans3['DAR'] = ans3['DA'] / (inputs3['投资性房地产'][-2] + inputs3['固定资产'][-2] + inputs3['在建工程'][-2] + inputs3['无形资产'][-2] +
                       inputs3['开发支出'][-2] +
                       inputs3['长期待摊费用'][-2])

        ##########存款利息率 Drate 需年化
        if ((ans3['Cash'] + inputs3['短期金融投资'][-2] + inputs3['货币资金'][-2]) / 2)==0:
            ans3['Drate'] = 0.03
        else:
            ans3['Drate'] = ans3['InsIncome'] /((ans3['Cash'] + inputs3['短期金融投资'][-2] + inputs3['货币资金'][-2]) / 2)

        #########应收账款周转天数 ARDay
        # ans3['ARDay'] = (ans3['AR'] + inputs1['应收票据'][-1]
        #  + inputs1['应收账款'][-1]) / inputs3['营业总收入'][-1] * 360 / 2
        ans3['ARDay'] = (ans3['AR'] + inputs3['应收票据'][-2] + inputs3['应收账款'][-2]) / ans3['Rev']* 180

        #########预付款项周转天数 PPDay，存货周转天数 InvDay，应付账款周转天数 APDay
        if ans3['Cost']!=0:
            ans3['PPDay'] = (ans3['PP'] + inputs3['预付款项'][-2]) / ans3['Cost']  * 180
            ans3['InvDay'] = (ans3['Inv'] + inputs3['存货'][-2]) / ans3['Cost'] * 180
            ans3['APDay'] = (ans3['AP'] + inputs3['应付票据'][-2] + inputs3['应付账款'][-2]) / ans3['Cost'] * 180
        else:
            for e in range(len(inputs1['营业成本'])-1):
                if inputs1['营业成本'][-(e+1)]!=0:
                    ans3['PPDay'] = (inputs1['预付款项'][-(e+2)] + inputs1['预付款项'][-(e+1)]) / \
                                    inputs1['营业成本'][-(e+1)] * 180
                    ans3['InvDay'] = (inputs1['存货'][-(e+2)] + inputs1['存货'][-(e+1)]) / inputs1['营业成本'][-(e+1)] * 180
                    ans3['APDay'] = (inputs1['应付票据'][-(e+2)] + inputs1['应付账款'][-(e+2)] + inputs1['应付票据'][-(e+1)]
                                     + inputs1['应付账款'][-(e+1)]) / inputs1['营业成本'][-(e+1)] * 180
                    break

        #########应记负债周转天数 ALDay
        if ans3['OptCst']!=0:
            ans3['ALDay'] = (ans3['AL'] + inputs3['预收款项'][-2] + inputs3['应付职工薪酬'][-2]) / ans3['OptCst'] * 180
        else:
            for e in range(len(inputs1['当期无形资产摊销'])-1):
                optcst = inputs1['销售费用'][-(e+1)] + inputs1['管理费用'][-(e+1)] \
                         + (inputs1['财务费用'][-(e+1)] - inputs1['利息支出'][-(e+1)] + inputs1['利息收入'][-(e+1)]) \
                         - (inputs1['当期固定资产折旧'][-(e+1)] + inputs1['当期无形资产摊销'][-(e+1)] +
                            inputs1['当期长期待摊费用摊销'][-(e+1)])
                if optcst!=0:
                    ans3['ALDay']=(inputs1['预收款项'][-(e+1)] + inputs1['应付职工薪酬'][-(e+1)]+inputs1['预收款项'][-(e+2)] +
                               inputs1['应付职工薪酬'][-(e+2)])/optcst
                    break

        #########应交税费周转天数 ATDay
        if ans3['Tax']!=0:
            ans3['ATDay'] = (ans3['AT'] + inputs3['应交税费'][-2]) / ans3['Tax'] * 180
        else:
            for e in range(len(inputs1['利润总额'])-1):
                if inputs1['利润总额'][-(e + 1)] > 0:
                    temptax = inputs1['利润总额'][-(e + 1)] * 0.25
                    ans3['ATDay'] = (inputs1['应交税费'][-(e + 1)] + inputs1['应交税费'][-(e + 2)]) / temptax * 180
                    break
        ##############################################################333333#################利润表相关指标
        #######营业收入增长率GR
        ans3['GR'] = []
        if 0 in inputs1['营业总收入'][-3:]:
            wirte_error('process_standard_data_单月报:近三年营业收入含0')
        ans3['GR'].append((inputs3['营业总收入'][-2] + inputs1['营业总收入'][-2] * coefficent) / (
                inputs1['营业总收入'][-2] * (1 - coefficent) + inputs1['营业总收入'][-3] * coefficent) - 1)
        ans3['GR'].append((inputs3['营业总收入'][-1] + inputs1['营业总收入'][-1] - inputs3['营业总收入'][-2]) / (
                inputs3['营业总收入'][-2] + inputs1['营业总收入'][-2] * coefficent) - 1)

        ###########毛利率(不含营业税)GPM1
        ans3['GPM1'] = 1 - ans3['Cost'] / ans3['Rev']

        ###########毛利率(含营业税)GPM2
        ans3['GPM2'] = 1 - (ans3['Cost'] + ans3['BTS']) / ans3['Rev']

        #########费用率ExpM
        ans3['ExpM'] = ans3['OptCst'] / ans3['Rev']

        ##########非经常损益占比NIPLM
        ans3['NIPLM'] = ans3['NIPL'] / ans3['Rev']

        ##########借款利息率 Brate
        # Brate = []
        # for e in range(target_len - 1):
        #     Brate.append(ans31['InsExp'][e + 1] / ((ans31['Debt'][e] + ans31['Debt'][e + 1]) / 2))

        ##########所得税率 Trate\
        if ans3['EBT']!=0:
            ans3['Trate'] = ans3['Tax'] / ans3['EBT']
        else:
            ans3['Trate']=0.25


        ##########少数股东权益占比 MEM
        if  ans3['NI']!=0:
            ans3['MEM'] = ans3['MPL'] / ans3['NI']
        else:
            for e in range(inputs1['净利润']-1):
                ni=inputs1['净利润'][-(1+e)]*(1-coefficent) + inputs1['净利润'][-(2+e)] * coefficent
                if ni !=0:
                    mpl=inputs1['净利润'][-(1+e)]*(1-coefficent) + inputs1['净利润'][-(2+e)] * coefficent \
                      - inputs1['归属于母公司股东的净利润'][-(1+e)]*(1-coefficent) - \
                        inputs1['归属于母公司股东的净利润'][-(2+e)] * coefficent
                    ans3['MEM']=mpl/ni
                    break
    for e in INDEXS:
        if ans3[e]==False:
            wirte_error('Error when process standard data 月报 '+e)
    return ans3


def process_addinfo_month(inputs3,inputs1, inputs2):
    ans4 = {}
    month=inputs3['end_month'][0]
    ans4['plan5_fixExp'] = []
    ans4['plan5_ingExp'] = []
    ans4['plan5_efIncome'] = []
    ans4['plan5_dcExp'] = []
    ans4['plan5_debtIncome'] = []
    ans4['plan5_debtExp'] = []
    ans4['plan5_mpr'] = []
    ans4['plan5_OptExpM'] = []
    ans4['plan5_TaxRate'] = []
    ans4['plan5_invday'] = []
    ans4['plan5_arday'] = []
    ans4['plan5_apday'] = []
    for key in ans4.keys():
        if inputs2[key] == [None]:
            ans4[key].append(0)
        else:
            ans4[key].append(inputs2[key][0])
    if inputs2['re'] == [None]:
        ans4['re'] = get_re(inputs2['Indus_code'])
    else:
        ans4['re'] = inputs2['re']
    if inputs2['debtRate'] == [None]:
        if len(inputs3['短期借款'])==1:
            if (((inputs1['短期借款'][-1] + inputs1['长期借款'][-1] + inputs1['应付债券'][-1]) + (
                        inputs3['短期借款'][-1] + inputs3['长期借款'][-1] + inputs3['应付债券'][-1])) / 2)==0:
                ans4['debtRate'] = [0.07]
            else:
                ans4['debtRate'] = [
                pow(inputs3['利息支出'][-1] / (((inputs1['短期借款'][-1] + inputs1['长期借款'][-1] + inputs1['应付债券'][-1]) + (
                        inputs3['短期借款'][-1] + inputs3['长期借款'][-1] + inputs3['应付债券'][-1])) / 2) + 1, 12 / month) - 1]
        else:
            ins_exp=inputs3['利息支出'][-1] + inputs1['利息支出'][-1] -inputs3['利息支出'][-2]
            if ((inputs3['短期借款'][-2] + inputs3['长期借款'][-2] + inputs3['应付债券'][-2] +
              inputs3['短期借款'][-1] + inputs3['长期借款'][-1] + inputs3['应付债券'][-1]) / 2)==0:
                ans4['debtRate']=[0.07]
            else:
                ans4['debtRate']=[ins_exp / (( inputs3['短期借款'][-2] + inputs3['长期借款'][-2] + inputs3['应付债券'][-2] +
                        inputs3['短期借款'][-1] + inputs3['长期借款'][-1] + inputs3['应付债券'][-1]) / 2)]

    else:
        ans4['debtRate'] = inputs2['debtRate']
    ans4['plan5_gr'] = inputs2['plan5_gr']
    ans4['Indus_code'] = inputs2['Indus_code']
    ans4['target_CS'] = [sum(
        [ans4['plan5_debtIncome'][0], inputs3['短期借款'][-1], inputs3['应付票据'][-1], inputs3['长期借款'][-1],
         inputs3['应付债券'][-1]]) / (ans4['plan5_efIncome'][0] + inputs3['母公司股东的权益合计'][-1])]

    return ans4


def process_data(inputs1,inputs2,inputs3=[]):
    if inputs3==[]:
        ans1 = process_YearFR(inputs1)
        ans2 = process_addinfo_year(inputs1, inputs2)
        d={'inputs1':ans1,'inputs2':ans2}

    else:
        ans3=process_MonthFR(inputs1,inputs3)
        ans4=process_addinfo_month(inputs3,inputs1,inputs2)
        d = {'inputs1': ans3, 'inputs2': ans4}

    return d
