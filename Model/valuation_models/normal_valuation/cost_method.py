# -*- coding: utf-8 -*-
import math
import numpy as np
import scipy.stats

from Tool.functions.is_result_legal import result_legal


class Cost():
    def __compute(self,input,riskless_rate):
        net_income_margin = float(input['NI']) / input['Rev'][-1]
        receivables_days = float(input['AR']) / input['Rev'][-1] * 360
        inventory_turnover_days = float(input['Inv']) / input['Rev'][-1] * 360
        payment_period = float(input['AP']) / input['Rev'][-1] * 360
        accounts_rec = []
        inventory = []
        accounts_pay = []
        oprating_cash_flow = []
        old_accounts_rec = 0
        old_inventory = 0
        old_accounts_pay = 0
        count = 0
        for e in input['Rev']: #Rev长度为3
            e=float(e)
            ni=e*net_income_margin
            ar=e*receivables_days/360
            inv=e*inventory_turnover_days/360
            ap=e*payment_period/360

            if count==0:
                old_accounts_rec=ar
                old_inventory=inv
                old_accounts_pay=ap
            else:
                ar_dec=old_accounts_rec-ar
                inv_dec=old_inventory-inv
                ap_inc=ap-old_accounts_pay
                optcf=ni+ar_dec+ap_inc+inv_dec

                old_accounts_rec=ar
                old_inventory=inv
                old_accounts_pay=ap

                oprating_cash_flow.append(optcf)
            accounts_rec.append(ar)
            inventory.append(inv)
            accounts_pay.append(ap)
            count+=1

        cash=[input['Cash']]

        cash.append(input['Cash']-oprating_cash_flow[-1])
        cash.append(input['Cash']-oprating_cash_flow[-1]-oprating_cash_flow[-2])
        cash=list(reversed(cash))
        OthAst=input['TA']-input['Cash']-input['AR']-input['Inv']
        total_asset=[]
        for e in range(len(cash)):
            if e!=len(cash)-1:
                total_asset.append(accounts_rec[e]+cash[e]+accounts_pay[e]+inventory[e]+OthAst)
            else:
                total_asset.append(input['TA'])
        flag=0
        for e in total_asset:
            if e<=0:
                flag=1
        if flag==1:
            cof_rev_growthrate=[math.log(input['Rev'][1])-math.log(input['Rev'][0]),math.log(input['Rev'][2])-math.log(input['Rev'][1])]
        else:
            cof_rev_growthrate=[math.log(total_asset[1])-math.log(total_asset[0]),math.log(total_asset[2])-math.log(total_asset[1])]
        std_cof_rev_growthrate=np.std(cof_rev_growthrate,ddof = 1)
        d1_3=(math.log(total_asset[-1]/input['L'])+(riskless_rate+std_cof_rev_growthrate*std_cof_rev_growthrate/2)*3)/(std_cof_rev_growthrate*math.pow(3,0.5))
        d2_3=d1_3-std_cof_rev_growthrate*math.pow(3,0.5)
        d1_5=(math.log(total_asset[-1]/input['L'])+(riskless_rate+std_cof_rev_growthrate*std_cof_rev_growthrate/2)*5)/(std_cof_rev_growthrate*math.pow(5,0.5))
        d2_5=d1_5-std_cof_rev_growthrate*math.pow(5,0.5)
        d1_8=(math.log(total_asset[-1]/input['L'])+(riskless_rate+std_cof_rev_growthrate*std_cof_rev_growthrate/2)*8)/(std_cof_rev_growthrate*math.pow(8,0.5))
        d2_8=d1_8-std_cof_rev_growthrate*math.pow(8,0.5)

        self.__output={}
        self.__output['MV_min']=total_asset[-1]*scipy.stats.norm(0,1).cdf(d1_3)-input['L']*math.pow(math.e,3*-riskless_rate)*scipy.stats.norm(0,1).cdf(d2_3)
        self.__output['MV_avg']=total_asset[-1]*scipy.stats.norm(0,1).cdf(d1_5)-input['L']*math.pow(math.e,5*-riskless_rate)*scipy.stats.norm(0,1).cdf(d2_5)
        self.__output['MV_max']=total_asset[-1]*scipy.stats.norm(0,1).cdf(d1_8)-input['L']*math.pow(math.e,8*-riskless_rate)*scipy.stats.norm(0,1).cdf(d2_8)
        self.__output['p_min']=self.__output['MV_min']/input['SC']
        self.__output['p_avg']=self.__output['MV_avg']/input['SC']
        self.__output['p_max']=self.__output['MV_max']/input['SC']
        if result_legal('Cost_method',self.__output)==False:
            self.__output=False

    def get_output(self,input,riskless_rate=0.04):
        self.__compute(input,riskless_rate)
        return self.__output






