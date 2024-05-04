# -*- coding: utf-8 -*-
import numpy as np
import math

from Config.mongodb import read_mongo_limit, read_mongo_all, get_last_update_date
from Tool.functions.base_protect import BaseProtect as bp
from Tool.functions.dlol import mkt_dlol
from Tool.functions.semi_std import semi_std
from Tool.functions.is_result_legal import result_legal
from Report.Log import logger

#market_value:从数据库里取到的市场法的值A【行业一，行业二】
#先对不同市场的指数进行平衡权重，得到估值后再次折价,如今进行流动性折价self.__DLOL=1/(1+0.15)


class Market_Mtd:

    def compute(self,output,pc,indus_cod, cost_result, args, code_list):
        ##判断行业分组
        self.__indus1=[]
        self.__indus2=[]
        self.__code = {}
        self.peer_list = []
        self.__p1=0
        self.__p2=0
        # 获取流动性折价
        self.__DLOL=mkt_dlol(args)
        count=0
        for key,value in indus_cod.items():
            if count==0:
                self.__indus1.append(key)
                self.__code[key] = code_list[0]
                self.__p1=value
                # for code in self.__code1:
                #     if code.e
            else:
                self.__indus2.append(key)
                self.__code[key] = code_list[1]
                self.__p2=value
            count+=1

        for key,value in indus_cod.items():
            if value==self.__p1:
                self.__indus1.append(key)
            else:
                self.__indus2.append(key)
        ############行业分组判断结束
        try:
            market_value_A={}
            # market_value_3={}
            weight_A={}
            # weight_3={}

            ##############################################A股市场行情_A############
            for key in indus_cod.keys():
                market_value_A[key]={}
                weight_A[key]=[]

                ########日更数据
                # data = read_mongo_limit("AM_hypothesis", "Mkt_A", {"GICS3_code": int(key)}, {"_id": 0})
                date = get_last_update_date("AM_hypothesis", "Mkt_A")
                data = read_mongo_limit("AM_hypothesis", "Mkt_A", {"update_date": date,
                                                                   "StockCode": {"$in": self.__code[key]}}, {"_id": 0})
                name1=['PE','PE_p','PB','PB_p','EV_SALE','EV_SALE_p','EV_NOPAT','EV_EBIT','EBIT_REV']
                for e in name1:
                    market_value_A[key][e] = data[e].tolist()
                if not self.peer_list:
                    self.peer_list = data["StockCode"].tolist()
                else:
                    self.peer_list.extend(data["StockCode"].tolist())
                    self.peer_list = list(set(self.peer_list))
                ########季更数据
                # data = read_mongo_limit("AM_hypothesis", "Mkt_AA", {"GICS3_code": int(key)}, {"_id": 0})
                date = get_last_update_date("AM_hypothesis", "Mkt_AA")
                data = read_mongo_limit("AM_hypothesis", "Mkt_AA", {"update_date": date,
                                                                    "StockCode": {"$in": self.__code[key]}}, {"_id": 0})
                name2=[ 'A','GPM','D_A','NIM' ]
                for e in name2:
                    market_value_A[key][e] = data[e].tolist()

                ########年更数据
                # data = read_mongo_limit("AM_hypothesis", "Mkt_AAA", {"GICS3_code": int(key)}, {"_id": 0})
                date = get_last_update_date("AM_hypothesis", "Mkt_AAA")
                data = read_mongo_limit("AM_hypothesis", "Mkt_AAA", {"update_date": date,
                                                                     "StockCode": {"$in": self.__code[key]}}, {"_id": 0})
                name3 = ['Rev_g']
                for e in name3:
                    market_value_A[key][e] = data[e].tolist()

                ##########A股比重
                count_list = []
                for index, value in market_value_A[key].items():
                    count_list.append(len(value))

                for e in range(min(count_list)):
                    if output['A'][0]>0 and float(market_value_A[key]['A'][e])>0 or output['A'][0]<0 and  float(market_value_A[key]['A'][e])<0:
                        c1=2*output['A'][0]*float(market_value_A[key]['A'][e])/(math.pow(float(market_value_A[key]['A'][e]),2)+math.pow(output['A'][0],2))
                    else:
                        c1=0
                    if output['GR']>0 and float(market_value_A[key]['Rev_g'][e])>0 or output['GR']<0 and float(market_value_A[key]['Rev_g'][e])<0:
                        c2=2*output['GR']*float(market_value_A[key]['Rev_g'][e])/(math.pow(float(market_value_A[key]['Rev_g'][e]),2)+math.pow(output['GR'],2))
                    else:
                        c2=0
                    if output['D/E']!=0 and (output['D/E']+1)!=0 and (float(market_value_A[key]['D_A'][e])>0 and (output['D/E']/(output['D/E']+1))>0) or ((output['D/E']/(output['D/E']+1))<0 and float(market_value_A[key]['D_A'][e])<0):
                        c3=2*(output['D/E']/(output['D/E']+1))*float(market_value_A[key]['D_A'][e])/(math.pow(float(market_value_A[key]['D_A'][e]),2)+math.pow((output['D/E']/(output['D/E']+1)),2))
                    else:
                        c3=0
                    if output['Rev'][0]!=0 and output['EBIT'][0]!=0 and (float(market_value_A[key]['GPM'][e])>0 and output['EBIT'][0]/output['Rev'][0]>0) or (output['EBIT'][0]/output['Rev'][0]<0 and float(market_value_A[key]['GPM'][e])<0) :
                        c4=2*output['EBIT'][0]/output['Rev'][0]*float(market_value_A[key]['GPM'][e])/(math.pow(float(market_value_A[key]['GPM'][e]),2)+math.pow(output['EBIT'][0]/output['Rev'][0],2))
                    else:
                        c4=0

                    w= c1+c2+c3+c4
                    weight_A[key].append(w)
            ##############################################三板股市场行情_3############
            # for key in indus_cod.keys():
            #     market_value_3[key]={}
            #     weight_3[key]=[]
            #     ########日更数据
            #     data = read_mongo_limit("AM_hypothesis", "Mkt_3", {"GICS3_code": int(key)}, {"_id": 0})
            #     name1=['PE','PE_p','PB','PB_p','EV_SALE','EV_SALE_p','EV_NOPAT','EV_EBIT','EBIT_REV']
            #     for e in name1:
            #         market_value_3[key][e] = data[e].tolist()
            #
            #     ########季更数据
            #
            #     ########年更数据
            #     data = read_mongo_limit("AM_hypothesis", "Mkt_333", {"GICS3_code": int(key)}, {"_id": 0})
            #     name3=[ 'Rev_g','A','GPM','D_A','NIM' ]
            #     for e in name3:
            #         market_value_3[key][e] = data[e].tolist()
            #
            #     ##########三板比重
            #     for e in range(len(market_value_3[key]['PE'])):
            #         if output['A'][0]>0 and float(market_value_3[key]['A'][e])>0 or output['A'][0]<0 and  float(market_value_3[key]['A'][e])<0:
            #             c1=2*output['A'][0]*float(market_value_3[key]['A'][e])/(math.pow(float(market_value_3[key]['A'][e]),2)+math.pow(output['A'][0],2))
            #         else:
            #             c1=0
            #         if output['GR']>0 and float(market_value_3[key]['Rev_g'][e])>0 or output['GR']<0 and float(market_value_3[key]['Rev_g'][e])<0:
            #             c2=2*output['GR']*float(market_value_3[key]['Rev_g'][e])/(math.pow(float(market_value_3[key]['Rev_g'][e]),2)+math.pow(output['GR'],2))
            #         else:
            #             c2=0
            #         if output['D/E']!=0 and (output['D/E']+1)!=0 and (float(market_value_3[key]['D_A'][e])>0 and (output['D/E']/(output['D/E']+1))>0) or ((output['D/E']/(output['D/E']+1))<0 and float(market_value_3[key]['D_A'][e])<0):
            #             c3=2*(output['D/E']/(output['D/E']+1))*float(market_value_3[key]['D_A'][e])/(math.pow(float(market_value_3[key]['D_A'][e]),2)+math.pow((output['D/E']/(output['D/E']+1)),2))
            #         else:
            #             c3=0
            #         if output['Rev'][0]!=0 and output['EBIT'][0]!=0 and (float(market_value_3[key]['GPM'][e])>0 and output['EBIT'][0]/output['Rev'][0]>0) or (output['EBIT'][0]/output['Rev'][0]<0 and float(market_value_3[key]['GPM'][e])<0) :
            #             c4=2*output['EBIT'][0]/output['Rev'][0]*float(market_value_3[key]['GPM'][e])/(math.pow(float(market_value_3[key]['GPM'][e]),2)+math.pow(output['EBIT'][0]/output['Rev'][0],2))
            #         else:
            #             c4=0
            #
            #         w= c1+c2+c3+c4
            #         weight_3[key].append(w)
        except Exception as e:
            logger(2, e)
        #######存为内部变量
        # self.__market_value3=market_value_3
        self.__market_valueA=market_value_A
        self.__weightA=weight_A
        # self.__weight3=weight_3
        #####估值结果
        self.__result={}
        self.__result['PE0']=self.__PE(pc,output,cost_result)
        self.__result['PE1']=self.__PEp(pc,output,cost_result)
        self.__result['PB0']=self.__PB(pc,output,cost_result)
        self.__result['PB1']=self.__PBp(pc,output,cost_result)
        self.__result['EVS0']=self.__EV_S(pc,output,cost_result)
        self.__result['EVS1']=self.__EV_Sp(pc,output,cost_result)
        self.__result['EVEBIT0']=self.__EV_EBIT(pc,output,cost_result)
        self.__result['EVNOPAT']=self.__EV_NOPAT(pc,output,cost_result)

        for key,value in self.__result.items():
            if value!={}:
                ##########错误值判断
                if value['score'] != 0 and result_legal('nor_mkt'+key,value)==False :
                    value['score']=0
                #########评分调整
                if value['MV_avg']==cost_result['MV_avg'] and value['MV_min']==cost_result['MV_min'] and value['MV_max']==cost_result['MV_max']:
                    value['score']=0.000001


    ###############向外提供参数
    def get_outPut(self):

        self.__output={}

        ##所属行业MVIC/NOPAT.std_MVIC/NOPAT

        idx_indus1=[]
        idx_indus2=[]
        idx_weight=[]
        idx=[]
        # for indus in self.__market_value3.keys():
        #     for v in range(len(self.__market_value3[indus]['EV_NOPAT'])):
        #         if float(self.__market_value3[indus]['EV_NOPAT'][v])>0 and float(self.__market_value3[indus]['EBIT_REV'][v])>0.02 and float(self.__market_value3[indus]['EBIT_REV'][v])<0.5:
        #                 if indus in self.__indus1:
        #                     idx_indus1.append(float(self.__market_value3[indus]['EV_NOPAT'][v]))
        #                     idx_weight.append(self.__p1)
        #                 else:
        #                     idx_indus2.append(float(self.__market_value3[indus]['EV_NOPAT'][v]))
        #                     idx_weight.append(self.__p2)
        #                 idx.append(float(self.__market_value3[indus]['EV_NOPAT'][v]))
        for indus in self.__market_valueA.keys():
            for v in range(len(self.__market_valueA[indus]['EV_NOPAT'])):
                if float(self.__market_valueA[indus]['EV_NOPAT'][v])>0 and float(self.__market_valueA[indus]['EBIT_REV'][v])>0.02 and float(self.__market_valueA[indus]['EBIT_REV'][v])<0.5:
                        if indus in self.__indus1:
                            idx_indus1.append(float(self.__market_valueA[indus]['EV_NOPAT'][v]))
                            idx_weight.append(self.__p1)
                        else:
                            idx_indus2.append(float(self.__market_valueA[indus]['EV_NOPAT'][v]))
                            idx_weight.append(self.__p2)
                        idx.append(float(self.__market_valueA[indus]['EV_NOPAT'][v]))

        if idx_indus1==[] and idx_indus2!=[] :
            avg=np.average(idx_indus2)
        elif idx_indus1!=[] and idx_indus2==[]  :
            avg=np.average(idx_indus1)
        elif idx_indus1!=[] and idx_indus2!=[]:
            avg=np.average(idx_indus1)*self.__p1+np.average(idx_indus2)*self.__p2
        else:
            avg=False

        if avg!=False and len(idx_weight)>1 :
            idx_weight_1=[]
            tt=sum(idx_weight)
            for e in idx_weight:
                idx_weight_1.append(e/tt)

            all=[]
            for e in range(len(idx_weight_1)):
                all.append(len(idx_weight_1)*idx_weight_1[e]*idx[e])
            up=max(all)
            down=min(all)
            self.__output['EV_NOPAT']=round(avg,6)
            self.__output['std_EV_NOPAT']=round(np.std(all),6)
            self.__output['range_std']=round((up-down)/(self.__output['std_EV_NOPAT']*2),6)
        else:
            self.__output['EV_NOPAT']=avg
            self.__output['std_EV_NOPAT']=avg
            self.__output['range_std']=avg

        ##全市场MVIC/NOPAT
        try:
            data3 = read_mongo_all("AM_hypothesis", "Mkt_3")["EV_NOPAT"].tolist()
            dataA = read_mongo_all("AM_hypothesis", "Mkt_A")["EV_NOPAT"].tolist()
        except Exception as e:
            logger(2, e)
        all_mkt=[]
        for e in data3:
            if float(e)>0 and float(e)<200:
                all_mkt.append(float(e))
        for e in dataA:
            if float(e)>0 and float(e)<200:
                all_mkt.append(float(e))
        if all_mkt==[]:
            self.__output['m_EV_NOPAT']=False
        else:
            self.__output['m_EV_NOPAT']=round(np.average(all_mkt),6)
        return self.__output


    def __PE(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sPE']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['NIM'][count])>0.01 and (float(self.__market_valueA[indus]['PE'][count]) > 0 or float(self.__market_valueA[indus]['PE'][count])< 0):
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['PE'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['NIM'][count])>0.01 and (float(self.__market_value3[indus]['PE'][count]) > 0 or float(self.__market_value3[indus]['PE'][count])< 0):
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['PE'][count])*suojian)

            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)
                # temp=0
                # for e in range(len(wi_pe_1)):
                #     temp+=wi_pe_1[e]*PE[e]

                avg=np.average(idx,weights=weight_idx_1)



                all=[]
                for e in range(len(weight_idx_1)):
                    all.append(idx[e]*len(weight_idx_1)*weight_idx_1[e])
                [up_semi,down_semi]=semi_std(all,avg)

                ans['idx_avg']=round(avg,6)
                ans['idx_max']=round(avg+up_semi,6)
                ans['idx_min']=round(avg-down_semi,6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all),6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round(ans['idx_avg']*output['NI'][0]*self.__DLOL,2),0)
                ans['MV_max']=max(round(ans['idx_max']*output['NI'][0]*self.__DLOL,2),0)
                ans['MV_min']=max(round(ans['idx_min']*output['NI'][0]*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])

                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return ans

   

    def __PEp(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sPEp']:
             ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['NIM'][count])>0.01 and (float(self.__market_valueA[indus]['PE_p'][count]) > 0 or float(self.__market_valueA[indus]['PE_p'][count])< 0):
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:
                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['PE_p'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['NIM'][count])>0.01 and (float(self.__market_value3[indus]['PE_p'][count]) > 0 or float(self.__market_value3[indus]['PE_p'][count])< 0):
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['PE_p'][count])*suojian)
            if len(weight_idx) < 3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all)*pc['pc_pep'],6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round(ans['idx_avg']*output['NI'][0]*self.__DLOL,2),0)
                ans['MV_max']=max(round(ans['idx_max']*output['NI'][0]*self.__DLOL,2),0)
                ans['MV_min']=max(round(ans['idx_min']*output['NI'][0]*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return  ans
    def __PB(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sPB']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['D_A'][count])<0.7 and (float(self.__market_valueA[indus]['PB'][count]) > 0 or float(self.__market_valueA[indus]['PB'][count])< 0):
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['PB'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['D_A'][count])<0.7 and (float(self.__market_value3[indus]['PB'][count]) > 0 or float(self.__market_value3[indus]['PB'][count])< 0):
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['PB'][count])*suojian)

            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)

                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all),6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(ans['idx_avg']*output['B'][0]*self.__DLOL,0)
                ans['MV_max']=max(ans['idx_max']*output['B'][0]*self.__DLOL,0)
                ans['MV_min']=max(ans['idx_min']*output['B'][0]*self.__DLOL,0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return ans

    def __PBp(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sPBp']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['D_A'][count])<0.7 and (float(self.__market_valueA[indus]['PB_p'][count]) > 0 or float(self.__market_valueA[indus]['PB_p'][count])< 0):
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['PB_p'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['D_A'][count])<0.7 and (float(self.__market_value3[indus]['PB_p'][count]) > 0 or float(self.__market_value3[indus]['PB_p'][count])< 0):
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['PB_p'][count])*suojian)

            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all)*pc['pc_pbp'],6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round(ans['idx_avg']*output['B'][0]*self.__DLOL,2),0)
                ans['MV_max']=max(round(ans['idx_max']*output['B'][0]*self.__DLOL,2),0)
                ans['MV_min']=max(round(ans['idx_min']*output['B'][0]*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return  ans

    def __EV_S(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sEV_S']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['EV_SALE'][count]) > 0 or float(self.__market_valueA[indus]['EV_SALE'][count])< 0:
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['EV_SALE'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['EV_SALE'][count]) > 0 or float(self.__market_value3[indus]['EV_SALE'][count])< 0:
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['EV_SALE'][count])*suojian)


            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)
                # temp=0
                # for e in range(len(wi_pe_1)):
                #     temp+=wi_pe_1[e]*PE[e]

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all),6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round((ans['idx_avg']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_max']=max(round((ans['idx_max']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_min']=max(round((ans['idx_min']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return ans
    def __EV_Sp(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sEV_Sp']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if float(self.__market_valueA[indus]['EV_SALE_p'][count]) > 0 or float(self.__market_valueA[indus]['EV_SALE_p'][count])< 0:
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['EV_SALE_p'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #         if float(self.__market_value3[indus]['EV_SALE_p'][count]) > 0 or float(self.__market_value3[indus]['EV_SALE_p'][count])< 0:
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['EV_SALE_p'][count])*suojian)


            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)
                # temp=0
                # for e in range(len(wi_pe_1)):
                #     temp+=wi_pe_1[e]*PE[e]

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all)*pc['pc_evsp'],6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round((ans['idx_avg']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_max']=max(round((ans['idx_max']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_min']=max(round((ans['idx_min']*output['Rev'][0]-output['L'])*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return ans
    def __EV_EBIT(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sEV_EBIT']:
            ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if (float(self.__market_valueA[indus]['EV_EBIT'][count]) > 0 or float(self.__market_valueA[indus]['EV_EBIT'][count])< 0) and float(self.__market_valueA[indus]['EBIT_REV'][count])>0.02 and float(self.__market_valueA[indus]['EBIT_REV'][count])<0.5 :
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['EV_EBIT'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #        if (float(self.__market_value3[indus]['EV_EBIT'][count]) > 0 or float(self.__market_value3[indus]['EV_EBIT'][count])< 0) and float(self.__market_value3[indus]['EBIT_REV'][count])>0.02 and float(self.__market_value3[indus]['EBIT_REV'][count])<0.5 :
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['EV_EBIT'][count])*suojian)


            if len(weight_idx)<3:
                return ans
            # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)
                # temp=0
                # for e in range(len(wi_pe_1)):
                #     temp+=wi_pe_1[e]*PE[e]

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all),6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round((ans['idx_avg']*output['EBIT'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_max']=max(round((ans['idx_max']*output['EBIT'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_min']=max(round((ans['idx_min']*output['EBIT'][0]-output['L'])*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)
        return ans
    def __EV_NOPAT(self,pc,output,cost_result):
        ans={}
        idx=[]
        weight_idx=[]
        if output['sEV_NOPAT']:
                        ################A
            for indus in self.__market_valueA.keys():
                suojian=pc['pc_A']
                for count in range(len(self.__weightA[indus])):
                    if (float(self.__market_valueA[indus]['EV_NOPAT'][count]) > 0 or float(self.__market_valueA[indus]['EV_NOPAT'][count])< 0) and float(self.__market_valueA[indus]['EBIT_REV'][count])>0.02 and float(self.__market_valueA[indus]['EBIT_REV'][count])<0.5 :
                        if indus in self.__indus1:

                            weight_idx.append(self.__weightA[indus][count]*self.__p1)
                        else:

                            weight_idx.append(self.__weightA[indus][count]*self.__p2)

                        idx.append(float(self.__market_valueA[indus]['EV_NOPAT'][count])*suojian)
            ###############3
            # for indus in self.__market_value3.keys():
            #     suojian=pc['pc_3']
            #     for count in range(len(self.__market_value3[indus]['PE'])):
            #        if (float(self.__market_value3[indus]['EV_NOPAT'][count]) > 0 or float(self.__market_value3[indus]['EV_NOPAT'][count])< 0) and float(self.__market_value3[indus]['EBIT_REV'][count])>0.02 and float(self.__market_value3[indus]['EBIT_REV'][count])<0.5 :
            #             if indus in self.__indus1:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p1)
            #             else:
            #
            #                 weight_idx.append(self.__weight3[indus][count]*self.__p2)
            #
            #             idx.append(float(self.__market_value3[indus]['EV_NOPAT'][count])*suojian)


            if len(weight_idx) < 3:
                return ans
                # 权重归一化
            if weight_idx!=[]:
                tt=sum(weight_idx)
                weight_idx_1=[]
                for e in weight_idx:
                    weight_idx_1.append(e/tt)
                # temp=0
                # for e in range(len(wi_pe_1)):
                #     temp+=wi_pe_1[e]*PE[e]

                avg=np.average(idx,weights=weight_idx_1)

                all = []
                for e in range(len(weight_idx_1)):
                    all.append(idx[e] * len(weight_idx_1) * weight_idx_1[e])
                [up_semi, down_semi] = semi_std(all, avg)

                ans['idx_avg'] = round(avg, 6)
                ans['idx_max'] = round(avg + up_semi, 6)
                ans['idx_min'] = round(avg - down_semi, 6)
                if np.std(all)!=0:
                    ans['score']=round(np.average(all)/np.std(all),6)
                else:
                    ans['score']=0
                ans['MV_avg']=max(round((ans['idx_avg']*output['NOPAT'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_max']=max(round((ans['idx_max']*output['NOPAT'][0]-output['L'])*self.__DLOL,2),0)
                ans['MV_min']=max(round((ans['idx_min']*output['NOPAT'][0]-output['L'])*self.__DLOL,2),0)
                [ans['MV_max'],ans['MV_avg'],ans['MV_min']]=bp(ans['MV_max'],ans['MV_avg'],ans['MV_min'],cost_result['MV_max'],cost_result['MV_avg'],cost_result['MV_min'])
                ans['p_avg']=round(ans['MV_avg']/output['SC'],2)
                ans['p_min']=round(ans['MV_min']/output['SC'],2)
                ans['p_max']=round(ans['MV_max']/output['SC'],2)

        return ans


    def get_result(self):

        return self.__result, self.peer_list

# pc_A=0.8  ##需要允许自设
# pc_3=0.9  ##需要允许自设
# pc_pbp=0.9  ##需要允许自设
# pc_pep=0.9    ##需要允许自设
# pc_evsp=0.9   ##需要允许自设
# indus_code={'401020':0.7,'151010':0.3}
# new_code={'401010':0.7,'151010':0.3}
# pc={'pc_A':pc_A,'pc_3':pc_3,'pc_pbp':pc_pbp,'pc_pep':pc_pep,'pc_evsp':pc_evsp}
# m=Market_Mtd()
# m.compute([],pc,indus_code,new_code,None,None)

