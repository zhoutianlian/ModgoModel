import pandas as pd

from Data.Conn import *
from Config.Database import Database as Db


def merge_table_all(table_list, merge_key, merge_rule):
    data = table_list[0]
    for i in table_list[1:]:
        data = pd.merge(data, i, how=merge_rule, on=merge_key)

    return data


async def get_corporation(db_config):
    async with ConnMongo(**db_config.base) as conn:
        tb, select = Db.mv['tb'], Db.mv['select']
        mv_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.base) as conn:
        tb, select = Db.price['tb'], Db.price['select']
        price_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.orig) as conn:
        tb, select = Db.share['tb'], Db.share['select']
        equity_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.base) as conn:
        tb, select = Db.rev['tb'], Db.rev['select']
        rev_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.base) as conn:
        tb, select = Db.netprofit['tb'], Db.netprofit['select']
        netp_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.orig) as conn:
        tb, select = Db.paycapital['tb'], Db.paycapital['select']
        paycapital_info = await conn(tb).wait('find_new', select=select)
    async with ConnMongo(**db_config.base) as conn:
        tb, select = Db.indus['tb'], Db.indus['select']
        indus_info = await conn(tb).wait('find_new', select=select)
    return mv_info, price_info, equity_info, rev_info, netp_info, paycapital_info, indus_info


# def get_corporation_fs(loop, db_config):
#     tasks = [ef(get_corporation(db_config))]
#     loop.run_until_complete(wait(tasks))
#     mv_info, price_info, equity_info, rev_info, netp_info, paycapital_info, indus_info = tasks[0].result()
#     company_info = get_company_info()
#     value_info = merge_table_all([mv_info, price_info, equity_info, rev_info, netp_info, paycapital_info, company_info,
#                                   indus_info], ["stock_code"], "inner")
#     value_info["other_value"] = value_info["mv"] - (value_info["w_close_price"] * value_info["total_capitalshare"])
#     return value_info

