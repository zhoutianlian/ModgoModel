# -*- coding: utf-8 -*-
import math

from Tool.functions.base_protect import BaseProtect as bp
from Tool.functions.is_result_legal import result_legal


class EVA():
    def __compute(self,output,wacc,foreva,cost_result):
        ##########通用计算
        df_c=[]
        df_b=[]
        df_a=[]
        eva_c=[]
        eva_b=[]
        eva_a=[]
        ceva_c=[]
        ceva_b=[]
        ceva_a=[]
        predict_pc=[]
        cc=cb=ca=0
        for y in range(len(output['NOPAT'])): # 10+1
            dfc=1.0/math.pow((1+wacc['wacc_min']),y)
            dfb=1.0/math.pow((1+wacc['wacc_avg']),y)
            dfa=1.0/math.pow((1+wacc['wacc_max']),y)

            if y!=0:
                evac=output['NOPAT'][y]-output['E+debt'][y-1]*wacc['wacc_min']
                evab=output['NOPAT'][y]-output['E+debt'][y-1]*wacc['wacc_avg']
                evaa=output['NOPAT'][y]-output['E+debt'][y-1]*wacc['wacc_max']
                cc+=evac*dfc
                cb+=evab*dfb
                ca+=evaa*dfa
                predict_pc.append(math.pow(y-foreva['bestY'],2)*foreva['exitYpc'])
            else:
                evac=output['NOPAT'][0]-output['E+debt'][0]*wacc['wacc_min']
                evab=output['NOPAT'][0]-output['E+debt'][0]*wacc['wacc_avg']
                evaa=output['NOPAT'][0]-output['E+debt'][0]*wacc['wacc_max']

            df_c.append(dfc)
            df_b.append(dfb)
            df_a.append(dfa)
            eva_c.append(evac)
            eva_b.append(evab)
            eva_a.append(evaa)
            ceva_c.append(cc)
            ceva_b.append(cb)
            ceva_a.append(ca)
         ########子模型
        submod={}
        ###1,趋零
        submod['near_zero']={}
        submod['near_zero']['PVTV_c']=[]
        submod['near_zero']['PVTV_b']=[]
        submod['near_zero']['PVTV_a']=[]
        for y in range(len(output['NOPAT'])): # 10+1
            submod['near_zero']['PVTV_c'].append(eva_c[y]*foreva['perpetuity_eva_pc']/(1+wacc['wacc_min']-foreva['perpetuity_eva_pc'])*df_c[y])
            submod['near_zero']['PVTV_b'].append(eva_b[y]*foreva['perpetuity_eva_pc']/(1+wacc['wacc_avg']-foreva['perpetuity_eva_pc'])*df_b[y])
            submod['near_zero']['PVTV_a'].append(eva_a[y]*foreva['perpetuity_eva_pc']/(1+wacc['wacc_max']-foreva['perpetuity_eva_pc'])*df_a[y])
        ###子模型同一项
        for key, value in submod.items():
            submod[key]['isPositive']=[]
            submod[key]['ed_c']=[]
            submod[key]['ed_b']=[]
            submod[key]['ed_a']=[]
            submod[key]['ISM_c']=[]
            submod[key]['ISM_b']=[]
            submod[key]['ISM_a']=[]
            submod[key]['IDM_c']=[]
            submod[key]['IDM_b']=[]
            submod[key]['IDM_a']=[]
            submod[key]['sensi_exitY']=[]
            submod[key]['sensi_Hy']=[]
            submod[key]['s_TVM']=[]
            submod[key]['s_score']=[]
            submod[key]['s_MV_c']=[]
            submod[key]['s_MV_b']=[]
            submod[key]['s_MV_a']=[]
            submod[key]['s_p_c']=[]
            submod[key]['s_p_b']=[]
            submod[key]['s_p_a']=[]
            for y in range(len(output['NOPAT'])):
                if submod[key]['PVTV_c'][y]>0:
                    submod[key]['isPositive'].append(1)
                else:
                    submod[key]['isPositive'].append(0)
                edc=max(ceva_c[y]+submod[key]['PVTV_c'][y]+output['E+debt'][0],output['NetDebt'][0])
                edb=max(ceva_b[y]+submod[key]['PVTV_b'][y]+output['E+debt'][0],output['NetDebt'][0])
                eda=max(ceva_a[y]+submod[key]['PVTV_a'][y]+output['E+debt'][0],output['NetDebt'][0])
                ismc=edc/output['NOPAT'][0]
                ismb=edb/output['NOPAT'][0]
                isma=eda/output['NOPAT'][0]
                idmc=edc/output['NOPAT'][1]
                idmb=edb/output['NOPAT'][1]
                idma=eda/output['NOPAT'][1]
                submod[key]['ed_c'].append(edc)
                submod[key]['ed_b'].append(edb)
                submod[key]['ed_a'].append(eda)
                submod[key]['ISM_c'].append(ismc)
                submod[key]['ISM_b'].append(ismb)
                submod[key]['ISM_a'].append(isma)
                submod[key]['IDM_c'].append(idmc)
                submod[key]['IDM_b'].append(idmb)
                submod[key]['IDM_a'].append(idma)
            for y in range(len(output['NOPAT'])-1):
                if submod[key]['ISM_b'][y+1]!=0:

                    sensiexity=abs(submod[key]['ISM_b'][y+1]-submod[key]['ISM_b'][y])/abs(submod[key]['ISM_b'][y+1])
                    sensihy=abs(submod[key]['ISM_a'][y+1]-submod[key]['ISM_c'][y+1])/abs(submod[key]['ISM_b'][y+1]*2)
                    stvm=submod[key]['PVTV_b'][y+1]/submod[key]['ed_b'][y+1]
                    if output['E+debt'][y+1]<=0 or output['A'][y+1]<=0:
                        sscore=0
                    else:
                        sscore=round(submod[key]['isPositive'][y+1]/(math.pow(predict_pc[y],2)+math.pow(sensiexity,2)+math.pow(sensihy,2)+math.pow(stvm*foreva['TVpc'],2)),6)
                else:
                    sensiexity=False
                    sensihy=False
                    stvm=False
                    sscore=0
                smvc=max(submod[key]['ed_c'][y+1]-output['NetDebt'][0],0)
                smvb=max(submod[key]['ed_b'][y+1]-output['NetDebt'][0],0)
                smva=max(submod[key]['ed_a'][y+1]-output['NetDebt'][0],0)

                spc=smvc/output['SC']
                spb=smvb/output['SC']
                spa=smva/output['SC']
                submod[key]['sensi_exitY'].append(sensiexity)
                submod[key]['sensi_Hy'].append(sensihy)
                submod[key]['s_TVM'].append(stvm)
                submod[key]['s_score'].append(sscore)
                submod[key]['s_MV_c'].append(smvc)
                submod[key]['s_MV_b'].append(smvb)
                submod[key]['s_MV_a'].append(smva)
                submod[key]['s_p_c'].append(spc)
                submod[key]['s_p_b'].append(spb)
                submod[key]['s_p_a'].append(spa)

            if foreva['exitY']=='False':
                submod[key]['score']=max(submod[key]['s_score'])
                for y in range(len(submod[key]['s_score'])):
                    if submod[key]['s_score'][y]==submod[key]['score']:
                        submod[key]['ExitY']=y+1
                        break
            else:
                submod[key]['score']=submod[key]['s_score'][foreva['exitY']]
                submod[key]['ExitY']=foreva['exitY']

            submod[key]['TVM']=submod[key]['s_TVM'][submod[key]['ExitY']-1]
            submod[key]['MV_min']=submod[key]['s_MV_c'][submod[key]['ExitY']-1]
            submod[key]['MV_avg']=submod[key]['s_MV_b'][submod[key]['ExitY']-1]
            submod[key]['MV_max']=submod[key]['s_MV_a'][submod[key]['ExitY']-1]

            #####兜底
            [submod[key]['MV_max'], submod[key]['MV_avg'], submod[key]['MV_min']] = \
                bp(submod[key]['MV_max'], submod[key]['MV_avg'], submod[key]['MV_min'], cost_result['MV_max'],
                   cost_result['MV_avg'], cost_result['MV_min'])
            submod[key]['p_min'] = submod[key]['MV_min'] / output['SC']
            submod[key]['p_avg'] = submod[key]['MV_avg'] / output['SC']
            submod[key]['p_max'] = submod[key]['MV_max'] / output['SC']
            ####阈值判断 错误值检验
            if result_legal('eva'+key,submod[key])==False or submod[key]['PVTV_c'][-1]<=0:
                submod[key]['score']=0
            ####评分调整
            if submod[key]['MV_max'] == cost_result['MV_max'] and submod[key]['MV_avg'] == cost_result['MV_avg'] and \
                    submod[key]['MV_min'] == cost_result['MV_min']:
                submod[key]['score'] = 0.000001

        self.__eva_value={}
        for key, value in submod.items():
            self.__eva_value[key]={}

            self.__eva_value[key]['score']=round(submod[key]['score'],6)
            self.__eva_value[key]['ExitY']=submod[key]['ExitY']
            self.__eva_value[key]['TVM']=round(submod[key]['TVM'],6)
            self.__eva_value[key]['MV_min']=round(submod[key]['MV_min'],2)
            self.__eva_value[key]['MV_avg']=round(submod[key]['MV_avg'],2)
            self.__eva_value[key]['MV_max']=round(submod[key]['MV_max'],2)
            self.__eva_value[key]['p_min']=round(submod[key]['p_min'],2)
            self.__eva_value[key]['p_avg']=round(submod[key]['p_avg'],2)
            self.__eva_value[key]['p_max']=round(submod[key]['p_max'],2)

    def get_output(self,output,wacc,foreva,cost_result):
        self.__compute(output,wacc,foreva,cost_result)
        return self.__eva_value
