# -*- coding: utf-8 -*-：
import sys
import datetime
import threading
import getopt
import pandas as pd

from Tool.functions.valuation_exception import InsertException
from Tool.send_email_for_exception import send_mail
from Report.Log import logger
PYDEVD_USE_FRAME_EVAL = "NO"
# 首先读取数据库内所有用户，遍历用户列表，取出对应的公司，依据用户公司锁定一条估值记录，确定财报精度，取出精度最高的财报，进行估值
# 在这其中可以使用多进程配合多线程进行并发操作


sem = threading.Semaphore(5)


class AutoValuation(object):

    def __init__(self):
        self.db = connect_mysql_rdt_fintech()
        self.cursor = self.db.cursor()

    def get_user(self):
        # 读取数据库用户表，得到用户ID列表
        sql = "SELECT id from t_user_info"
        self.cursor.execute(sql)
        user_list = self.cursor.fetchall()
        return user_list

    def get_relation(self, user_list):
        relation = {}
        for i in user_list:
            sql = "SELECT enterprise_id from t_enterprise_user_relation where user_id=%s and whether_del=0"
            self.cursor.execute(sql, [i])
            company_list = self.cursor.fetchall()
            if company_list:
                relation[i] = company_list
        return relation

    def get_record(self, cursor):
        cursor.execute("SELECT id, activity_id, channel_id, currency_id,val_type,val_accuracy,user_id, enterprise_id "
                       "from t_valuating_record where val_valid=1 and val_terminal!=4 order by val_accuracy")
        return cursor.fetchall()

    def do_auto_valuation(self, *args):
        with sem:
            db = connect_mysql_rdt_fintech()
            cursor = db.cursor()
            # 来源终端对应自动估值
            valuation_terminal = 6
            # 输入方法字段使用自动估值对应的数字
            valuation_inputmethod = 50
            # 基准日和日期依据当前时间生成
            value_time = datetime.datetime.now()
            vid, activity_id, channel_id, currency_id, valuation_type, val_accuracy, user_id, enterprise_id = args
            last_id = None
            # 往记录表插入数据，生成vid
            try:
                # ValuatingInput
                data_input = read_mongo_limit("rdt_fintech", "ValuatingInput", {"_id": vid}, {"_id": 0})
                if not data_input.empty:
                    with cursor as curs:
                        curs.execute("insert into t_valuating_record (activity_id, c_time, channel_id, currency_id,"
                                     "enterprise_id, user_id, val_accuracy,val_inputmethod, val_terminal,val_type,"
                                     "val_valid,valuation_failure, val_source_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                     (activity_id, value_time, channel_id, currency_id, enterprise_id, user_id, val_accuracy,
                                      valuation_inputmethod, valuation_terminal, valuation_type, 0, 1, vid))
                        last_id = curs.lastrowid
                        db.commit()
                        data_input["_id"] = last_id
                        save_mongo("rdt_fintech", "ValuatingInput", data_input)
                else:
                    logger(2, f"估值ID为{vid}的记录未找到ValuatingInput数据")
            except Exception as e:
                db.rollback()
                raise InsertException("生成估值记录数据失败，原因:%s" % e)
            finally:
                cursor.close()
                db.close()
            # 依据获取的vid及估值模型id，传入相应估值模型，进行估值
            print(str(value_time) + "开始进行估值")
            # try:
            if last_id:
                Main.Valuation(last_id).run()
            # except Exception as e:
            #     print(e)

    def run(self):
        # 构建进程池
        # p = Pool(4)
        # p = Queue(8)
        # 获取所有用户列表
        # user_list = self.get_user()
        # # 获取用户-公司字典
        # relation_dict = self.get_relation(user_list)
        records = list(self.get_record(self.cursor))
        if records:
            data = pd.DataFrame(records, columns=["id", "activity_id", "channel_id", "currency_id", "val_type",
                                                  "val_accuracy", "user_id", "enterprise_id"])
            data.drop_duplicates(subset=["user_id", "enterprise_id"], inplace=True)
            data["length"] = data["user_id"].apply(lambda x: len(x))
            data = data.query("length < 9")
            self.cursor.close()
            self.db.close()
            # for key, value in relation_dict.items():
            #     # 使用多进程配合多线程进行并发操作
            #     # print("-----")
            #     p.apply_async(self.do_auto_valuation, args=(key, value), error_callback=send_mail)
            #     # self.do_auto_valuation(key, value)
            # # p.terminate()
            # p.join()

            thread_list = []
            for index, value in data.iterrows():
                t = threading.Thread(target=self.do_auto_valuation, args=(
                    [value["id"], value["activity_id"], value["channel_id"], value["currency_id"], value["val_type"],
                     value["val_accuracy"], value["user_id"], value["enterprise_id"]]))
                thread_list.append(t)
                # self.do_auto_valuation(key, value)
            for t in thread_list:
                t.setDaemon(True)
                t.start()

            for t in thread_list:
                t.join(180)


if __name__ == '__main__':
    try:
        import Config.Database
        opts, args = getopt.getopt(sys.argv[1:], 'e:')
        for key, value in opts:
            if key in ['-e']:
                Config.Database.set_db(value)
        from Config.Database import ConnDB as db_config, Database as db, Fields as fd
        from Data.Conn import ConnMysql, connect_mysql_rdt_fintech
        from Config.mongodb import read_mongo_limit, save_mongo
        import Main

        auto = AutoValuation()
        auto.run()
        send_mail("自动估值完成")
    except Exception as e:
        logger(2, e)
