from pymongo import MongoClient
import pandas as pd

def connect_mongo():
    #     mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
    #     mongo_uri = 'mongodb://hub:hubhub@:47.100.56.171:27017/'+db_name
    username = 'hub'
    password = 'hubhub'
    host = "192.168.2.105"
    port = '27017'
    mongo_uri = 'mongodb://%s:%s@%s:%s/?authSource=admin' % (username, password, host, port)
    conn = MongoClient(mongo_uri)
    return conn

def read_mongo_all(db_name, collection_name):
    conn = connect_mongo()
    db = conn[db_name]
    collection = db[collection_name]
    cursor = collection.find().batch_size(5000)

    temp_list = []
    i = 0
    for single_item in cursor:
        temp_list.append(single_item)
        i += 1
        if i % 5000 == 0:
            print(i)

    df = pd.DataFrame(temp_list)

    conn.close()
    del df['_id']
    print('read success')

    return df

def save_mongo_from_dict(db_name, collection_name, data):
    conn = connect_mongo()
    # 如果存在则直接引用，不存在则自动创建库 database name
    db = conn[db_name]
    # 如果存在则直接引用，不存在则自动创建 table name
    collection = db[collection_name]

    # *将dataframe转化为json，但是时间类型数据变为数字
    # *records = json.loads(data.T.to_json()).values()

    # 将dataframe转化为dict，时间类型数据正常
    collection.insert_one(data)

    conn.close()


def save_to_mongo(SS_R):
    save_mongo_from_dict("rdt_fintech", "valuation_result_corporation_mini", SS_R)


def save_data(SS_R, mv, p_price, equity, other_value, stock_code, stock_name):
    SS_R["mv"] = mv
    SS_R["p_price"] = p_price
    SS_R["p_avg"] = (SS_R["MV_avg"] - other_value) / equity
    SS_R["p_swing"] = (SS_R["p_avg"] / SS_R["p_price"]) - 1
    SS_R["stock_code"] = stock_code
    SS_R["stock_name"] = stock_name

    save_to_mongo(SS_R)
