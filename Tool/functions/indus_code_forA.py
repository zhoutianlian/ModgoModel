# -*- coding: utf-8 -*-：
import copy

from Config.mongodb import read_mongo_all
from Report.Log import logger
# #输入用户原本输入的GICS三级行业，返回A股中含有的GICS三级行业


def retrack_Ainsudcode(collection, indus_code, column: str="gics_code_third"):

    # ########上市公司的三级行业
    df = read_mongo_all("AM_hypothesis", collection)
    total_indus = df[column].values
    new_code=copy.deepcopy(indus_code)
    for key in list(new_code.keys()):
        a=key
        count=1
        flag=0
        while a not in total_indus and count*2<len(a) :
            for ins in total_indus:
                if a[:-2*count]==str(ins)[:-2*count]:
                    a=ins
                    new_code[str(ins)]=new_code.pop(key)  #功能：相当于更改key值
                    flag=1
                    break
            if flag==1:
                break
            count+=1
        if count!=1 and flag==0:
            logger(2, "Wrong in Indus_code_forA_GR in indus_code %s"%a)
            break
    return new_code


