# -*- coding: utf-8 -*-
from Data.Conn import connect_mysql_rdt_fintech
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


# 通过公司ID在mysql中获得新闻条数（number of news)
def get_news(company_id):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    sql_id = "select count(*) from t_company_moment_info where enterprise_id = %s"
    try:
        cursor.execute(sql_id, [int(company_id)])
        [pieces_of_news] = list(cursor.fetchall())[0]
    except Exception as e:
        logger(2, e)
        cursor.close()
        db.close()
        pieces_of_news = 0

    cursor.close()
    db.close()
    return pieces_of_news


# 用过新闻条数给公司价值一个乘数multiplier
def multiplier_news(pieces):
    news_index = pieces / 100
    news_index = min(news_index, 1)
    news_index = news_index / 10
    multi_news = news_index + 1
    return multi_news


# 综合以上所有输入和输出，函数的输入变为vid，输出为调整后的估值
# 在导出的结论的字典中修正估值
def adjust_result_dict(vid, result_dict):
    keys_to_adjust = ["MV_min", "MV_avg", "MV_max", "p_min", "p_avg", "p_max"]
    company_id = get_company_id(vid)
    if not isinstance(company_id, int):
        multiplier = 1.0
        return result_dict, multiplier
    else:
        multiplier = multiplier_news(get_news(company_id))
        for i in keys_to_adjust:
            result_dict[i] = result_dict[i] * multiplier
        return result_dict, multiplier


