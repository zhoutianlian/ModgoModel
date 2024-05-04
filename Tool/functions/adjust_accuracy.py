# -*- coding: utf-8 -*-：
import datetime
import numpy as np
from pandas import DataFrame

from Data.Conn import connect_mysql_rdt_fintech, ConnMysql
from Config.mongodb import read_mongo_limit, update_data_demo
from Tool.functions.read.get_something import get_fin_id, read_df, get_id, get_mini_id
from Report.Log import logger
from Tool.Util import volatility_accuracy, change_data, get_sigma


def adjust_accuracy(vid, val_valid=None):
    """
    调整估值精度
    :param vid: 估值ID
    :return: None
    """
    bal_list, flow_list, indus, hy_id, bm_id, market = get_id(vid)
    from Config.Database import ConnDB as db_config, Database as db, Fields as fd

    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.vr['tb'], [fd.eid, fd.uid, fd.vdate]
        com_data = conn(tb).find_one(where={"id": vid}, select=select)

    extra = 0
    if len(com_data[fd.uid]) > 9:
        # 游客状态
        relation_data = {}
        extra = -0.005
    else:
        with ConnMysql(**db_config.rdt_mysql) as conn:
            tb, select = db.enterprise_user['tb'], db.enterprise_user['select']
            relation_data = conn(tb).find_one(where={fd.eid: com_data[fd.eid], fd.uid: com_data[fd.uid]}, select=select)
    bal_df = read_df("rdt_fintech", "NewBal", bal_list)
    flow_df = read_df("rdt_fintech", "NewFlow", flow_list)
    # 整数部分：财报日期
    bal_df["date"] = str(bal_df["date"].values[0])
    flow_df["date"] = str(flow_df["date"].values[0])
    bal_df["date"] = bal_df["date"].apply(lambda x: datetime.datetime.strptime(str(x), "%Y%m"))
    flow_df["date"] = flow_df["date"].apply(lambda x: datetime.datetime.strptime(str(x), "%Y%m"))
    enddate = bal_df["date"].sort_values(ascending=False)[0]
    integer_part = int(enddate.strftime("%Y")[2:] + enddate.strftime("%m"))

    # 小数部分：引用财报数量
    decimal_count_one = len(bal_list) * 0.01 + len(flow_list) * 0.02
    # 小数部分：最近一年财报数量

    year = datetime.datetime.now().year - 1
    date = datetime.datetime.strptime(str(year), "%Y")
    last_year_bal_df = bal_df[bal_df["date"] > date]  # type: DataFrame
    last_year_flow_df = flow_df[flow_df["date"] > date]
    decimal_count_two = last_year_bal_df.count(axis=0)[0] * 0.1 + last_year_flow_df.count(axis=0)[0] * 0.2
    # 小数部分：财务科目数量
    if "_class" in bal_df:
        bal_df.drop(["_class", "gaap", "sys", "date", "_id", "fx"], axis=1, inplace=True)
        flow_df.drop(["_class", "date", "start", "_id", "gaap", "sys", "fx"], axis=1,
                     inplace=True)
    else:
        bal_df.drop(["gaap", "sys", "date", "_id", "fx"], axis=1, inplace=True)
        flow_df.drop(["date", "start", "_id", "gaap", "sys", "fx"], axis=1,
                     inplace=True)
    decimal_count_three = np.mean([bal_df.count(axis=1).values[0], flow_df.count(axis=1).values[0]]) * 0.001
    # 小数部分：合格的估值方法数量
    try:
        data = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": vid}, {"_id": 0})
        data = data.to_dict("record")[0]
        score_list = data["val"]["detail"].values()
        num = 0
        if score_list:
            for i in score_list:
                if "score" in i:
                    if i["score"] > 5:
                        num += 1
            decimal_count_four = num * 0.01
        else:
            decimal_count_four = 0

        # 小数部分：综合估值评分
            # sql_summary = "select generalresult_score from t_general_final_result where valuation_id=%s"
            # cursor.execute(sql_summary, [vid])
            # score_summary = cursor.fetchall()[0][0]
        if "score" in data["val"]:
            score_summary = data["val"]["score"]
            decimal_count_five = score_summary * 0.01
        else:
            decimal_count_five = 0

        # 小数部分：估值日期， 精确到分钟
        date_record = com_data["c_time"]
        decimal_count_six = int(str(date_record.year)[2:]) * 0.01 + date_record.month * 0.001 \
                            + date_record.day * 0.00001 + date_record.hour * 0.000001 + date_record.minute * 0.0000001
    except Exception as e:
        decimal_count_four = 0
        decimal_count_five = 0
        decimal_count_six = 0
        logger(2, e)

    decimal_part = (decimal_count_one + decimal_count_two + decimal_count_three + decimal_count_four
                   + decimal_count_five + decimal_count_six)

    decimal_part = min(decimal_part, 0.9999999)

    accuracy = integer_part + decimal_part + extra
    if type(accuracy) is np.float64:
        accuracy = accuracy.item()
    accuracy = round(accuracy, 7)

    legal = False
    # 法人，加0.5
    if relation_data:
        if relation_data[fd.mType] == 2 and relation_data[fd.mStatus] == 0:
            accuracy += 0.6
            legal = True
    try:
        if val_valid == 1:
            valid = 1
            failure = 0
        elif val_valid == 0:
            valid = 0
            failure = 0
        else:

            db = connect_mysql_rdt_fintech()
            cursor = db.cursor()
            # 自然周为时间范围
            val_date_now = com_data[fd.vdate]
            val_date = datetime.datetime.strptime(datetime.datetime.strftime(val_date_now, "%Y-%m-%d"), "%Y-%m-%d")
            week_day = val_date.isoweekday()
            day_before = val_date - datetime.timedelta(days=week_day - 1)
            # day_after = val_date + datetime.timedelta(days=8 - week_day)
            count = 1
            score = 0

            res_now = data["val"]["syn"][1]
            sql = "SELECT enterprise_name from t_enterprise_info where id=%s"
            cursor.execute(sql, [com_data[fd.eid]])
            name = list(cursor.fetchall())[0][0]
            data_company = read_mongo_limit("tyc_data", "TycEnterpriseInfo", {"name": name},
                                            {"regCapital": 1, "estiblishTime": 1})

            date_before, res_before = change_data(data_company)

            # val_date_now = datetime.datetime.strptime("20200410", "%Y%m%d")
            # val_date_now = datetime.datetime.now()
            year = (val_date_now - date_before).days / 365

            year_before = val_date_now + datetime.timedelta(days=-365)

            # 读取最近一年所有估值
            sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and user_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by c_time desc limit 1"
            # sql = "SELECT id, c_time from t_valuating_record where enterprise_id=%s and user_id=%s and c_time<%s and c_time>%s and val_valid=1 and val_terminal!=6 order by c_time"

            cursor.execute(sql, [com_data[fd.eid], com_data[fd.uid], val_date_now])
            find = list(cursor.fetchall())

            if find:
                # 记录小于三条或成立时间小于两年

                # if len(find) < 3 or year < 2:
                #     # 补充考虑注册资本
                #     s = get_sigma(year, res_before)
                #     score += volatility_accuracy(res_before, res_now, year, s)
                #
                # for i in find:
                #     old_id, val_type, c_time = i
                #     data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                #     data_old = data_old.to_dict("record")[0]
                #     res_before = data_old["val"]["syn"][1]
                #     year = (val_date_now - date_before).days / 365
                #     s = get_sigma(year, res_before)
                #     score += volatility_accuracy(res_before, res_now, year, s)
                #     data_old[""]

                # score += volatility_accuracy(res_before, res_now, year, s)
                s = get_sigma(year, res_before)
                old_id, val_type = find[0]
                if val_type == 5:
                    query = {"flowId": 1, "_id": 0}
                    tb = "NewFlow"
                else:
                    query = {"balId": 1, "_id": 0}
                    tb = "NewBal"
                bal_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": bal_id}}, {"date": 1, "_id": 0})["date"]
                date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                data_old = data_old.to_dict("record")[0]
                res_before = data_old["val"]["syn"][1]
                year = (val_date_now - date_before).days / 365
                if year > 0:
                    # s = get_sigma(year, res_before)
                    score += volatility_accuracy(res_before, res_now, year, s)
                    count += 1

                sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6  and user_id=(select user_id from t_enterprise_manage_relation where enterprise_id=%s and manage_type=2 and manage_status=0) order by c_time desc limit 1 "

                cursor.execute(sql, [com_data[fd.eid], val_date_now, com_data[fd.eid]])
                find = list(cursor.fetchall())
                if find:
                    old_id, val_type = find[0]
                    if val_type == 5:
                        query = {"flowId": 1, "_id": 0}
                        tb = "NewFlow"
                    else:
                        query = {"balId": 1, "_id": 0}
                        tb = "NewBal"
                    bal_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                    end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": bal_id}}, {"date": 1, "_id": 0})["date"]
                    date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                    data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                    data_old = data_old.to_dict("record")[0]
                    res_before = data_old["val"]["syn"][1]
                    year = (val_date_now - date_before).days / 365
                    if year > 0:
                        # s = get_sigma(year, res_before)
                        score += volatility_accuracy(res_before, res_now, year, s)
                        count += 1

            else:
                # res_before *= 2.5
                s = get_sigma(year, res_before)
                # res_now = 300000000
                score += volatility_accuracy(res_before, res_now, year, s)

            volatility = (score / count) >= 2
            # if -1.65 < score < 1.65:
            if volatility:
                sql = "SELECT val_accuracy from t_valuating_record where enterprise_id=%s and c_time>%s and c_time<%s and val_valid=1 and val_terminal!=6 order by val_accuracy desc limit 1"
                cursor.execute(sql, [com_data[fd.eid], day_before, val_date_now])
                find = list(cursor.fetchall())
                if find:
                    if legal:
                        valid = 1
                        failure = 0
                    else:
                        val_accuracy = find[0][0]
                        if accuracy >= val_accuracy:
                            valid = 1
                            failure = 0
                        else:
                            valid = 0
                            failure = 0
                else:
                    valid = 1
                    failure = 0
            else:
                valid = 0
                failure = 0

        sql_update = 'Update t_valuating_record set val_accuracy=%s,val_valid=%s,valuation_failure=%s where id=%s'
        sql_value = [accuracy, valid, failure, vid]
        cursor.execute(sql_update, sql_value)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        cursor.close()
        db.close()
        logger(2, e)
    save_accuracy(vid, accuracy)


