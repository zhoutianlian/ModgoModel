# -*- coding: utf-8 -*-：
from Data.Conn import connect_mysql_valuation
from Config.mongodb import read_mongo_limit
from Tool.functions.errorinfo import wirte_error
from Tool.functions.semi_std import semi_std
import numpy as np
import datetime

from Report.Log import logger


class MktMethodFin():
    def get_result(self,bookvalue,indus_code,pc,sc,code_list):

        ##判断行业分组
        self.__indus1 = []
        self.__indus2 = []
        self.__code = {}
        self.__p1 = 0
        self.__p2 = 0
        self.__DLOL = 1
        count = 0
        for key, value in indus_code.items():
            if count == 0:
                self.__indus1.append(key)
                self.__code[key] = code_list[0]
                self.__p1 = value
            else:
                self.__indus2.append(key)
                self.__code[key] = code_list[1]
                self.__p2 = value
            count += 1

        ############行业分组判断结束
        db = connect_mysql_valuation()
        cursor = db.cursor()
        try:
            market_value_A = {}
            # market_value_3 = {}

            ##############################################A股市场行情_A############
            for key in indus_code.keys():
                market_value_A[key] = {}

                ########日更数据
                data = read_mongo_limit("AM_hypothesis", "Mkt_A", {"StockCode": {"$in": self.__code[key]}}, {"_id": 0})
                name1 = ['PB', 'PB_p']
                for e in name1:
                    market_value_A[key][e] = data[e].tolist()

                ########季更数据
                data = read_mongo_limit("AM_hypothesis", "Mkt_AA", {"StockCode": {"$in": self.__code[key]}}, {"_id": 0})
                name2 = ['D_A']
                for e in name2:
                    market_value_A[key][e] = data[e].tolist()



            ##############################################三板股市场行情_3############
            # for key in indus_code.keys():
            #     market_value_3[key] = {}
            #
            #     ########日更数据
            #     name1 = ['PB', 'PB_p']
            #     for e in name1:
            #         market_value_3[key][e] = []
            #     sql_3 = "select PB,PB_p   from Mkt_3 where GICS3_code=" + key
            #     cursor.execute(sql_3)
            #     data = list(cursor.fetchall())
            #     for count in range(len(name1)):
            #         for ele in data:
            #             market_value_3[key][name1[count]].append(ele[count])
            #     ########季更数据
            #
            #     ########年更数据
            #     name3 = ['D_A']
            #     for e in name3:
            #         market_value_3[key][e] = []
            #     sql_333 = "select D_A  from Mkt_333 where GICS3_code=" + key
            #     cursor.execute(sql_333)
            #     data = list(cursor.fetchall())
            #     for count in range(len(name3)):
            #         for ele in data:
            #             market_value_3[key][name3[count]].append(ele[count])

        except Exception as e:
            logger(2, e)
            cursor.close()
            db.close()
        cursor.close()
        db.close()
        #######存为内部变量
        # self.__market_value3 = market_value_3
        self.__market_valueA = market_value_A
        #估值
        self.__result={}
        try:
            self.__result['pb'] = self.__PB(pc,bookvalue,sc)
            self.__result['pbp'] = self.__PBp(pc,bookvalue,sc)
            flag = True
            for e in self.__result:
                if e != {}:
                    flag = False
                    break
            if flag:
                self.__result = {}

        except:
            wirte_error((str(datetime.datetime.now())+': error in valuation_models/financial_valuation/market'))

        return self.__result


    def __PBp(self,pc,bookvalue,sc):
        ans={}
        idx=[]

        ################A
        for indus in self.__market_valueA.keys():
            suojian=pc['pc_A']
            for count in range(min(len(self.__market_valueA[indus]['PB_p']), len(self.__market_valueA[indus]['D_A']))):
                if self.__market_valueA[indus]['D_A'][count]!='#DIV/0!' and self.__market_valueA[indus]['PB_p'][count]!='#DIV/0!' and  float(self.__market_valueA[indus]['D_A'][count])<0.7 and float(self.__market_valueA[indus]['PB_p'][count])!=0:

                    idx.append(float(self.__market_valueA[indus]['PB_p'][count])*suojian)
        ###############3
        # for indus in self.__market_value3.keys():
        #     suojian=pc['pc_3']
        #     for count in range(len(self.__market_value3[indus]['PB_p'])):
        #         if self.__market_value3[indus]['D_A'][count]!='#DIV/0!' and self.__market_value3[indus]['PB_p'][count]!='#DIV/0!'and  float(self.__market_value3[indus]['D_A'][count])<0.7 and float(self.__market_value3[indus]['PB_p'][count])!=0:
        #
        #             idx.append(float(self.__market_value3[indus]['PB_p'][count])*suojian)

        if idx!=[]:

            avg=np.average(idx)
            [up_semi, down_semi] = semi_std(idx, avg)

            ans['idx_avg'] = round(avg, 6).item()
            ans['idx_max'] = round(avg + up_semi, 6).item()
            ans['idx_min'] = round(avg - down_semi, 6).item()
            if np.std(idx)!=0:
                ans['score']=round(np.average(idx)/np.std(idx)*pc['pc_pbp'],6).item()
            else:
                ans['score']=0
            ans['MV_avg']=max(round(ans['idx_avg']*bookvalue*self.__DLOL,2),0)
            ans['MV_max']=max(round(ans['idx_max']*bookvalue*self.__DLOL,2),0)
            ans['MV_min']=max(round(ans['idx_min']*bookvalue*self.__DLOL,2),0)
            ans['p_avg']=round(ans['MV_avg']/sc,2)
            ans['p_min']=round(ans['MV_min']/sc,2)
            ans['p_max']=round(ans['MV_max']/sc,2)
        return ans
    def __PB(self,pc,bookvalue,sc):
        ans={}
        idx=[]

        ################A
        for indus in self.__market_valueA.keys():
            suojian=pc['pc_A']
            for count in range(min(len(self.__market_valueA[indus]['PB']), len(self.__market_valueA[indus]['D_A']))):
                if self.__market_valueA[indus]['D_A'][count]!='#DIV/0!' and self.__market_valueA[indus]['PB'][count]!='#DIV/0!' and  float(self.__market_valueA[indus]['D_A'][count])<0.7 and float(self.__market_valueA[indus]['PB'][count])!=0:

                    idx.append(float(self.__market_valueA[indus]['PB'][count])*suojian)
        ###############3
        # for indus in self.__market_value3.keys():
        #     suojian=pc['pc_3']
        #     for count in range(len(self.__market_value3[indus]['PB'])):
        #         if self.__market_value3[indus]['D_A'][count]!='#DIV/0!' and self.__market_value3[indus]['PB'][count]!='#DIV/0!'and  float(self.__market_value3[indus]['D_A'][count])<0.7 and float(self.__market_value3[indus]['PB'][count])!=0:
        #
        #             idx.append(float(self.__market_value3[indus]['PB'][count])*suojian)

        if idx!=[]:

            avg=np.average(idx)
            [up_semi, down_semi] = semi_std(idx, avg)

            ans['idx_avg'] = round(avg, 6)
            ans['idx_max'] = round(avg + up_semi, 6)
            ans['idx_min'] = round(avg - down_semi, 6)
            if np.std(idx)!=0:
                ans['score']=round(np.average(idx)/np.std(idx),6)
            else:
                ans['score']=0
            ans['MV_avg']=max(round(ans['idx_avg']*bookvalue*self.__DLOL,2),0)
            ans['MV_max']=max(round(ans['idx_max']*bookvalue*self.__DLOL,2),0)
            ans['MV_min']=max(round(ans['idx_min']*bookvalue*self.__DLOL,2),0)
            ans['p_avg']=round(ans['MV_avg']/sc,2)
            ans['p_min']=round(ans['MV_min']/sc,2)
            ans['p_max']=round(ans['MV_max']/sc,2)
        return  ans



