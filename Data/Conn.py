# -*- coding: utf-8 -*-：
import copy
from abc import abstractmethod
from pymongo import MongoClient
from pymysql import connect
from pandas import DataFrame
from Report.Log import logger
from Config.Database import ConnDB as conn


__all__ = ['ConnMongo', 'ConnMysql', 'connect_mysql_rdt_fintech', "connect_mysql_Require_Rate_of_Return",
           "connect_mysql_valuation_samuelson", "connect_mysql_valuation"]


class ConnDB:
    """
    这是一个连接数据库的虚拟类
    """

    def __init__(self, db: str, host: str = 'root', port: int = 27017):
        """
        创建一个连接实例
        :param db: 数据库名称
        """
        self.__dbname__ = db  # 不可由外部访问的数据库名称
        self.__host__ = host  # 不可由外部访问的host属性
        self.__port__ = port
        self.__conn__ = None  # 不可由外部访问的连接实例
        self.__db__ = None
        self.__tb__ = None
        self.__cursor__ = None
        self.__map__ = None

    @abstractmethod
    def __enter__(self):
        """
        使用with...as...连接数据库的方法
        :return:
        """
        raise NotImplemented

    async def __aenter__(self):
        """
        使用with...as...异步连接数据库的方法
        :return:
        """
        return self.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self.__conn__.close()
        if exc_value is None:
            info = f'关闭 <{self.__dbname__}>数据库'
            logger(0, info)
        else:
            info = f'连接或读取<{self.__dbname__}>失败\n错误类型: {exc_type}\n错误信息 {exc_value}\n错误追溯: {traceback}'
            logger(2, info)
        return False

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        使用with...as...异步连接时的退出
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        return self.__exit__(exc_type, exc_value, traceback)

    async def wait(self, func, *args, **kwargs):
        """
        这是一个将类的方法异步化的方法
        :param func:
        :param args:
        :return:
        """
        return self.__getattribute__(func)(*args, **kwargs)

    @abstractmethod
    def __call__(self, table: str):
        """
        这是一个打开表的方法
        :param table:
        :return:
        """
        raise NotImplemented


