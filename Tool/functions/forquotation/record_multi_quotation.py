from CONFIG.database import connect_mysql_fuyoubank_security
import datetime
from functions.forquotation.get_valuation_rank import get_rank
from functions.is_this_week import isthisweek
from log.log import logger


def record_for_multiquotation(data):
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        #获取公司id信息
        sql_find_companyid='select company_basic_id from parent where id=%s'
        cursor.execute(sql_find_companyid,[data['pid']])
        companyid=cursor.fetchall()[0][0]
        newrank=get_rank(data)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()

    # 如果newrank==False，没必要更新：
    if newrank != False:
        # 通过优先级判断数据库操作类型是insert 还是 update
        sql_find_rank = '''select result_rank,m_time from quotation_company_basic_info s where s.company_id=%s 
                        order by ABS(NOW() - s.m_time) ASC limit 1'''
        try:
            cursor.execute(sql_find_rank, [companyid])
            olddata = list(cursor.fetchall())
        except Exception as e:
            logger(e)
        finally:
            cursor.close()
            db.close()

        if olddata != []:  # 存在旧数据
            [oldrank, olddate] = olddata[0]
            if isthisweek(olddate) == True and oldrank <= newrank:  # 当oldrank==newrank，因为目前时间始终早于过去，所以更新
                update_multi_quotation(data, newrank)

            elif isthisweek(olddate) == False:
                insert_multi_quotation(data, newrank, companyid)

        else:  # 无旧数据
            insert_multi_quotation(data, newrank, companyid)



def update_multi_quotation(data,newrank):
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        sql_update = '''update quotation_company_basic_info set value_per_shareq=%s,
                                total_value=%s,m_time=%s,result_rank=%s'''
        update_date = datetime.datetime.now()
        data_for_update = [data['p_avg'], data['MV_avg'], update_date, newrank]
        cursor.execute(sql_update, data_for_update)
        db.commit()
    except Exception as e:
        logger(e)
    finally:
        cursor.close()
        db.close()


def insert_multi_quotation(data,newrank,companyid):
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        sql_find_company_name_and_financeround = '''select company_name,current_finance_round from 
                            ci_basic_company_info where id=%s'''
        cursor.execute(sql_find_company_name_and_financeround, [companyid])
        [company_name, fround] = cursor.fetchall()[0]
        temp = 0
        gics_code = 0
        for key, value in data['indus'].items():
            if value > temp:
                temp = value
                gics_code = key
        sql_find_indus_name = 'select gics_name from industry_info where id=%s'
        cursor.execute(sql_find_indus_name, [gics_code])
        gics_name = cursor.fetchall()[0][0]
        update_date = datetime.datetime.now()
        sql_insert = '''insert into quotation_company_basic_info(company_id,stock_nameq,finance_roundq,gics_nameq,
                                    total_value,value_per_shareq,
                                    m_time,result_rank) values (%s,%s,%s,%s,%s,%s,%s,%s)'''
        data_for_insert = [companyid, company_name, fround, gics_name, data['MV_avg'], data['p_avg'],
                           update_date, newrank]
        cursor.execute(sql_insert, data_for_insert)
        db.commit()
    except Exception as e:
        logger(e)
    finally:
        cursor.close()
        db.close()

