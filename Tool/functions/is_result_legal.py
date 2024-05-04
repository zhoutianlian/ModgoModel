# -*- coding: utf-8 -*-：
# ZXW
# 判断得到的结果是否有效，如无效则在infor中记录
# 使用需要传入结果所用方法名称（str）
# 结果数据结构为dict，至少含以下key值，其 value 类型为 float：{'MV_min','MV_max','MV_avg'}
import os
import datetime
import numpy as np

from Config.global_V import GlobalValue


def result_legal(name,result):
    ans = True
    value_list = list(result.values())
    if result['MV_min'] <= 0 or result['MV_min'] > result['MV_avg'] or \
            result['MV_avg'] > result['MV_max'] or result['MV_max']>GlobalValue.MV_CILLING or np.nan in value_list:
        ans = False
        path=os.path.abspath(os.path.join(os.getcwd(), "..")) + '/Log'
        if os.path.exists(path):
            path=path+'/log.txt'
            if os.path.exists(path):
                f = open(path, 'a')
                f.write(str(datetime.datetime.now()) + ':  the result of '+ name +' is illegal \n' )
                f.close()
            else:
                f = open(path, 'w')
                f.write(str(datetime.datetime.now()) + ':  the result of ' + name + ' is illegal \n')
                f.close()

        else:
            os.makedirs(path)
            path=path+'/log.txt'
            f = open(path, 'w')
            f.write(str(datetime.datetime.now()) + ':  the result of ' + name + ' is illegal \n')
            f.close()

    return ans


def result_legal_minus(name,result):
    ans = True
    if result['MV_min'] > result['MV_avg'] or \
            result['MV_avg'] > result['MV_max'] or result['MV_max']>GlobalValue.MV_CILLING:
        ans = False
        path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/Log'
        if os.path.exists(path):
            path=path+'/log.txt'
            if os.path.exists(path):
                f = open(path, 'a')
                f.write(str(datetime.datetime.now()) + ':  the result of '+ name +' is illegal_minus \n' )
                f.close()
            else:
                f = open(path, 'w')
                f.write(str(datetime.datetime.now()) + ':  the result of ' + name + ' is illegal_minus \n')
                f.close()

        else:
            os.makedirs(path)
            path=path+'/log.txt'
            f = open(path, 'w')
            f.write(str(datetime.datetime.now()) + ':  the result of ' + name + ' is illegal_minus \n')
            f.close()


    return ans