def adjust_accuracy_fin(vid):
    """
    调整财报精度
    :param vid: 估值ID
    :return: None
    """
    bal_list, indus = get_fin_id(vid)
    from Config.Database import ConnDB as db_config, Database as db, Fields as fd

    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.vr['tb'], [fd.eid, fd.uid, fd.vdate]
        com_data = conn(tb).find_one(where={"id": vid}, select=select)

    extra = 0
    if len(com_data[fd.uid]) > 9:
        # 游客状态
        relation_data = {}
        extra = -0.005
    else:
        with ConnMysql(**db_config.rdt_mysql) as conn:
            tb, select = db.enterprise_user['tb'], db.enterprise_user['select']
            relation_data = conn(tb).find_one(where={fd.eid: com_data[fd.eid], fd.uid: com_data[fd.uid]}, select=select)
    bal_df = read_df("rdt_fintech", "NewBal", bal_list)
    # 整数部分：财报日期
    bal_df["date"] = str(bal_df["date"].values[0])
    bal_df["date"] = bal_df["date"].apply(lambda x: datetime.datetime.strptime(x, "%Y%m"))
    enddate = bal_df["date"].sort_values(ascending=False)[0]
    integer_part = int(enddate.strftime("%Y")[2:] + enddate.strftime("%m"))

    # 小数部分：引用财报数量
    decimal_count_one = len(bal_list) * 0.01
    # 小数部分：最近一年财报数量
    year = datetime.datetime.now().year - 1
    date = datetime.datetime.strptime(str(year), "%Y")
    last_year_bal_df = bal_df[bal_df["date"] > date]  # type: DataFrame
    decimal_count_two = last_year_bal_df.count(axis=0)[0] * 0.1
    # 小数部分：财务科目数量
    bal_df.drop(["_class", "gaap", "sys", "date", "_id", "fx"], axis=1, inplace=True)

    decimal_count_three = bal_df.count(axis=1).values[0] * 0.001
    # 小数部分：合格的估值方法数量
    try:
        data = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": vid}, {"ipo_prospect": 0})
        data = data.to_dict("record")[0]
        score_list = data["val"]["detail"].values()
        num = 0
        if score_list:
            for i in score_list:
                if "score" in i:
                    if i["score"] > 5:
                        num += 1
            decimal_count_four = num * 0.01
        else:
            decimal_count_four = 0

        # 小数部分：综合估值评分
            # sql_summary = "select generalresult_score from t_general_final_result where valuation_id=%s"
            # cursor.execute(sql_summary, [vid])
            # score_summary = cursor.fetchall()[0][0]
        score_summary = data["val"]["score"]
        decimal_count_five = score_summary * 0.01

        # 小数部分：估值日期， 精确到分钟
        date_record = com_data["c_time"]
        decimal_count_six = int(str(date_record.year)[2:]) * 0.01 + date_record.month * 0.001 \
                            + date_record.day * 0.00001 + date_record.hour * 0.000001 + date_record.minute * 0.0000001
    except Exception as e:
        decimal_count_four = 0
        decimal_count_five = 0
        decimal_count_six = 0
        logger(2, e)
    decimal_part = (decimal_count_one + decimal_count_two + decimal_count_three + decimal_count_four
                   + decimal_count_five + decimal_count_six)

    decimal_part = min(decimal_part, 0.9999999)

    accuracy = integer_part + decimal_part + extra
    if type(accuracy) is np.float64:
        accuracy = accuracy.item()
    accuracy = round(accuracy, 7)
    legal = False
    # 法人，加0.5
    if relation_data:
        if relation_data[fd.mType] == 2 and relation_data[fd.mStatus] == 0:
            accuracy += 0.5
            legal = True
    try:
        db = connect_mysql_rdt_fintech()
        cursor = db.cursor()
        # 自然周为时间范围
        val_date_now = com_data[fd.vdate]
        val_date = datetime.datetime.strptime(datetime.datetime.strftime(val_date_now, "%Y-%m-%d"), "%Y-%m-%d")
        week_day = val_date.isoweekday()
        day_before = val_date - datetime.timedelta(days=week_day - 1)
        # day_after = val_date + datetime.timedelta(days=8 - week_day)
        count = 1
        score = 0
        res_now = data["val"]["syn"][1]
        sql = "SELECT enterprise_name from t_enterprise_info where id=%s"
        cursor.execute(sql, [com_data[fd.eid]])
        name = list(cursor.fetchall())[0][0]
        data_company = read_mongo_limit("tyc_data", "TycEnterpriseInfo", {"name": name},
                                        {"regCapital": 1, "estiblishTime": 1})

        date_before, res_before = change_data(data_company)
        year = (val_date_now - date_before).days / 365

        sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and user_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by c_time desc limit 1"
        cursor.execute(sql, [com_data[fd.eid], com_data[fd.uid], val_date_now])
        find = list(cursor.fetchall())

        if find:
            # 财报时间 跳过自动估值
            s = get_sigma(year, res_before)
            score += volatility_accuracy(res_before, res_now, year, s)

            old_id, val_type = find[0]
            if val_type == 5:
                query = {"flowId": 1, "_id": 0}
                tb = "NewFlow"
            else:
                query = {"balId": 1, "_id": 0}
                tb = "NewBal"
            bal_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
            end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": bal_id}}, {"date": 1, "_id": 0})["date"]
            date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
            data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
            data_old = data_old.to_dict("record")[0]
            res_before = data_old["val"]["syn"][1]
            year = (val_date_now - date_before).days / 365
            if year > 0:
                # s = get_sigma(year, res_before)
                score += volatility_accuracy(res_before, res_now, year, s)
                count += 1

            sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6  and user_id=(select user_id from t_enterprise_manage_relation where enterprise_id=%s and manage_type=2 and manage_status=0) order by c_time desc limit 1 "

            cursor.execute(sql, [com_data[fd.eid], val_date_now, com_data[fd.eid]])
            find = list(cursor.fetchall())
            if find:
                old_id, val_type = find[0]
                if val_type == 5:
                    query = {"flowId": 1, "_id": 0}
                    tb = "NewFlow"
                else:
                    query = {"balId": 1, "_id": 0}
                    tb = "NewBal"
                bal_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": bal_id}}, {"date": 1, "_id": 0})["date"]
                date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                data_old = data_old.to_dict("record")[0]
                res_before = data_old["val"]["syn"][1]
                year = (val_date_now - date_before).days / 365
                if year > 0:
                    # s = get_sigma(year, res_before)
                    score += volatility_accuracy(res_before, res_now, year, s)
                    count += 1

        else:
            res_before *= 2.5
            s = get_sigma(year, res_before)
            score += volatility_accuracy(res_before, res_now, year, s)

        volatility = (score / count) >= 2
        if volatility:
            sql = "SELECT val_accuracy from t_valuating_record where enterprise_id=%s and c_time>%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by val_accuracy desc limit 1"
            cursor.execute(sql, [com_data[fd.eid], day_before, val_date_now])
            find = list(cursor.fetchall())
            if find:
                if legal:
                    valid = 1
                    failure = 0
                else:
                    val_accuracy = find[0][0]
                    if accuracy >= val_accuracy:
                        valid = 1
                        failure = 0
                    else:
                        valid = 0
                        failure = 0
            else:
                valid = 1
                failure = 0
        else:
            valid = 0
            failure = 0

        sql_update = 'Update t_valuating_record set val_accuracy=%s,val_valid=%s,valuation_failure=%s where id=%s'
        sql_value = [accuracy, valid, failure, vid]
        cursor.execute(sql_update, sql_value)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        cursor.close()
        db.close()
        logger(2, e)

    save_accuracy(vid, accuracy)


