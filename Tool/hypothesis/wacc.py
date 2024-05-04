# -*- coding: utf-8 -*-：
##Input 数据结构{re_avg，re_min，re_max，debtcost，IncomeTaxR，CS}
#股东要求回报率-基准		re_avg
#股东要求回报率-差			re_min
#股东要求回报率-好		re_max
#债务成本			debtcost
#公司所得税率			IncomeTaxR
#目标资本结构			CS
# 债务成本	output.Dr
# 公司所得税率	output.IncomeTaxR
# 目标资本结构	TCS(从数据库取) D/E


def WACC(re,a,TCS):
    output={}
    Input={}
    Input['re_avg']=re
    Input['re_min']=Input['re_avg']+0.01
    Input['re_max']=Input['re_avg']-0.01
    Input['debtcost']=a['Dr']
    Input['IncomeTaxR']=a['IncomeTaxR']
    Input['CS']=TCS


    output['wacc_avg']=round(float(Input['CS'])/(1+Input['CS'])*(1-Input['IncomeTaxR'])*Input['debtcost']+1/(Input['CS']+1)*Input['re_avg'],6)
    output['wacc_min']=round(float(Input['CS'])/(1+Input['CS'])*(1-Input['IncomeTaxR'])*Input['debtcost']+1/(Input['CS']+1)*Input['re_min'],6)
    output['wacc_max']=round(float(Input['CS'])/(1+Input['CS'])*(1-Input['IncomeTaxR'])*Input['debtcost']+1/(Input['CS']+1)*Input['re_max'],6)
    output['re_avg']=round(Input['re_avg'],6)
    output['re_max']=round(Input['re_max'],6)
    output['re_min']=round(Input['re_min'],6)

    # output['wacc_avg']=0.15
    # output['wacc_min']=0.16
    # output['wacc_max']=0.14
    # output['re_avg']=0.15
    # output['re_max']=0.14
    # output['re_min']=0.16
    return output



