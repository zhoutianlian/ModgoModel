# -*- coding: utf-8 -*-
import math

from Tool.functions.base_protect import BaseProtect as bp
from Tool.functions.is_result_legal import result_legal


class RIM:
    def __compute(self,output,wacc,forri,cost_result):
        ##########通用计算
        df_c=[]
        df_b=[]
        df_a=[]
        ri_c=[]
        ri_b=[]
        ri_a=[]
        cRI_c=[]
        cRI_b=[]
        cRI_a=[]
        predict_pc=[]
        cc=cb=ca=0
        for y in range(len(output['NI'])): # 10+1
            dfc=1.0/math.pow((1+wacc['re_min']),y)
            dfb=1.0/math.pow((1+wacc['re_avg']),y)
            dfa=1.0/math.pow((1+wacc['re_max']),y)

            if y!=0:
                ric=output['NI'][y]-output['B'][y-1]*wacc['re_min']
                rib=output['NI'][y]-output['B'][y-1]*wacc['re_avg']
                ria=output['NI'][y]-output['B'][y-1]*wacc['re_max']
                cc+=ric*dfc
                cb+=rib*dfb
                ca+=ria*dfa
                predict_pc.append(math.pow(y-forri['bestY'],2)*forri['exitYpc'])

            else:
                ric=output['NI'][0]-output['B'][0]*wacc['re_min']
                rib=output['NI'][0]-output['B'][0]*wacc['re_avg']
                ria=output['NI'][0]-output['B'][0]*wacc['re_max']

            df_c.append(dfc)
            df_b.append(dfb)
            df_a.append(dfa)
            ri_c.append(ric)
            ri_b.append(rib)
            ri_a.append(ria)
            cRI_c.append(cc)
            cRI_b.append(cb)
            cRI_a.append(ca)
        ########子模型
        submod={}
        ###1,趋零
        submod['near_zero']={}
        submod['near_zero']['PVTV_c']=[]
        submod['near_zero']['PVTV_b']=[]
        submod['near_zero']['PVTV_a']=[]
        for y in range(len(output['NI'])): # 10+1
            submod['near_zero']['PVTV_c'].append(ri_c[y]*forri['perpetuity_ri_pc']/(1+wacc['re_min']-forri['perpetuity_ri_pc'])*df_c[y])
            submod['near_zero']['PVTV_b'].append(ri_b[y]*forri['perpetuity_ri_pc']/(1+wacc['re_avg']-forri['perpetuity_ri_pc'])*df_b[y])
            submod['near_zero']['PVTV_a'].append(ri_a[y]*forri['perpetuity_ri_pc']/(1+wacc['re_max']-forri['perpetuity_ri_pc'])*df_a[y])
        ###子模型同一项
        for key, value in submod.items():
            submod[key]['isPositive']=[]
            submod[key]['s_MV_c']=[]
            submod[key]['s_MV_b']=[]
            submod[key]['s_MV_a']=[]
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

            for y in range(len(output['NI'])):
                if submod[key]['PVTV_c'][y]>0:
                    submod[key]['isPositive'].append(1)
                else:
                    submod[key]['isPositive'].append(0)
                smvc=max(cRI_c[y]+submod[key]['PVTV_c'][y]+output['B'][0],0)
                smvb=max(cRI_b[y]+submod[key]['PVTV_b'][y]+output['B'][0],0)
                smva=max(cRI_a[y]+submod[key]['PVTV_a'][y]+output['B'][0],0)

                ismc=smvc/output['NI'][0]
                ismb=smvb/output['NI'][0]
                isma=smva/output['NI'][0]
                idmc=smvc/output['NI'][1]
                idmb=smvb/output['NI'][1]
                idma=smva/output['NI'][1]
                submod[key]['s_MV_c'].append(smvc)
                submod[key]['s_MV_b'].append(smvb)
                submod[key]['s_MV_a'].append(smva)
                submod[key]['ISM_c'].append(ismc)
                submod[key]['ISM_b'].append(ismb)
                submod[key]['ISM_a'].append(isma)
                submod[key]['IDM_c'].append(idmc)
                submod[key]['IDM_b'].append(idmb)
                submod[key]['IDM_a'].append(idma)
            for y in range(len(output['NI'])-1):
                if submod[key]['ISM_b'][y+1]!=0:
                    sensiexity=abs(submod[key]['ISM_b'][y+1]-submod[key]['ISM_b'][y])/abs(submod[key]['ISM_b'][y+1])
                    sensihy=abs(submod[key]['ISM_a'][y+1]-submod[key]['ISM_c'][y+1])/abs(submod[key]['ISM_b'][y+1]*2)
                    stvm=submod[key]['PVTV_b'][y+1]/submod[key]['s_MV_b'][y+1]
                    if  output['B'][y+1]<=0:
                        sscore=0
                    else:
                        sscore=round(submod[key]['isPositive'][y+1]/(math.pow(predict_pc[y],2)+math.pow(sensiexity,2)+
                                                                     math.pow(sensihy,2)+math.pow(stvm*forri['TVpc'],2)),6)
                else:
                    sensiexity=False
                    sensihy=False
                    stvm=False
                    sscore=0



                submod[key]['sensi_exitY'].append(sensiexity)
                submod[key]['sensi_Hy'].append(sensihy)
                submod[key]['s_TVM'].append(stvm)
                submod[key]['s_score'].append(sscore)


            if forri['exitY']=='False':
                submod[key]['score']=max(submod[key]['s_score'])
                for y in range(len(submod[key]['s_score'])):
                    if submod[key]['s_score'][y]==submod[key]['score']:
                        submod[key]['ExitY']=y+1
                        break
            else:
                submod[key]['score']=submod[key]['s_score'][forri['exitY']]
                submod[key]['ExitY']=forri['exitY']
            submod[key]['TVM']=submod[key]['s_TVM'][submod[key]['ExitY']-1]
            submod[key]['MV_min']=submod[key]['s_MV_c'][submod[key]['ExitY']]
            submod[key]['MV_avg']=submod[key]['s_MV_b'][submod[key]['ExitY']]
            submod[key]['MV_max']=submod[key]['s_MV_a'][submod[key]['ExitY']]
            #####兜底
            [submod[key]['MV_max'], submod[key]['MV_avg'], submod[key]['MV_min']] = \
                bp(submod[key]['MV_max'], submod[key]['MV_avg'], submod[key]['MV_min'], cost_result['MV_max'],
                   cost_result['MV_avg'], cost_result['MV_min'])
            submod[key]['p_min'] = submod[key]['MV_min'] / output['SC']
            submod[key]['p_avg'] = submod[key]['MV_avg'] / output['SC']
            submod[key]['p_max'] = submod[key]['MV_max'] / output['SC']
            ####阈值判断 and 错误值检验
            if result_legal("rim"+key,submod[key])==False or submod[key]['PVTV_c'][-1]<=0:
                submod[key]['score']=0
            ####评分调整
            if submod[key]['MV_max'] == cost_result['MV_max'] and submod[key]['MV_avg'] == cost_result['MV_avg'] and \
                        submod[key]['MV_min'] == cost_result['MV_min']:
                submod[key]['score'] = 0.000001

        self.__rim_value={}
        for key, value in submod.items():

            self.__rim_value[key]={}
            self.__rim_value[key]['score']=round(submod[key]['score'],6)
            self.__rim_value[key]['ExitY']=submod[key]['ExitY']
            self.__rim_value[key]['TVM']=round(submod[key]['TVM'],6)
            self.__rim_value[key]['MV_min']=round(submod[key]['MV_min'],2)
            self.__rim_value[key]['MV_avg']=round(submod[key]['MV_avg'],2)
            self.__rim_value[key]['MV_max']=round(submod[key]['MV_max'],2)
            self.__rim_value[key]['p_min']=round(submod[key]['p_min'],2)
            self.__rim_value[key]['p_avg']=round(submod[key]['p_avg'],2)
            self.__rim_value[key]['p_max']=round(submod[key]['p_max'],2)

    def get_output(self,output,wacc,forri,cost_result):
        self.__compute(output,wacc,forri,cost_result)
        return self.__rim_value