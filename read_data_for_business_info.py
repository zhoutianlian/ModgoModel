import pandas as pd
import numpy as np
import requests

from connect_mongo import read_mongo_limit


def merge_table_all(table_list, merge_key, merge_rule):
    data = table_list[0]
    for i in table_list[1:]:
        data = pd.merge(data, i, how=merge_rule, on=merge_key)

    return data


def get_data_for_business_info(company_name):
    company_business_info = read_mongo_limit('tyc_data', 'TycEnterpriseInfo', {'name': company_name},
                                             {'_id': 0}).drop_duplicates(subset=['name'])
    if company_business_info.empty:
        company_name = company_name.replace("(", "（")
        company_name = company_name.replace(")", "）")
        company_business_info = read_mongo_limit('tyc_data', 'TycEnterpriseInfo', {'name': company_name},
                                                 {'_id': 0}).drop_duplicates(subset=['name'])
    if "businessScope" in company_business_info:
        res = requests.post("http://101.132.32.7:7000/indus", data={"text": company_business_info["businessScope"]})
        gics1 = res.content.decode()[:2]
    else:
        gics1 = "10"

    # staff
    if "socialStaffNum" in company_business_info:
        company_staff = company_business_info[['name', 'socialStaffNum']]
        company_staff.replace("-", 0, inplace=True)
    else:
        company_business_info['socialStaffNum'] = 0
        company_staff = company_business_info[['name', 'socialStaffNum']]
    company_staff.replace(np.nan, 0, inplace=True)
    company_staff.rename(columns={'name': 'company_name', 'socialStaffNum': 'staffNum'}, inplace=True)

    # RegCapital or 实缴资本
    if "actualCapital" in company_business_info:
        company_capital = company_business_info[['name', 'actualCapital']]
        company_capital.rename(columns={'actualCapital': 'regCapital'}, inplace=True)
    else:
        company_capital = company_business_info[['name', 'regCapital']]
    company_capital.replace("-", 0, inplace=True)
    try:
        company_capital['split'] = company_capital['regCapital'].str.split('万')
        company_capital['注册资本数字'] = company_capital['split'].apply(lambda x: x[0])
        company_capital['注册资本unit'] = company_capital['split'].apply(lambda x: x[1])

        company_capital['注册资本数字'] = company_capital['注册资本数字'].astype('float64')

        company_capital.loc[company_capital['注册资本unit'] == '美元', '注册资本CNY'] = company_capital.loc[company_capital[
                                                                                                      '注册资本unit'] == '美元', '注册资本数字'] * 70000
        company_capital.loc[company_capital['注册资本unit'] == '人民币', '注册资本CNY'] = company_capital.loc[company_capital[
                                                                                                       '注册资本unit'] == '人民币', '注册资本数字'] * 10000
        company_capital.loc[company_capital['注册资本unit'] == '日元', '注册资本CNY'] = company_capital.loc[company_capital[
                                                                                                      '注册资本unit'] == '日元', '注册资本数字'] * 660

        company_capital = company_capital[['name', '注册资本CNY']]

        company_capital.rename(columns={'name': 'company_name', '注册资本CNY': 'regCapital'}, inplace=True)
    except Exception as e:
        print(e)
        company_capital = pd.DataFrame([[company_name, 0]], columns=["company_name", "regCapital"])
    # patent
    company_patent = read_mongo_limit('tyc_data', 'Patent', {'enterpriseName': company_name}, {'_id': 0})
    if not company_patent.empty:
        if "patent_status" in company_business_info:
            company_patent = company_patent[company_patent["patent_status"] == "无效"]
            company_patent = company_patent.groupby('enterpriseName').count().reset_index()
        else:
            company_patent["applicantname"] = 0
    else:
        company_patent["enterpriseName"] = company_name
        company_patent["applicantname"] = 0
    company_patent = company_patent[['enterpriseName', 'applicantname']]
    company_patent.rename(columns={'enterpriseName': 'company_name', 'applicantname': 'unValidPatentsNum'},
                          inplace=True)

    company_name_df = pd.DataFrame([company_name]).rename(columns={0: 'company_name'})

    company_patent = pd.merge(company_patent, company_name_df, how='right', on='company_name')

    company_patent.replace(np.nan, 0, inplace=True)

    # merge
    company_data = merge_table_all(
        [company_staff, company_capital, company_patent], 'company_name',
        'inner')

    return {"gics": gics1, "staff": company_data["staffNum"].values[0],
            "regCapital": company_data["regCapital"].values[0],
            "patent": int(company_data["unValidPatentsNum"].values[0])}

