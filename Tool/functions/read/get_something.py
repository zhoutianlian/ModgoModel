# -*- coding: utf-8 -*-：
import pandas as pd
import numpy as np
import redis

from Config.mongodb import Conn, read_mongo_limit, get_last_update_date, read_mongo_all, get_last_update_data
from Tool.functions.semi_std import semi_std
from Config.para import *
from Tool.functions import indus_code_forA as indc
from Report.Log import logger
from Config.Database import Database as Db
from Config.Database import ConnDB
from Data.Conn import connect_mysql_rdt_fintech


def get_id(vid):
    data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_class": 0})
    bal_list = data["balId"].values[0]
    flow_list = data["flowId"].values[0]
    try:
        hy_id = data["hypoId"].values[0].item()
    except:
        hy_id = data['hypoId'].values[0]
    indus = data["inputIndustry"].to_dict()[0]
    market = data["inputMarket"].values[0].item()
    finance_round = data["inputRound"].values[0].item()
    return bal_list, flow_list, indus, hy_id, market, finance_round


def get_fin_id(vid):
    data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_class": 0})
    bal_list = data["balId"].values[0]
    indus = data["inputIndustry"].to_dict()[0]
    return bal_list, indus


def get_market_id(vid):
    data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_class": 0})
    market = data["inputMarket"].values[0]
    return market


def get_company_name(vid):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    name = None
    try:
        sql = "select enterprise_name from t_enterprise_info where id=(select enterprise_id from t_valuating_record where id=%s)"
        cursor.execute(sql, [vid])
        name = cursor.fetchall()[0][0]
    except Exception as e:
        logger(2, e)
    finally:
        cursor.close()
        db.close()
    return name


def get_company_id(name):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    eid = None
    try:
        sql = "select id from t_enterprise_info where enterprise_name=%s"
        cursor.execute(sql, [name])
        eid = cursor.fetchall()[0][0]
    except Exception as e:
        logger(2, e)
    finally:
        cursor.close()
        db.close()
    return eid


def get_ipo(vid):
    name = get_company_name(vid)
    ipo = read_ipo(name)

    return ipo


def get_mini_id(vid):
    data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_class": 0})
    flow_list = data["flowId"].values[0]
    return flow_list


def get_vc_id(vid):
    data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_class": 0})
    vc_id = data["vcId"].values[0].item()
    indus = data["inputIndustry"].to_dict()[0]
    staff = data["inputStaffNum"].values[0].item()
    fin_round = data["inputRound"].values[0].item()
    return vc_id, indus, staff, fin_round


def get_ins(indus):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    indus_dict = dict()
    code_list = []
    for i in indus:
        demo_list = []
        indus_dict[i[:6]] = indus[i][0]
        format_strings = ",".join(['%s'] * len(indus[i][1]))
        if len(indus[i][1]) > 0:
            if len(indus[i][1]) > 1:
                sql = "select stock_code from t_company_industry_code where id in (%s)" % format_strings
            else:
                sql = "select stock_code from t_company_industry_code where id=%s" % format_strings
            cursor.execute(sql, indus[i][1])
            name_tuple = list(cursor.fetchall())
            for name in name_tuple:
                demo_list.append(name[0])
            code_list.append(demo_list)
    cursor.close()
    db.close()
    return indus_dict, code_list


def get_indus_turnover(indus_code):
    turnover_avg=0
    turnover_max=0
    turnover_min=0
    indus_code = indc.retrack_Ainsudcode("optimal_debt_to_investcapital", indus_code)
    try:
        for key,value in indus_code.items():
            res_df = read_mongo_limit("AM_hypothesis", "Turnover", {"GICS_Code": int(key)}, {"_id": 0})["AssetTurnover"]
            if not res_df.empty:
                temp = np.average(res_df)
                turnover_avg += temp * value
                [up_std, down_std] = semi_std(res_df, temp)
                turnover_max += turnover_avg + up_std * value
                turnover_min += turnover_avg - down_std * value
    except Exception as e:
        logger(2, e)

    return {'max':turnover_max,'avg':turnover_avg,'min':turnover_min}


def get_indus_dtol(indus_code):

    dtol_avg = 0
    # dtol_max = 0
    # dtol_min = 0
    indus_code = indc.retrack_Ainsudcode("optimal_debt_to_investcapital", indus_code)
    try:
        for key, value in indus_code.items():
            res_df = read_mongo_limit("AM_hypothesis", "Turnover", {"GICD_Code": str(key)}, {"_id": 0})
            if not res_df.empty:
                temp = np.average(res_df)
                dtol_avg += temp * value
            # [up_std, down_std] = semi_std(dtol, temp)
            # dtol_max += dtol_avg + up_std * value
            # dtol_min += dtol_avg - down_std * value
    except Exception as e:
        logger(2, e)
    # return {'max': dtol_max, 'avg': dtol_avg, 'min': dtol_min}
    return dtol_avg


