# -*- coding: utf-8 -*-
import math
from Tool.functions.base_protect import BaseProtect as bp
from Tool.functions.is_result_legal import result_legal


class NOPAT:
    def __compute(self,output,wacc,fornop,cost_result):
        ##########通用计算
        df_c=[]
        df_b=[]
        df_a=[]
        cNOPAT_c=[]
        cNOPAT_b=[]
        cNOPAT_a=[]
        predict_pc=[]
        cc=cb=ca=0
        for y in range(len(output['NOPAT'])): # 10+1
            dfc=1.0/math.pow((1+wacc['wacc_min']),y)
            dfb=1.0/math.pow((1+wacc['wacc_avg']),y)
            dfa=1.0/math.pow((1+wacc['wacc_max']),y)

            if y!=0:
                cc+=output['NOPAT'][y]*dfc
                cb+=output['NOPAT'][y]*dfb
                ca+=output['NOPAT'][y]*dfa
                predict_pc.append(math.pow(y-fornop['bestY'],2)*fornop['exitYpc'])

            df_c.append(dfc)
            df_b.append(dfb)
            df_a.append(dfa)
            cNOPAT_c.append(cc)
            cNOPAT_b.append(cb)
            cNOPAT_a.append(ca)
        ########子模型
        submod={}
        ###1,固定增长率
        submod['fix_gr']={}
        if True:
            submod['fix_gr']['flag']=True
        else:
            submod['fix_gr']['flag']=False

        submod['fix_gr']['PVTV_c']=[]
        submod['fix_gr']['PVTV_b']=[]
        submod['fix_gr']['PVTV_a']=[]
        for y in range(len(output['NOPAT'])): # 10+1
            submod['fix_gr']['PVTV_c'].append(output['NOPAT'][y]*(1+fornop['perpetuity_g_c'][y])/(wacc['wacc_min']-fornop['perpetuity_g_c'][y])*df_c[y])
            submod['fix_gr']['PVTV_b'].append(output['NOPAT'][y]*(1+fornop['perpetuity_g_b'][y])/(wacc['wacc_avg']-fornop['perpetuity_g_b'][y])*df_b[y])
            submod['fix_gr']['PVTV_a'].append(output['NOPAT'][y]*(1+fornop['perpetuity_g_a'][y])/(wacc['wacc_max']-fornop['perpetuity_g_a'][y])*df_a[y])

        ###2,价值驱动
        submod['value_drive']={}
        if True:
            submod['value_drive']['flag']=True
        else:
            submod['value_drive']['flag']=False
        submod['value_drive']['NOPAT_g']=[]
        submod['value_drive']['A_g']=[]
        submod['value_drive']['ed_r']=[]
        submod['value_drive']['VDF_c']=[]
        submod['value_drive']['VDF_b']=[]
        submod['value_drive']['VDF_a']=[]
        submod['value_drive']['PVTV_c']=[]
        submod['value_drive']['PVTV_b']=[]
        submod['value_drive']['PVTV_a']=[]
        for y in range(len(output['NOPAT'])):
            if y==0:
                ng=output['NOPAT'][y+1]/output['NOPAT'][y]-1
                ag=output['A'][y+1]/output['A'][y]-1
                edr=output['NOPAT'][y+1]/output['E+debt'][y]

            else:
                ng=output['NOPAT'][y]/output['NOPAT'][y-1]-1
                ag=output['A'][y]/output['A'][y-1]-1
                edr=output['NOPAT'][y]/output['E+debt'][y-1]
            vc=(1-(ag/fornop['perpetuity_g_pc'])/(edr/fornop['perpetuity_ed_pc']))/(wacc['wacc_min']-ag/fornop['perpetuity_g_pc'])
            vb=(1-(ag/fornop['perpetuity_g_pc'])/(edr/fornop['perpetuity_ed_pc']))/(wacc['wacc_avg']-ag/fornop['perpetuity_g_pc'])
            va=(1-(ag/fornop['perpetuity_g_pc'])/(edr/fornop['perpetuity_ed_pc']))/(wacc['wacc_max']-ag/fornop['perpetuity_g_pc'])
            pc=output['NOPAT'][y]*vc*df_c[y]
            pb=output['NOPAT'][y]*vb*df_b[y]
            pa=output['NOPAT'][y]*va*df_a[y]


            submod['value_drive']['NOPAT_g'].append(ng)
            submod['value_drive']['A_g'].append(ag)
            submod['value_drive']['ed_r'].append(edr)
            submod['value_drive']['VDF_c'].append(vc)
            submod['value_drive']['VDF_b'].append(vb)
            submod['value_drive']['VDF_a'].append(va)
            submod['value_drive']['PVTV_c'].append(pc)
            submod['value_drive']['PVTV_b'].append(pb)
            submod['value_drive']['PVTV_a'].append(pa)

        ###3,退出乘数
        submod['exitm']={}
        # if min(output['NOPAT'])>0 and fornop['MVIC/NOPAT']!=False and fornop['m_MVIC/NOPAT']!=False and fornop['std_MVIC/NOPAT']!=False:
        if fornop['MVIC/NOPAT'] != False and fornop['m_MVIC/NOPAT'] != False and fornop[
            'std_MVIC/NOPAT'] != False:

            submod['exitm']['flag']=True
            # print ('pass exitm')
        else:
            submod['exitm']['flag']=False
        if submod['exitm']['flag']:
            submod['exitm']['ExM_c']=[]
            submod['exitm']['ExM_b']=[]
            submod['exitm']['ExM_a']=[]
            submod['exitm']['PVTV_c']=[]
            submod['exitm']['PVTV_b']=[]
            submod['exitm']['PVTV_a']=[]
            for y in range(len(output['NOPAT'])):
                if y==0:
                    exmc=fornop['MVIC/NOPAT']-fornop['std_MVIC/NOPAT']*fornop['range_std']
                    exmb=fornop['MVIC/NOPAT']
                    exma=fornop['MVIC/NOPAT']+fornop['std_MVIC/NOPAT']*fornop['range_std']
                else:
                    exmc=(exmc-fornop['m_MVIC/NOPAT'])*fornop['M_pc']+fornop['m_MVIC/NOPAT']
                    exmb=(exmb-fornop['m_MVIC/NOPAT'])*fornop['M_pc']+fornop['m_MVIC/NOPAT']
                    exma=(exma-fornop['m_MVIC/NOPAT'])*fornop['M_pc']+fornop['m_MVIC/NOPAT']
                pc=exmc*output['NOPAT'][y]*df_c[y]
                pb=exmb*output['NOPAT'][y]*df_b[y]
                pa=exma*output['NOPAT'][y]*df_a[y]
                submod['exitm']['ExM_c'].append(exmc)
                submod['exitm']['ExM_b'].append(exmb)
                submod['exitm']['ExM_a'].append(exma)
                submod['exitm']['PVTV_c'].append(pc)
                submod['exitm']['PVTV_b'].append(pb)
                submod['exitm']['PVTV_a'].append(pa)

        ###子模型同一项
        for key, value in submod.items():
            if submod[key]['flag']==False :
                continue
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

            for y in range(len(output['NOPAT'])):
                if submod[key]['PVTV_c'][y]>0:
                    submod[key]['isPositive'].append(1)
                else:
                    submod[key]['isPositive'].append(0)
                edc=max(cNOPAT_c[y]+submod[key]['PVTV_c'][y],output['NetDebt'][0])
                edb=max(cNOPAT_b[y]+submod[key]['PVTV_b'][y],output['NetDebt'][0])
                eda=max(cNOPAT_a[y]+submod[key]['PVTV_a'][y],output['NetDebt'][0])
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
                        sscore=round(submod[key]['isPositive'][y+1]/(math.pow(predict_pc[y],2)+math.pow(sensiexity,2)+math.pow(sensihy,2)+math.pow(stvm*fornop['TVpc'],2)),6)
                else:

                    sensiexity=False
                    sensihy=False
                    stvm=False
                    sscore=0

                smvc=max(submod[key]['ed_c'][y+1]-output['NetDebt'][0],0)
                smvb=max(submod[key]['ed_b'][y+1]-output['NetDebt'][0],0)
                smva=max(submod[key]['ed_a'][y+1]-output['NetDebt'][0],0)


                submod[key]['sensi_exitY'].append(sensiexity)
                submod[key]['sensi_Hy'].append(sensihy)
                submod[key]['s_TVM'].append(stvm)
                submod[key]['s_score'].append(sscore)
                submod[key]['s_MV_c'].append(smvc)
                submod[key]['s_MV_b'].append(smvb)
                submod[key]['s_MV_a'].append(smva)

            if fornop['exitY']=='False':
                submod[key]['score']=max(submod[key]['s_score'])
                for y in range(len(submod[key]['s_score'])):
                    if submod[key]['s_score'][y]==submod[key]['score']:
                        submod[key]['ExitY']=y+1
                        break
            else:
                submod[key]['score']=submod[key]['s_score'][fornop['exitY']]
                submod[key]['ExitY']=fornop['exitY']

            submod[key]['TVM']=submod[key]['s_TVM'][submod[key]['ExitY']-1]
            submod[key]['MV_min']=submod[key]['s_MV_c'][submod[key]['ExitY']-1]
            submod[key]['MV_avg']=submod[key]['s_MV_b'][submod[key]['ExitY']-1]
            submod[key]['MV_max']=submod[key]['s_MV_a'][submod[key]['ExitY']-1]

            #####兜底
            [submod[key]['MV_max'],submod[key]['MV_avg'],submod[key]['MV_min']]=\
                bp(submod[key]['MV_max'],submod[key]['MV_avg'],submod[key]['MV_min'],cost_result['MV_max'],
                   cost_result['MV_avg'],cost_result['MV_min'])
            submod[key]['p_min']=submod[key]['MV_min']/output['SC']
            submod[key]['p_avg']=submod[key]['MV_avg']/output['SC']
            submod[key]['p_max']=submod[key]['MV_max']/output['SC']
            ####阈值判断and错误值检验
            if result_legal("nopat"+key,submod[key])==False or submod[key]['PVTV_c'][-1]<=0 or submod[key]['flag']==False \
                or output['NOPAT'][submod[key]['ExitY']]<0:
                submod[key]['score']=0
            #对价值驱动法双重判断
            if key == 'value_drive':
                if submod[key]['VDF_c'][submod[key]['ExitY']]>submod[key]['VDF_b'][submod[key]['ExitY']] or \
                        submod[key]['VDF_b'][submod[key]['ExitY']]>submod[key]['VDF_a'][submod[key]['ExitY']]:
                    submod[key]['score'] = 0
            ####评分调整
            if submod[key]['MV_max']==cost_result['MV_max'] and submod[key]['MV_avg']==cost_result['MV_avg'] \
                    and submod[key]['MV_min']==cost_result['MV_min']:
                submod[key]['score'] = 0.000001


        self.__nopat_value={}
        for key, value in submod.items():
            self.__nopat_value[key]={}
            if submod[key]['flag']==False:
                continue

            self.__nopat_value[key]['score']=round(submod[key]['score'],6)
            self.__nopat_value[key]['ExitY']=submod[key]['ExitY']
            self.__nopat_value[key]['exit_value'] = submod[key]['PVTV_b'][submod[key]['ExitY']-1]
            self.__nopat_value[key]['TVM']=round(submod[key]['TVM'],6)
            self.__nopat_value[key]['MV_min']=round(submod[key]['MV_min'],2)
            self.__nopat_value[key]['MV_avg']=round(submod[key]['MV_avg'],2)
            self.__nopat_value[key]['MV_max']=round(submod[key]['MV_max'],2)
            self.__nopat_value[key]['p_min']=round(submod[key]['p_min'],2)
            self.__nopat_value[key]['p_avg']=round(submod[key]['p_avg'],2)
            self.__nopat_value[key]['p_max']=round(submod[key]['p_max'],2)
        # self.__nopat_value["exitm"]["TVM"] = self.__nopat_value["exitm"]["TVM"].item()
    def get_output(self,output,wacc,fornop,cost_result):
        self.__compute(output,wacc,fornop,cost_result)
        return self.__nopat_value










