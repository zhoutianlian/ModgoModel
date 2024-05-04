from .EMQuantAPI_Python.python3.EmQuantAPI import *


def get_company_info():
    c.start()
    update_date = "2019-11-23"
    company_code = c.sector("001004", update_date)
    company_code_list = company_code.Codes
    # 获取公司证券资料（股票简称、上市、退市日期）
    data_date = c.css(company_code_list, "COMPNAME,EMPLOYEENUM", "Ispandas=1, Year=2019").reset_index()
    # 合并数据
    data_date.rename(columns={'CODES': 'stock_code', "COMPNAME": "company_name", "EMPLOYEENUM": "staff"}, inplace=True)
    c.stop()
    return data_date