def adjust_accuracy_mini(vid):
    """
    调整财报精度
    :param vid: 估值ID
    :return: None
    """
    flow_list = get_mini_id(vid)
    from Config.Database import ConnDB as db_config, Database as db, Fields as fd

    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.vr['tb'], [fd.eid, fd.uid, fd.vdate]
        com_data = conn(tb).find_one(where={"id": vid}, select=select)
    extra = 0
    if len(com_data[fd.uid]) > 9:
        # 游客状态
        relation_data = {}
        extra = -0.005
    else:
        with ConnMysql(**db_config.rdt_mysql) as conn:
            tb, select = db.enterprise_user['tb'], db.enterprise_user['select']
            relation_data = conn(tb).find_one(where={fd.eid: com_data[fd.eid], fd.uid: com_data[fd.uid]}, select=select)
    flow_df = read_df("rdt_fintech", "NewFlow", flow_list)
    # 整数部分：财报日期
    # 扣100天
    flow_df["date"] = str(flow_df["date"].values[0])
    flow_df["date"] = flow_df["date"].apply(lambda x: datetime.datetime.strptime(x, "%Y%m"))
    enddate = flow_df["date"].sort_values(ascending=False)[0] - datetime.timedelta(days=100)
    integer_part = int(enddate.strftime("%Y")[2:] + enddate.strftime("%m"))

    # 小数部分：引用财报数量
    decimal_count_one = len(flow_df) * 0.01
    # 小数部分：最近一年财报数量
    year = datetime.datetime.now().year - 1
    date = datetime.datetime.strptime(str(year), "%Y")
    last_year_bal_df = flow_df[flow_df["date"] > date]  # type: DataFrame
    decimal_count_two = last_year_bal_df.count(axis=0)[0] * 0.1
    # 小数部分：财务科目数量
    flow_df.drop(["_class", "gaap", "sys", "date", "_id", "fx"], axis=1, inplace=True)

    decimal_count_three = flow_df.count(axis=1).values[0] * 0.001

    data = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": vid}, {"ipo_prospect": 0})
    data = data.to_dict("record")[0]
    # 小数部分：估值日期， 精确到分钟
    date_record = com_data["c_time"]
    decimal_count_four = int(str(date_record.year)[2:]) * 0.01 + date_record.month * 0.001 \
                            + date_record.day * 0.00001 + date_record.hour * 0.000001 + date_record.minute * 0.0000001

    decimal_part = (decimal_count_one + decimal_count_two + decimal_count_three + decimal_count_four)

    decimal_part = min(decimal_part, 0.9999999)

    accuracy = integer_part + decimal_part + extra
    if type(accuracy) is np.float64:
        accuracy = accuracy.item()
    accuracy = round(accuracy, 7)

    legal = False
    # 法人，加0.5
    if relation_data:
        if relation_data[fd.mType] == 2 and relation_data[fd.mStatus] == 0:
            accuracy += 0.5
            legal = True

    try:
        db = connect_mysql_rdt_fintech()
        cursor = db.cursor()
        # 自然周为时间范围
        val_date_now = com_data[fd.vdate]
        val_date = datetime.datetime.strptime(datetime.datetime.strftime(val_date_now, "%Y-%m-%d"), "%Y-%m-%d")
        week_day = val_date.isoweekday()
        day_before = val_date - datetime.timedelta(days=week_day - 1)
        # day_after = val_date + datetime.timedelta(days=8 - week_day)
        count = 1
        score = 0
        res_now = data["val"]["syn"][1]
        sql = "SELECT enterprise_name from t_enterprise_info where id=%s"
        cursor.execute(sql, [com_data[fd.eid]])
        name = list(cursor.fetchall())[0][0]
        data_company = read_mongo_limit("tyc_data", "TycEnterpriseInfo", {"name": name},
                                        {"regCapital": 1, "estiblishTime": 1})

        date_before, res_before = change_data(data_company)
        year = (val_date_now - date_before).days / 365

        sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and user_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by c_time desc limit 1"
        cursor.execute(sql, [com_data[fd.eid], com_data[fd.uid], val_date_now])
        find = list(cursor.fetchall())

        if find:
            # 财报时间 跳过自动估值
            s = get_sigma(year, res_before)
            # res_now = 300000000
            score += volatility_accuracy(res_before, res_now, year, s)

            old_id, val_type = find[0]
            if val_type == 5:
                query = {"flowId": 1, "_id": 0}
                tb = "NewFlow"
            else:
                query = {"balId": 1, "_id": 0}
                tb = "NewBal"
            try:
                flow_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": flow_id}}, {"date": 1, "_id": 0})["date"]
                date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                data_old = data_old.to_dict("record")[0]
                res_before = data_old["val"]["syn"][1]
                year = (val_date_now - date_before).days / 365
                if year > 0:
                    # s = get_sigma(year, res_before)
                    score += volatility_accuracy(res_before, res_now, year, s)
                    count += 1

                sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6  and user_id=(select user_id from t_enterprise_manage_relation where enterprise_id=%s and manage_type=2 and manage_status=0) order by c_time desc limit 1"

                cursor.execute(sql, [com_data[fd.eid], val_date_now, com_data[fd.eid]])
                find = list(cursor.fetchall())
                if find:
                    old_id, val_type = find[0]
                    if val_type == 5:
                        query = {"flowId": 1, "_id": 0}
                        tb = "NewFlow"
                    else:
                        query = {"balId": 1, "_id": 0}
                        tb = "NewBal"
                    flow_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                    end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": flow_id}}, {"date": 1, "_id": 0})[
                           "date"]
                    date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                    data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                    data_old = data_old.to_dict("record")[0]
                    res_before = data_old["val"]["syn"][1]
                    year = (val_date_now - date_before).days / 365
                    if year > 0:
                        # s = get_sigma(year, res_before)
                        score += volatility_accuracy(res_before, res_now, year, s)
                        count += 1
            except Exception as e:
                logger(2, "mongo查询用户历史估值失败" + str(e))
        else:
            res_before *= 2.5
            s = get_sigma(year, res_before)
            score += volatility_accuracy(res_before, res_now, year, s)

        volatility = (score / count) >= 2
        if volatility:
            sql = "SELECT val_accuracy from t_valuating_record where enterprise_id=%s and c_time>%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by val_accuracy desc limit 1"
            cursor.execute(sql, [com_data[fd.eid], day_before, val_date_now])
            find = list(cursor.fetchall())
            if find:
                if legal:
                    valid = 1
                    failure = 0
                else:
                    val_accuracy = find[0][0]
                    if accuracy >= val_accuracy:
                        valid = 1
                        failure = 0
                    else:
                        valid = 0
                        failure = 0
            else:
                valid = 1
                failure = 0
        else:
            valid = 0
            failure = 0

        sql_update = 'Update t_valuating_record set val_accuracy=%s,val_valid=%s,valuation_failure=%s where id=%s'
        sql_value = [accuracy, valid, failure, vid]
        cursor.execute(sql_update, sql_value)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        cursor.close()
        db.close()
        logger(2, e)
    save_accuracy(vid, accuracy)