class ConnMongo(ConnDB):
    """
    这个类用于连接mongodb
    """

    def __init__(self, db: str, uri: str):
        super().__init__(db)
        from pymongo import ASCENDING, DESCENDING
        self.uri = uri
        self.ASCENDING = ASCENDING
        self.DESCENDING = DESCENDING
        self.batch_size = 5000

    def __enter__(self):
        """
        with... as... 连接数据库的方法
        :return:
        """
        self.__conn__ = MongoClient(self.uri)
        self.__db__ = self.__conn__[self.__dbname__]
        info = f'连接 <Mongo> <{self.__dbname__}>数据库 <uri={self.uri}>'
        logger(0, info)
        return self

    def __call__(self, table: str):
        self.__tbname__ = table
        self.__tb__ = self.__db__[table]
        return self

    def __select(self, select):
        """
        条件筛选转换方法
        :param select: 字符串、列表、元组、集合或字典（以value为数据库内的名称，key为修改成的名称)
        :return: pymongo默认的字典 {字段名: 1}
        """
        if type(select) is str:
            return {select: 1}
        elif type(select) in [list, tuple, set]:
            return {s: 1 for s in select}
        elif type(select) is dict:
            self.__map__ = select
            return {s: 1 for s in select.values()}

    @staticmethod
    def __sort(sort):
        """
        排序转换方法
        :param sort: 字典 {字段名: 排序方式}
        :return: pymongo默认的列表 [(字段名, 排序方式)]
        """
        return [(key, value) for key, value in sort.items()]

    def find_one(self, where: dict = None, select: any = None, sort: dict = None, sequence: int = 0):
        """
        查询单条数据
        :param where: 条件筛选
        :param select: 返回字段
        :param sort: 排序
        :param sequence: 第几个
        :return:
        """
        projection = None if select is None else self.__select(select)
        sorting = None if sort is None else self.__sort(sort)
        data = self.__tb__.find_one(filter=where, projection=projection, sort=sorting, skip=sequence)
        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        if self.__map__ is not None:
            data = {key: data[value] for key, value in self.__map__.items()}
            self.__map__ = None
        return data

    def find(self, where: dict = None, select: any = None, sort: dict = None, size: int = None,
             skip: int = 0):
        """
        简化的数据查询方法
        :param where: 条件筛选
                $lt     小于                  {'age': {'$lt': 20}}
                $gt     大于                  {'age': {'$gt': 20}}
                $lte    小于等于              {'age': {'$lte': 20}}
                $gte    大于等于
                $ne     不等于                {'age': {'$ne': 20}}
                $in     在范围内               {'age': {'$in': [20, 23]}}
                $nin    不在范围内             {'age': {'$nin': [20, 23]}}
                $regex  匹配正则               {'name': {'$regex': '^M.*'}}name以M开头
                $exists 属性是否存在           {'name': {'$exists': True}}name属性存在
                $type   类型判断               {'age': {'$type': 'int'}}age的类型为int
                $mod    数字模操作             {'age': {'$mod': [5, 0]}}年龄模5余0
                $text   文本查询               {'$text': {'$search': 'Mike'}}text类型的属性中包含Mike字符串
                $where  高级条件查询            {'$where': 'obj.fans_count == obj.follows_count'}自身粉丝数等于关注数
        :param select: 返回字段 字符串、列表、元组或集合
        :param sort: 排序字典 字段名: 排序方式  1: 升序（第一个为最小）, -1: 降序（第一个为最大）
        :param size: 最大返回数据量
        :param skip: 跳过数据量
        :return:
        """
        projection = None if select is None else self.__select(select)
        sorting = None if sort is None else self.__sort(sort)

        if size is None:
            self.__cursor__ = self.__tb__.find(filter=where, projection=projection, sort=sorting, skip=skip) \
                .batch_size(self.batch_size)
        else:
            self.__cursor__ = self.__tb__.find(filter=where, projection=projection, sort=sorting, limit=size,
                                               skip=skip).batch_size(self.batch_size)

        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        data = DataFrame(list(self.__cursor__))
        if self.__map__ is not None:
            rename = {value: key for key, value in self.__map__}
            data = data.rename(columns=rename)
            self.__map__ = None
        return data

    def find_new(self, where: dict = None, select: any = None):
        """
        按照update_date查询最新
        :param where:
        :param select:
        :return:
        """
        tb = self.__tbname__
        # new_date = self(tb).find_one(sort={'update_date': -1}, select='update_date')['update_date']  # 自我排序法
        new_date = self.__db__["update_record"].find_one({"tablename": tb}, {"_id": 0, "last_update_date": 1})["last_update_date"]
        where = dict() if where is None else where
        where['update_date'] = new_date
        return self(self.__tbname__).find(where=where, select=select)

    def count(self, where: dict = None):
        """
        对查询结果进行计数
        :param where:
        :return:
        """
        count = self.__tb__.find(filter=where).count()
        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        return count

    def update_one(self, where: dict, new: dict = None, change: dict = None, upsert: bool = False):
        """
        找到并更新一条数据
        :param where:
        :param new: 覆盖更新
        :param change: 增量更新
        :param upsert: 如果数据不存在是否新建
        :return: 匹配数量和更新数量
        """
        match, modify = 0, 0
        if new is not None:
            result = self.__tb__.update_one(where, {'$set': new}, upsert=upsert)
            match += result.matched_count
            modify += result.modified_count
        if change is not None:
            result = self.__tb__.update_one(where, {'$inc': change}, upsert=upsert)
            match += result.matched_count
            modify += result.modified_count
        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 更新记录<{modify}>条 (匹配<{match}>条)'
        logger(2, info)
        return match, modify

    def update_many(self, where: dict, new: dict = None, change: dict = None, upsert: bool = False):
        """
        找到并更新一条数据
        :param where:
        :param new: 覆盖更新
        :param change: 增量更新
        :param upsert: 如果数据不存在是否新建
        :return: 匹配数量和更新数量
        """
        match, modify = 0, 0
        if new is not None:
            result = self.__tb__.update_many(where, {'$set': new}, upsert=upsert)
            match += result.matched_count
            modify += result.modified_count
        if change is not None:
            result = self.__tb__.update_many(where, {'$inc': change}, upsert=upsert)
            match += result.matched_count
            modify += result.modified_count
        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 更新记录<{modify}>条 (匹配<{match}>条)'
        logger(2, info)
        return match, modify

    def insert(self, data: any):
        """
        插入记录
        :param data: 数据字典或数据框架
        :return: 插入的_id值
        """
        assert type(data) in [dict, DataFrame], f'非法的数据格式{type(data)}'
        if type(data) is dict:
            insert_result = self.__tb__.insert_one(data)
            result = insert_result.inserted_id
        else:
            data_list = data.to_dict('records')
            insert_result = self.__tb__.insert_many(data_list)
            result = insert_result.inserted_ids
        self.__tb__ = None
        info = f'在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 插入记录 _id={result}'
        logger(0, info)
        return result

    def delete_one(self, where: dict):
        """
        删除一条记录
        :param where: 条件
        :return: 删除记录数
        """
        result = self.__tb__.delete_one(where)
        count = result.deleted_count
        self.__tb__ = None
        info = f'警告: 在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 删除记录<{count}>条'
        logger(2, info)
        return count

    def delete_many(self, where: dict):
        """
        批量删除数据
        :param where:
        :return:
        """
        result = self.__tb__.delete_many(where)
        count = result.deleted_count
        self.__tb__ = None
        info = f'警告: 在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 删除记录<{count}>条'
        logger(2, info)
        return count

    def replace_one(self, where: dict, data: dict, upsert: bool = False):
        """
        替换一条数据
        :param where:
        :param data:
        :param upsert:
        :return:
        """
        result = self.__tb__.replace_one(where, data, upsert=upsert)
        match, modify = result.matched_count, result.modified_count
        self.__tb__ = None
        info = f'警告: 在 <Mongo> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 替换记录<{modify}>条 (匹配<{match}>条)'
        logger(2, info)
        return match, modify

    def upsert(self, where: dict, data: any):
        """
        替换或插入记录
        :param where:
        :param data:
        :return:
        """
        tb = self.__tbname__
        try:
            self(tb).delete_many(where)
        except Exception as err:
            print(err)
        finally:
            if type(data) is dict:
                where.update(data)
                data = where
            elif type(data) is DataFrame:
                for key, value in where:
                    if key not in data.columns:
                        data[key] = value
            else:
                raise TypeError
            self(tb).insert(data)