def get_hypothesis(indus_code):
    last_date_cs = get_last_update_date("AM_hypothesis", "optimal_debt_to_investcapital")
    last_date_risk = get_last_update_date("AM_hypothesis", "lasted_riskfree_risk")
    cs_df = read_mongo_limit("AM_hypothesis", "optimal_debt_to_investcapital", {"update_date": last_date_cs}, {"_id": 0})
    risk_df = read_mongo_limit("AM_hypothesis", "lasted_riskfree_risk", {"update_date": last_date_risk}, {"_id": 0})
    riskfree_rate = risk_df["riskfree_rate"].values[0]
    cs = 0
    new_code = indc.retrack_Ainsudcode("optimal_debt_to_investcapital", indus_code)
    for e, value in new_code.items():
        DA = cs_df[cs_df["gics_code_third"]==e]["optimal_debt_to_investcapital"].values[0]
        D_E = 1 / (1 / DA - 1)
        cs += D_E * value

    return cs, riskfree_rate


def read_mongo_real():
    last_date = read_mongo_all("AM_origin", 'update_record')
    valuation_china_realestate_year_date = pd.Timestamp(
        last_date.loc[last_date['tablename'] == 'valuation_china_realestate_year', 'last_update_date'].values[0])
    valuation_china_realestate_month_date = pd.Timestamp(
        last_date.loc[last_date['tablename'] == 'valuation_china_realestate_month', 'last_update_date'].values[0])
    valuation_china_citizen_expense_season_date = pd.Timestamp(
        last_date.loc[last_date['tablename'] == 'valuation_china_citizen_expense_season', 'last_update_date'].values[0])
    valuation_china_realestate_year = read_mongo_limit("AM_origin", 'valuation_china_realestate_year',
                                                       {'update_date': valuation_china_realestate_year_date},
                                                       {'_id': 0, "update_date": 0})
    valuation_china_realestate_month = read_mongo_limit("AM_origin", 'valuation_china_realestate_month',
                                                        {'update_date': valuation_china_realestate_month_date},
                                                        {'_id': 0, "update_date": 0, "cpi_reside_rent_m": 0})
    valuation_china_citizen_expense_season = read_mongo_limit("AM_origin",
                                                              'valuation_china_citizen_expense_season',
                                                              {
                                                                  'update_date': valuation_china_citizen_expense_season_date},
                                                              {'_id': 0, "update_date": 0})
    [building_construction_area, cpi_reside_rent_y] = valuation_china_realestate_year.values.tolist()[0]
    [land_acquisition_area_m, land_transaction_price_m, real_estate_development_enterprises_funds_m] = \
    valuation_china_realestate_month.values.tolist()[0]
    [per_capita_disposable_income_reside, per_consumption_expenditure_reside] = \
    valuation_china_citizen_expense_season.values.tolist()[0]

    return building_construction_area,cpi_reside_rent_y,land_transaction_price_m,land_acquisition_area_m,real_estate_development_enterprises_funds_m, \
           per_consumption_expenditure_reside,per_capita_disposable_income_reside


def get_para(PID):
    # ###参数寻找

    return [pc_A,pc_3,pc_pbp,pc_pep,pc_evsp,exitY,bestY,exitYpc,TVpc,perpetuity_g_basic,perpetuity_eva_pc,perpetuity_ri_pc,M_pc,perpetuity_g_pc,perpetuity_ed_pc]


def get_stock_code(VID):
    name_list = []
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    sql = "select valuation_peer_ids from t_valuation_record where id=%s"
    try:
        cursor.execute(sql, [VID])
        peer_id = cursor.fetchall()[0][0]
    except Exception as e:
        logger(2, e)
        cursor.close()
        db.close()
    peer_list = peer_id.split("|")
    for peer in peer_list:
        demo_list = []
        peers = peer.split(",")
        format_strings = ",".join(['%s'] * len(peers))
        sql = "select stock_code from t_company_industry_code where id in (%s)" % format_strings
        cursor.execute(sql, peers)
        name_tuple = list(cursor.fetchall())
        for i in name_tuple:
            demo_list.append(i[0])
        name_list.append(demo_list)
    cursor.close()
    db.close()
    return name_list


def read_df(db, collection, code_list):
    conn = Conn(db)
    db = conn[db]
    collection = db[collection]
    cursor = collection.find({"_id": {"$in": code_list}}).batch_size(5000)
    temp_list = []
    # i = 0
    for single_item in cursor:
        temp_list.append(single_item)
    # print(cursor.next())
    df = pd.DataFrame(temp_list)
    conn.close()

    return df


def get_FFR(GR, FFR):
    demo = {}
    demo["mgr"] = GR[0]
    demo["fgr"] = GR[1:]
    res = dict(demo, **FFR)
    return res