def adjust_accuracy_vc(vid):
    from Config.Database import ConnDB as db_config, Database as db, Fields as fd
    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.vr['tb'], [fd.eid, fd.uid, fd.vdate]
        com_data = conn(tb).find_one(where={"id": vid}, select=select)
    data = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": vid}, {"_id": 0})
    data = data.to_dict("record")[0]
    try:
        db = connect_mysql_rdt_fintech()
        cursor = db.cursor()
        val_date_now = com_data[fd.vdate]
        val_date = datetime.datetime.strptime(datetime.datetime.strftime(val_date_now, "%Y-%m-%d"), "%Y-%m-%d")
        week_day = val_date.isoweekday()
        day_before = val_date - datetime.timedelta(days=week_day - 1)
        # day_after = val_date + datetime.timedelta(days=8 - week_day)
        count = 1
        score = 0
        res_now = data["val"]["syn"][1]
        sql = "SELECT enterprise_name from t_enterprise_info where id=%s"
        cursor.execute(sql, [com_data[fd.eid]])
        name = list(cursor.fetchall())[0][0]
        data_company = read_mongo_limit("tyc_data", "TycEnterpriseInfo", {"name": name},
                                        {"regCapital": 1, "estiblishTime": 1})

        date_before, res_before = change_data(data_company)
        if res_before < 0 or res_now < 0:
            valid = 0
            failure = 0
        else:
            year = (val_date_now - date_before).days / 365

            sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and user_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6 order by c_time desc limit 1"
            cursor.execute(sql, [com_data[fd.eid], com_data[fd.uid], val_date_now])
            find = list(cursor.fetchall())

            if find:
                # 财报时间 跳过自动估值
                s = get_sigma(year, res_before)
                # res_now = 300000000
                score += volatility_accuracy(res_before, res_now, year, s)

                old_id, val_type = find[0]
                if val_type == 5:
                    query = {"flowId": 1, "_id": 0}
                    tb = "NewFlow"
                else:
                    query = {"balId": 1, "_id": 0}
                    tb = "NewBal"
                flow_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": flow_id}}, {"date": 1, "_id": 0})["date"]
                date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                data_old = data_old.to_dict("record")[0]
                res_before = data_old["val"]["syn"][1]
                year = (val_date_now - date_before).days / 365
                if year > 0:
                    # s = get_sigma(year, res_before)
                    score += volatility_accuracy(res_before, res_now, year, s)
                    count += 1
                sql = "SELECT id, val_type from t_valuating_record where enterprise_id=%s and c_time<%s and val_valid=1 and val_type!=3 and val_terminal!=6  and user_id=(select user_id from t_enterprise_manage_relation where enterprise_id=%s and manage_type=2 and manage_status=0) order by c_time desc limit 1"

                cursor.execute(sql, [com_data[fd.eid], val_date_now, com_data[fd.eid]])
                find = list(cursor.fetchall())
                if find:
                    old_id, val_type = find[0]
                    if val_type == 5:
                        query = {"flowId": 1, "_id": 0}
                        tb = "NewFlow"
                    else:
                        query = {"balId": 1, "_id": 0}
                        tb = "NewBal"
                    flow_id = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": old_id}, query).values[0][0]
                    end = read_mongo_limit("rdt_fintech", tb, {"_id": {"$in": flow_id}}, {"date": 1, "_id": 0})["date"]
                    date_before = datetime.datetime.strptime(str(max(end)), "%Y%m")
                    data_old = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": old_id}, {"_id": 0})
                    data_old = data_old.to_dict("record")[0]
                    res_before = data_old["val"]["syn"][1]
                    year = (val_date_now - date_before).days / 365
                    if year > 0:
                        # s = get_sigma(year, res_before)
                        score += volatility_accuracy(res_before, res_now, year, s)
                        count += 1

            else:
                res_before *= 2.5
                s = get_sigma(year, res_before)
                score += volatility_accuracy(res_before, res_now, year, s)

            volatility = (score / count) >= 2
            if volatility:
                valid = 1
                failure = 0
            else:
                valid = 0
                failure = 0
        sql_update = 'Update t_valuating_record set val_valid=%s,valuation_failure=%s where id=%s'
        sql_value = [valid, failure, vid]
        cursor.execute(sql_update, sql_value)
        db.commit()
    except Exception as e:
        logger(2, e)
    finally:
        cursor.close()
        db.close()
    # save_accuracy(vid, 0, score)


def save_accuracy(vid, accuracy):
    demo_dict = dict()
    data_res = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": vid}, None)
    data_res.iloc[0]["val"]["accuracy"] = accuracy
    # data_res.iloc[0]["val"]["volatility"] = score
    demo_dict["val"] = data_res.iloc[0]["val"]
    update_data_demo("rdt_fintech", "ValuationResult", {"_id": vid}, {"$set": demo_dict}, 1)


if __name__ == '__main__':
    import Config.Database

    # time1 = datetime.datetime.now()
    Config.Database.set_db('test')

    # data = read_mongo_limit("rdt_fintech", "ValuationResult", {"_id": 1561}, {"ipo_prospect": 0})res_before = 32500000
    #     year = 16
    #     s = get_sigma(year, res_before)
    #     res_now = 3000000000
    #
    #     print(volatility_accuracy(res_before, res_now, year, s))
    # adjust_accuracy_mini(11649)
    adjust_accuracy_vc(13470)
