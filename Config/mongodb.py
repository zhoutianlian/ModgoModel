from Config.Database import ConnDB
import pandas as pd
from pymongo import MongoClient
from Config.CONFIG import config


#     mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
#     mongo_uri = 'mongodb://hub:hubhub@:47.100.56.171:27017/'+db_name
username = config['DEFAULT']['mongo_user']
password = config['DEFAULT']['mongo_password']
host = ConnDB.host
# host = "192.168.2.105"
port = ConnDB.port
def Conn(db):
    mongo_uri = 'mongodb://%s:%s@%s:%s/?authSource=%s' % (username, password, host, port, db)
    conn = MongoClient(mongo_uri)
    return conn

# def connect_mongo():
#     #     mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
#     #     mongo_uri = 'mongodb://hub:hubhub@:47.100.56.171:27017/'+db_name
#     username = 'hub'
#     password = 'hubhub'
#     host = ConnDB.host
#     # host = "192.168.2.105"
#     port = ConnDB.port
#     mongo_uri = 'mongodb://%s:%s@%s:%s/?authSource=admin' % (username, password, host, port)
#     conn = MongoClient(mongo_uri)
#     return conn


def read_mongo_all(db_name, collection_name):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    cursor = collection.find().batch_size(5000)

    temp_list = []
    # i = 0;
    for single_item in cursor:
        temp_list.append(single_item)
        # i = i + 1
        # if (i % 5000 == 0):
        #     print(i)

    df = pd.DataFrame(temp_list)

    conn.close()
    del df['_id']

    return df


def read_mongo_columns(db_name, collection_name, query):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    cursor = collection.find({}, query).batch_size(5000)

    temp_list = []
    # i = 0;
    for single_item in cursor:
        temp_list.append(single_item)
        # i = i + 1
        # if (i % 5000 == 0):
        #     print(i)

    df = pd.DataFrame(temp_list)

    conn.close()

    return df


def read_mongo(db_name, collection_name, conditions):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    cursor = collection.find(conditions).batch_size(5000)

    temp_list = []
    # i = 0
    for single_item in cursor:
        temp_list.append(single_item)
        # i = i + 1
        # if (i % 5000 == 0):
        #     print(i)

    df = pd.DataFrame(temp_list)

    conn.close()

    return df


def read_mongo_limit(db_name, collection_name, conditions,result):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    cursor = collection.find(conditions,result).batch_size(5000)

    temp_list = []
    # i = 0
    for single_item in cursor:
        temp_list.append(single_item)
        # i = i + 1
        # if (i % 5000 == 0):
        #     print(i)

    df = pd.DataFrame(temp_list)

    conn.close()

    return df


def save_mongo(db_name, collection_name, data):
    # conn = connect_mongo()
    conn = Conn(db_name)
    # 如果存在则直接引用，不存在则自动创建库 database name
    db = conn[db_name]
    # 如果存在则直接引用，不存在则自动创建 table name
    collection = db[collection_name]

    # *将dataframe转化为json，但是时间类型数据变为数字
    # *records = json.loads(data.T.to_json()).values()

    # 将dataframe转化为dict，时间类型数据正常
    records = data.to_dict('records')
    collection.insert_many(records)

    conn.close()


def save_mongo_from_dict(db_name, collection_name, data):
    # conn = connect_mongo()
    # 如果存在则直接引用，不存在则自动创建库 database name
    conn = Conn(db_name)
    db = conn[db_name]
    # 如果存在则直接引用，不存在则自动创建 table name
    collection = db[collection_name]

    # *将dataframe转化为json，但是时间类型数据变为数字
    # *records = json.loads(data.T.to_json()).values()

    # 将dataframe转化为dict，时间类型数据正常
    collection.insert_one(data)

    conn.close()


def show_collections(db_name):
    # conn = connect_mongo()
    # 如果存在则直接引用，不存在则自动创建库 database name
    conn = Conn(db_name)
    db = conn[db_name]
    # 如果存在则输出collection的名字
    ans=db.list_collection_names()


    conn.close()

    return ans


def delete_collection(db_name,collection_name):
    # conn = connect_mongo()
    # 如果存在则直接引用，不存在则自动创建库 database name
    conn = Conn(db_name)
    db = conn[db_name]
    # 如果存在则输出collection的名字
    ans = db.list_collection_names()
    if collection_name in ans:
        # 删除表名
        db.drop_collection(collection_name)
        print('delete success')
    else:
        print ('no such collection!')
    conn.close()


def get_mvalue(db_name,collection_name,column_name,sort):
    # conn = connect_mongo()
    #取最大值sort赋值-1
    #取最小值sort赋值1
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]

    target = list(collection.find().sort([(column_name,sort)]).limit(1))[0][column_name]
    conn.close()
    return target


def get_last_update_date(db_name,table_name):
    last_date = read_mongo_limit(db_name, 'update_record', {'tablename': table_name},
                     {'last_update_date': 1, '_id': 0}).iloc[0, 0]
    return last_date


def get_last_update_data(db_name, table_name):
    last_date = read_mongo_limit(db_name, 'update_record', {'tablename': table_name},
                                 {'last_update_date': 1, '_id': 0}).iloc[0, 0]
    data = read_mongo_limit(db_name, table_name, {"update_date": last_date}, {"_id": 0})
    return data


def update_data(db_name,collection_name,column_name,myquery,newvalues,number):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    column = collection[column_name]
    if number ==1:
        column.update_one(myquery,newvalues)
        print('更新单条数据成功')
    else:
        column.update_many(myquery, newvalues)
        print('更新多条数据成功')

    conn.close()


def update_data_demo(db_name,collection_name,myquery,newvalues,number):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collection = db[collection_name]
    if number ==1:
        collection.update_one(myquery,newvalues)
        print('更新单条数据成功')
    else:
        collection.update_many(myquery, newvalues)
        print('更新多条数据成功')

    conn.close()


def show_item_count(db_name):
    # conn = connect_mongo()
    conn = Conn(db_name)
    db = conn[db_name]
    collections = db.list_collection_names()
    ans={}
    for table in collections:
        collection = db[table]
        num=collection.find().count()
        ans[table]=num
    conn.close()
    return ans

# ans=show_item_count('AM_basement')
# for key,value in ans.items():
#     if value!=111712:
#         print (key,value)


# data_bal = read_mongo_limit("rdt_fintech", "VC", {"_id": "vc153"}, None)
# data_flow = read_mongo_limit("rdt_fintech", "Flow", {"_id": "f1338"}, None)
#
# data_bal["_id"] = 153
# data_flow["_id"] = 1061
# # data["balId"] = [1091]
# # data["flowId"] = [1059]
# save_mongo("rdt_fintech", "VC", data_bal)
# save_mongo("rdt_fintech", "Flow", data_flow)

# data = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": 1759}, None)
# data_flow = read_mongo_limit("rdt_fintech", "Flow", {"_id": "f1059"}, None)

# data["_id"] = 3845
# del data["balId"]
# del data["flowId"]
# data["vcId"] = 135
# data["balId"] = [1091]
# data["flowId"] = [1059]
# save_mongo("rdt_fintech", "ValuatingInput", data)
# save_mongo("rdt_fintech", "Flow", data_flow)