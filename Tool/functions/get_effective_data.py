import pymongo
import pandas as pd
from Config.mongodb import Conn


def get_data(db, collection, count):
    if collection == "valuation_china_realestate_month":
        res = {"_id": 0, "update_date": 0, "cpi_reside_rent_m": 0}
    else:
        res = {"_id": 0, "update_date": 0}
    conn = Conn(db)
    result = conn[db][collection].find(None, res).limit(count).sort([("update_date",pymongo.DESCENDING)])
    temp_list = []
    # i = 0;
    for single_item in result:
        temp_list.append(single_item)

    df = pd.DataFrame(temp_list)
    df = df.replace({0: None})
    df.dropna(axis=0, inplace=True)
    conn.close()
    if not df.empty:
        return df.iloc[0]
    else:
        return None


def get_effective_data(db, collection):

    data = get_data(db, collection, 10)
    if data is not None:
        return data
    else:
        data = get_data(db, collection, 20)
        return data

