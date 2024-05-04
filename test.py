import pandas as pd
from copy import deepcopy
from math import log10

import Config.Database

Config.Database.set_db("test")

# from Valuatoin.valuation_mini import run_mini
#
#
# def change(num):
#     unit = 1
#     if num < 0:
#         unit = -1
#     elif num == 0:
#         return num
#     num = abs(num)
#     mag = int(log10(num))
#     num = int(str(num)[:2]) * pow(10, mag - 1) * unit
#     return num
#
#
# data = pd.read_excel("modgo估值.xls")
# data_res = deepcopy(data)
# data_res["res"] = 0
# data_res["rev"] = 0
# data_res["profit"] = 0
# for index, value in data.iterrows():
#     name = value["全称"]
#     print(name)
#     indus = value["GICS行业代码"]
#     staff = value["员工人数"]
#     a = value["营业收入（万）"] * 10000
#     rev = change(a)
#     b = value["营业利润（万）"] * 10000
#     profit = change(b)
#     if rev <= 0 or profit == 0:
#         data_res["res"].iloc[index] = None
#         data_res["rev"].iloc[index] = rev
#         data_res["profit"].iloc[index] = profit
#         continue
#     print("开始估值")
#     res = run_mini(0, 0, name, indus, staff, rev, profit, saving=False)
#     # print(res)
#     data_res["res"].iloc[index] = res
#     data_res["rev"].iloc[index] = rev
#     data_res["profit"].iloc[index] = profit
#     # print(data_res.iloc[index])
# data_res.to_csv("result.csv", index=0, encoding="gbk")

import random
import pandas as pd

from Data.Conn import connect_mysql_rdt_fintech
from Config.mongodb import read_mongo_limit

db = connect_mysql_rdt_fintech()
cursor = db.cursor()

sql_com = "select enterprise_name,enterprise_gicscode from t_enterprise_info where id=%s"
sql_indus = "select industry_name from t_industry_info where id=%s"

name_list = []
indus_list = []
for i in range(5000, 10000):
    cursor.execute(sql_com, [i])
    find = cursor.fetchall()
    if find:
        name, indus_code = find[0]
        cursor.execute(sql_indus, [str(indus_code)[:2]])
        indus = cursor.fetchall()[0][0]
        name_list.append(name)
        indus_list.append(indus)

data = pd.DataFrame()
data["name"] = name_list
data["indus"] = indus_list

data_tyc = read_mongo_limit("tyc_data", "TycEnterpriseInfo", {"name": {"$in": name_list}},
                            {"_id": 0, "name": 1, "socialStaffNum": 1, "estiblishTime": 1, "regLocation": 1, "regCapital": 1})

data_patent = read_mongo_limit("tyc_data", "Patent", {"enterpriseName": {"$in": name_list}},
                               {"_id": 0, "enterpriseName": 1, "patentType": 1})

data_patent.rename(columns={"enterpriseName": "name"}, inplace=True)

data = data.merge(data_tyc, on=["name"])
data = data.merge(data_patent, on=["name"], how="left")
data.to_csv("res.csv", index=0, encoding="utf-8-sig")