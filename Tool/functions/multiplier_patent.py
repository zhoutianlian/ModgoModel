# -*- coding: utf-8 -*-
from Data.Conn import connect_mysql_rdt_fintech
from Config.mongodb import read_mongo_limit
from Report.Log import logger


# 在mysql里面获取公司id（CID）

def get_company_id(vid):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    sql_id = "select enterprise_id from t_valuating_record where id = %s"
    try:
        cursor.execute(sql_id, [vid])
        [company_id] = list(cursor.fetchall())[0]
    except Exception as e:
        logger(2, e)
        cursor.close()
        db.close()
    cursor.close()
    db.close()
    try:
        company_id = int(company_id)
    except:
        pass
    return company_id


# 获取企业名称
def get_enterpriseName(company_id):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    sql_name = 'select enterprise_name from t_enterprise_info where id = %s'
    try:
        cursor.execute(sql_name, [company_id])
    except Exception as e:
        logger(2, e)
        cursor.close()
        db.close()

    [enterprise_name] = list(cursor.fetchall())[0]

    cursor.close()
    db.close()
    return enterprise_name


# 通过公司名称在mongoDB中获得发明专利个数
def get_patent(enterprise_name):
    pa = read_mongo_limit("tyc_data", "Patent", {'enterpriseName': enterprise_name, 'patentType': '发明专利'},
                          {'_id': 0, 'patentType': 1}).count()
    if len(pa) == 0:
        pa = 0
    else:
        pa = pa[0].item()
    return pa


# 用发明专利数给公司价值一个乘数multiplier
def multiplier_patent(pa):
    patent_index = pa / 10
    patent_index = min(patent_index, 1)
    patent_index = patent_index / 10
    multi_patent = patent_index + 1
    return multi_patent


# 综合以上所有输入和输出，函数的输入变为vid，输出为调整后的估值
# 在导出的结论的字典中修正估值
def adjust_result_dict(vid, result_dict):
    keys_to_adjust = ["MV_min", "MV_avg", "MV_max", "p_min", "p_avg", "p_max"]
    company_id = get_company_id(vid)
    if not isinstance(company_id, int):
        multiplier = 1.0
        return result_dict, multiplier
    else:
        multiplier = multiplier_patent(get_patent(company_id))
        for i in keys_to_adjust:
            result_dict[i] = result_dict[i] * multiplier
        return result_dict, multiplier