def get_hypothesis_re(indus_code):
    last_date_cs = get_last_update_date("AM_hypothesis", "optimal_debt_to_investcapital")
    last_date_re = get_last_update_date("AM_hypothesis", "industry_re")
    last_date_risk = get_last_update_date("AM_hypothesis", "lasted_riskfree_risk")
    cs_df = read_mongo_limit("AM_hypothesis", "optimal_debt_to_investcapital", {"update_date": last_date_cs}, {"_id": 0})
    re_df = read_mongo_limit("AM_hypothesis", "industry_re", {"update_date": last_date_re}, {"_id": 0})
    risk_df = read_mongo_limit("AM_hypothesis", "lasted_riskfree_risk", {"update_date": last_date_risk}, {"_id": 0})
    riskfree_rate = risk_df["riskfree_rate"].values[0]
    cs = 0
    re = 0
    new_code = indc.retrack_Ainsudcode("optimal_debt_to_investcapital", indus_code)
    for e, value in new_code.items():
        DA = cs_df[cs_df["gics_code_third"]==e]["optimal_debt_to_investcapital"].values[0]
        DA = max(0.1, DA)
        D_E = DA / (1 - DA)
        cs += D_E * value

    new_code = indc.retrack_Ainsudcode("industry_re", indus_code)
    for e, value in new_code.items():
        re += re_df[re_df["gics_code_third"]==e]["industry_re"].values[0] * value

    return cs, re, riskfree_rate


def read_ipo(name):
    if name:
        redis_pool = redis.ConnectionPool(host=ConnDB.redis_host, port=ConnDB.redis_port, db=0,
                                          password=ConnDB.redis_password)
        r = redis.StrictRedis(connection_pool=redis_pool)
        if r.exists("ipo_a"):
            company_dict = eval(r.get("ipo_a").decode())
            if name in company_dict:
                if company_dict[name].startswith("68"):
                    return {"科创板": 0}
                else:
                    return {"沪深A股": 0}

        else:
            com = get_last_update_data("AM_origin", Db.company['tb'])
            data_dict = dict()
            if not com.empty:
                com = com.drop_duplicates(subset=["stock_code"]).reset_index()
                for index, data in com.iterrows():
                    data_dict[com.iloc[index]["name"]] = com.iloc[index]["stock_code"]
                r.set("ipo_a", str(data_dict), ex=604800)
                if name in data_dict:
                    if data_dict[name].startswith("68"):
                        return {"科创板": 0}
                    else:
                        return {"沪深A股": 0}

        if r.exists("ipo_hk"):
            company_dict = eval(r.get("ipo_hk").decode())
            if name in company_dict:
                return {"香港主板": 0}

        else:
            com = get_last_update_data("AM_origin", Db.hk_company['tb'])
            data_dict = dict()
            if not com.empty:
                com = com.drop_duplicates(subset=["stock_code"]).reset_index()
                for index, data in com.iterrows():
                    data_dict[com.iloc[index]["name"]] = com.iloc[index]["stock_code"]
                r.set("ipo_hk", str(data_dict), ex=604800)
                if name in data_dict:
                    return {"香港主板": 0}

        if r.exists("ipo_america"):
            company_dict = eval(r.get("ipo_america").decode())
            if name in company_dict:
                return {"美股市场": 0}

        else:
            com = get_last_update_data("AM_origin", Db.america_company['tb'])
            data_dict = dict()
            if not com.empty:
                com = com.drop_duplicates(subset=["stock_code"]).reset_index()
                for index, data in com.iterrows():
                    data_dict[com.iloc[index]["name"]] = com.iloc[index]["stock_code"]
                r.set("ipo_america", str(data_dict), ex=604800)
                if name in data_dict:
                    return {"美股市场": 0}

        if r.exists("ipo_san"):
            company_dict = eval(r.get("ipo_san").decode())
            if name in company_dict:
                return {"新三板": 0}
            else:
                return False
        else:
            com = get_last_update_data("AM_origin", Db.san_company['tb'])
            data_dict = dict()
            if not com.empty:
                com = com.drop_duplicates(subset=["stock_code"]).reset_index()
                for index, data in com.iterrows():
                    data_dict[com.iloc[index]["name"]] = com.iloc[index]["stock_code"]
                r.set("ipo_san", str(data_dict), ex=604800)
                if name in data_dict:
                    return {"新三板": 0}
                else:
                    return False
            else:
                return False
    else:
        return False


def get_peer(code_list):
    if code_list:
        db = connect_mysql_rdt_fintech()
        cursor = db.cursor()
        sql = "select id from t_company_industry_code where stock_code in %s"
        cursor.execute(sql, [tuple(code_list)])
        id_list = cursor.fetchall()
        if id_list:
            res = [i[0] for i in id_list]
            return res[:10]
        else:
            return False
    else:
        return False


def get_peer_code(data_1, data_2):

    code_list = data_2[data_2["gics"] == data_1["gics"]]["stock_code"]
    demo = [data_1["stock_code"]]
    res = get_peer(list(set(code_list) - set(demo)))
    if res:
        return res
    else:
        code_list = data_2[data_2["gics"].apply(lambda x: x.startswith(data_1["gics"][:6]))]["stock_code"]
        demo = [data_1["stock_code"]]
        res = get_peer(list(set(code_list) - set(demo)))
        if res:
            return res
        else:
            code_list = data_2[data_2["gics"].apply(lambda x: x.startswith(data_1["gics"][:4]))]["stock_code"]
            demo = [data_1["stock_code"]]
            res = get_peer(list(set(code_list) - set(demo)))
            return res