class ConnMysql(ConnDB):
    """
    这个类用于连接mysql
    """

    def __init__(self, db: str, host: str, port: int = 3306, user: str = 'root', password: str = 'root',
                 charset: int = 'utf8mb4'):
        super().__init__(db, host, port)
        self.__user__ = user
        self.__password__ = password
        self.__charset__ = charset
        self.__conn__ = None
        self.__cursor__ = None
        self.__resql()

    def __enter__(self):
        """
        连接
        :return:
        """
        self.__conn__ = connect(host=self.__host__,
                                port=self.__port__,
                                user=self.__user__,
                                password=self.__password__,
                                database=self.__dbname__,
                                charset=self.__charset__)

        self.__cursor__ = self.__conn__.cursor()
        info = f'连接 <Mysql> <{self.__dbname__}>数据库 <host={self.__host__} port={self.__port__} user={self.__user__}>'
        logger(0, info)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__conn__.commit()
        self.__cursor__.close()
        return super().__exit__(exc_type, exc_value, traceback)

    def __call__(self, table):
        self.__fromsql__ = f'FROM {table}'
        self.__insertsql__ = f'INSERT INTO {table}'
        self.__updatesql__ = f'UPDATE {table}'
        self.__deletesql__ = f'DELETE FROM {table}'
        self.__tbname__ = table
        return self

    def __resql(self):
        """
        重置SQL
        :return:
        """
        self.__selectsql__ = 'SELECT *'
        self.__fromsql__ = ''
        self.__wheresql__ = ''
        self.__groupsql__ = ''
        self.__havingsql__ = ''
        self.__ordersql__ = ''
        self.__insertsql__ = ''
        self.__valuessql__ = ''
        self.__updatesql__ = ''
        self.__setsql__ = ''
        self.__deletesql__ = ''
        self.__values__ = None

    def __select(self, select):
        """
        将返回字段转换为SQL
        :param select:
        :return:
        """
        if select is None:
            select_sql = '*'
        elif type(select) is str:
            select_sql = select
        else:
            select_sql = ', '.join(select)
        self.__selectsql__ = f'SELECT {select_sql}'

    def __where(self, where):
        """
        将筛选条件转换为SQL
        :param where:
        :return:
        """
        if where is not None:
            mapping = {'$lt': '<',
                       '$gt': '>',
                       '$lte': '<=',
                       '$gte': '>=',
                       '$ne': '<>',
                       '$in': ' IN ',
                       '$nin': ' NOT IN',
                       '$regex': ' REGEXP ',
                       '$like': ' LIKE ',
                       }
            sql = []
            for key, value in where.items():
                if type(value) is dict:
                    for k, v in value.items():
                        if type(v) is str:
                            sql.append(f'{key}{mapping[k]}{v}')
                        elif type(v) in [list, tuple, set]:
                            sql.append(f'{key}{mapping[k]}{tuple(v)}')
                        else:
                            sql.append(f'{key}{mapping[k]}\'{v}\'')
                elif type(value) is str:
                    sql.append(f'{key}=\'{value}\'')
                else:
                    sql.append(f'{key}={value}')
            if len(sql) > 0:
                where_sql = ' AND '.join(sql)
                self.__wheresql__ = f'WHERE {where_sql}'

    def __order(self, order: dict):
        """
        将排序转换为SQL
        :param order:
        :return:
        """
        if order is not None:
            sql = []
            for key, value in order.items():
                if value == -1:
                    sql.append(f'{key} DESC')
                elif value == 1:
                    sql.append(f'{key} ASC')
            order_sql = ', '.join(sql)
            self.__ordersql__ = f'ORDER BY {order_sql}'

    def __values(self, data):
        """
        将插入转换为SQL
        :param data:
        :return:
        """
        if type(data) is dict:
            into_sql = ', '.join(data.keys())
            sub_sql = ', '.join(['%s'] * len(data))
            self.__valuessql__ = f'({into_sql}) VALUES({sub_sql})'
            val_sql = tuple(map(lambda x: str(x), data.values()))
            self.__values__ = val_sql
        elif type(data) is DataFrame:
            into_sql = ', '.join(data.columns)
            sub_sql = ', '.join(['%s'] * data.shape[1])
            self.__valuessql__ = f'({into_sql}) VALUES({sub_sql})'
            val_sql = data.applymap(lambda x: str(x)).to_records(index=0).tolist()
            self.__values__ = val_sql
        else:
            raise ValueError

    def __set(self, data: dict):
        """
        将更新转换为SQL
        :param data:
        :return:
        """
        sql = []
        for key, value in data.items():
            sql.append(f'{key}=\'{value}\'')
        set_sql = ', '.join(sql)
        self.__setsql__ = f'SET {set_sql}'

    def __sql(self, act: str):
        """
        执行当前SQL并重置
        :return:
        """
        if act == 'query':
            sql = ' '.join([self.__selectsql__, self.__fromsql__, self.__wheresql__,
                            self.__groupsql__, self.__havingsql__, self.__ordersql__])
            # print(sql)
            self.__cursor__.execute(sql)

        elif act == 'insert':
            sql = ' '.join([self.__insertsql__, self.__valuessql__])
            # print(sql)
            if type(self.__values__) is tuple:
                self.__cursor__.execute(sql, self.__values__)
            else:
                self.__cursor__.executemany(sql, self.__values__)

        elif act == 'update':
            sql = ' '.join([self.__updatesql__, self.__setsql__, self.__wheresql__])
            # print(sql)
            self.__cursor__.execute(sql)

        elif act == 'delete':
            sql = ' '.join([self.__deletesql__, self.__wheresql__])
            # print(sql)
            self.__cursor__.execute(sql)
        else:
            raise ValueError

        self.__resql()

    def __get_names(self):
        data_info = self.__cursor__.description
        return [data[0] for data in data_info]

    def find_one(self, where: dict = None, select: any = None, sort: dict = None, sequence: int = None):
        """
        查询单条数据
        :param where:
        :param select:
        :param sort:
        :param sequence:
        :return:
        """
        self.__select(select)
        self.__where(where)
        self.__order(sort)
        self.__sql('query')
        sequence = 0 if sequence is None else sequence
        for i in range(sequence):
            self.__cursor__.fetchone()
        data = self.__cursor__.fetchone()
        names = self.__get_names()
        info = f'在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        if data:
            return dict(zip(names, data))
        else:
            return dict()

    def find(self, where: dict = None, select: any = None, sort: dict = None, size: int = None,
             skip: int = None):
        """
        批量查询数据
        :param where:
        :param select:
        :param sort:
        :param size:
        :param skip:
        :return:
        """
        self.__select(select)
        self.__where(where)
        self.__order(sort)
        self.__sql('query')
        skip = 0 if skip is None else skip
        data = self.__cursor__.fetchall() if size is None else self.__cursor__.fetchmany(size + skip)
        names = self.__get_names()
        df = DataFrame(list(data), columns=names)
        df = df.iloc[skip:]
        info = f'在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        return df

    def count(self, where: dict = None):
        self.__where(where)
        self.__sql('query')
        info = f'在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 查询记录'
        logger(0, info)
        #
        # self.__conn__ = connect()
        # self.__cursor__ = self.__conn__.cursor()
        return len(self.__cursor__.fetchall())

    def execute(self, sql: str):
        """
        执行任意SQL语句
        :param sql:
        :return: 游标
        """
        self.__cursor__.execute(sql)
        info = f'在 <Mysql> <{self.__dbname__}>数据库 执行自定义SQL <{sql}>'
        logger(2, info)
        return self.__cursor__

    def update(self, where: dict, data: dict):
        """
        更新数据
        :param where:
        :param data:
        :return:
        """
        assert len(data) > 0, '无效的筛选条件'
        self.__set(data)
        self.__where(where)
        self.__sql('update')
        info = f'在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 更新记录'
        logger(2, info)

    def insert(self, data: any):
        """
        插入数据
        :param data:
        :return:
        """
        assert type(data) in [dict, DataFrame], f'非法的数据类型: {type(data)}'
        self.__values(data)
        self.__sql('insert')
        info = f'在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 插入记录'
        logger(0, info)

    def delete(self, where: dict):
        """
        删除数据
        :param where:
        :return:
        """
        self.__where(where)
        self.__sql('delete')
        info = f'警告: 在 <Mysql> <{self.__dbname__}>数据库 <{self.__tbname__}>数据表 删除记录'
        logger(2, info)

    def upsert(self, where: dict, data: any):
        """
        替换或插入记录
        :param where:
        :param data:
        :return:
        """
        tb = self.__tbname__
        try:
            self(tb).delete(where)
        except Exception as err:
            print(err)
        finally:
            if type(data) is dict:
                where.update(data)
                data = where
            elif type(data) is DataFrame:
                for key, value in where:
                    if key not in data.columns:
                        data[key] = value
            else:
                raise TypeError
            self(tb).insert(data)


def connect_mysql_rdt_fintech():
    db_config = copy.deepcopy(conn.rdt_mysql)
    # db_config["db"] = "rdt_fintech"
    cms = None
    try:
        cms = connect(**db_config)
    except Exception as e:
        logger(2, e)
    return cms


def connect_mysql_Require_Rate_of_Return():
    db_config = copy.deepcopy(conn.rdt_mysql)
    db_config["db"] = "Require_Rate_of_Return"
    cms = None
    try:
        cms = connect(**db_config)
    except Exception as e:
        logger(2, e)
    return cms


def connect_mysql_valuation_samuelson():
    db_config = copy.deepcopy(conn.rdt_mysql)
    db_config["db"] = "valuation_samuelson"
    cms = None
    try:
        cms = connect(**db_config)
    except Exception as e:
        logger(2, e)
    return cms


def connect_mysql_valuation():
    db_config = copy.deepcopy(conn.rdt_mysql)
    db_config["db"] = "valuation"
    cms = None
    try:
        cms = connect(**db_config)
    except Exception as e:
        logger(2, e)
    return cms
