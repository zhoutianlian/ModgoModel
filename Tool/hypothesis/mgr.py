# -*- coding: utf-8 -*-：
import os
from keras import models
from math import exp

from Config.mongodb import read_mongo_limit
from Report.Log import logger
from Tool.functions import indus_code_forA as indc


def get_MGR(inputs):
    demo = []
    indus_code = inputs["Indus_code"]
    MGR = 0
    indus_code = indc.retrack_Ainsudcode("optimal_debt_to_investcapital", indus_code)
    for indus, coef in indus_code.items():
        rev = inputs["Rev"][0]
        try:
            df = read_mongo_limit("AM_hypothesis", "industry_growth_rate", {'indus': indus}, {'_id': 0})
            target = (rev - float(df["mean"].values[0])) / float(df["std"].values[0])
            if target < 0:
                target = exp(target) - 1
            demo.append(target)
            current_path = os.path.dirname(__file__)
            lm = current_path + '/gr_models/' + indus + '_DN.h5'
            a = models.load_model(lm)
            gr = a.predict(demo)[0][0] * coef
            MGR += gr
        except Exception as e:
            logger(2, e)
    return MGR



# a = {"Indus_code": {"101010": 0.7, "101020": 0.3}, "Rev": [0, 0, 1000000]}
# get_MGR(a)
    # sql = "SELECT indus_gr_decision_tree from indus_gr_decision_tree where gics_code_third=%s ORDER by predict_date desc limit 3"
    # db = connect_mysql_from_mongodb()
    # cursor = db.cursor()
    # try:
    #     indus_GR = {}
    #     for e in indus_code.keys():
    #         cursor.execute(sql, e)
    #         a = cursor.fetchall()
    #         indus_GR[e] = a[0] + a[1] + a[2]
    #     cursor.close()
    #     db.close()
    # except Exception as e:
    #     logger(e)
    #     cursor.close()
    #     db.close()
    #
    # count =0
    # # #对每个行业进行操作
    #
    # current_path = os.path.dirname(__file__)
    # lm=grabTree(current_path+'/ml')
    #
    # if type(inputs['Inv'])==list:
    #     inv=inputs['Inv'][-1]
    #     ap=inputs['AP'][-1]
    #     ar=inputs['AR'][-1]
    #     ta=inputs['TA'][-1]
    #     ni=inputs['NI'][-1]
    # else:
    #     inv=inputs['Inv']
    #     ap=inputs['AP']
    #     ar=inputs['AR']
    #     ta=inputs['TA']
    #     ni=inputs['NI']
    # for e,value in indus_GR.items():
    #     X=[[GR[0],GR[1],value[2],value[1],value[0],inv,ap,ar,ta,ni]]
    #     for ele in range(len(X[0])):
    #         X[0][ele]=np.float64(X[0][ele])
    #     if count==0:  #####只有一个行业
    #         MGR=lm.predict(X)[0]*indus_code[e]
    #     else:  ########两个行业
    #         MGR+=lm.predict(X)[0]*indus_code[e]
    #     count+=1
    # return MGR.item()

#get_MGR([0.34,0.45],{'101010':0.7,'151010':0.3})



