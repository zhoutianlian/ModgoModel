# -*- coding: utf-8 -*-：
import copy
from numpy import average, nan, inf
import redis
from asyncio import ensure_future as ef, wait
import pandas as pd
import Config.Database
from Config.Database import ConnDB
from Config.Database import Database as Db, Fields as Fd
from Data.Conn import *
from FinMod.FS import *
from Hypothesis.Basement import Hypo
from Config.Abnormal import NormalRange
from Tool.Industry import find_similar_industry as si
from Algorithm.Multiplier import *
from Algorithm.Weight import vote
from Algorithm.RGRAlgo import predict_online, predict
from Report.Log import logger


__all__ = ['read', 'read_all_mini', 'read_algo', 'read_net', "read_pattern", "prepare", "FinStm", "ready", "read_ipo"]

redis_pool = redis.ConnectionPool(host=ConnDB.redis_host, port=ConnDB.redis_port, db=0, password=ConnDB.redis_password)


def read(loop, ind_dict, claimed_peers_industry, vid_data, name, spider: int=1, tyc: int=1):
    """
    读取对标公司信息、用户假设、财务报表、商业模型
    :param loop:
    :param ind_dict:
    :param claimed_peers_industry:
    :param vid_data:
    :param name:
    :param spider:
    :param tyc:
    :return:
    """
    db_config = Config.Database.ConnDB
    with ConnMysql(**db_config.rdt_mysql) as conn_mysql, ConnMongo(**db_config.rdt_mongo) as conn_mongo:
        tasks = [ef(read_peers(conn_mysql, ind_dict, claimed_peers_industry)),  # 读取对标公司信息
                 ef(read_hypo(conn_mongo, vid_data[Fd.hyId], vid_data[Fd.input_method])),  # 读取用户假设
                 ef(read_fs(conn_mongo, vid_data[Fd.balId], vid_data[Fd.flowId])),  # 读取财务报表
                 ef(read_bm(conn_mongo, vid_data[Fd.bmId])), # 读取商业模型
                 # ef(read_net(name, spider, tyc))  # 读取网信数据
                 ef(read_ipo(name))
                 ]

        loop.run_until_complete(wait(tasks))

    results = [task.result() for task in tasks]
    return results


async def read_peers(conn, ind_dict, claimed_peers_ind):
    """
    根据对标公司id，从数据库匹配对标公司股票代码
    :param conn
    :param ind_dict:
    :param claimed_peers_ind:
    :return:
    """
    logger(1, '读取对标公司')
    peer_dict = dict()
    peer_list = list()
    tb, select = Db.peers['tb'], Db.peers['select']

    for ind, ids in zip(ind_dict, claimed_peers_ind):
        if len(ids) > 1:
            peer_data = await conn(tb).wait('find', where={'id': {'$in': ids}}, select=select)
        else:
            peer_data = await conn(tb).wait('find', where={'id': ids[0]}, select=select)
        peer = peer_data[select].tolist()
        peer_dict[ind] = peer
        peer_list.extend(peer)

    return peer_dict, peer_list


def read_indus_peers(indus_code):
    """
    这个方法根据GICS代码读取对标公司
    :param indus_code:
    :return:
    """
    indus = str(indus_code)
    logger(1, '根据行业代码读取对标公司')
    code = Fd.code
    db_config = Config.Database.ConnDB
    tb, where, select = Db.peers['tb'], Db.peers['where'], Db.peers['select']

    with ConnMysql(**db_config.rdt_mysql) as conn:
        while len(indus) >= 2:
            top, bottom = '9' * (8 - len(indus)), '0' * (8 - len(indus))
            top_value, bottom_value = int(indus + top), int(indus + bottom)
            peer_data = conn(tb).find(where={where: {'$gte': bottom_value, '$lte': top_value}}, select=select)
            if len(peer_data) >= 10:
                break
            logger(1, f'行业{indus}的对标公司不足10家')
            indus = indus[:-2]
        peers = peer_data[code].tolist()
    return peers


async def read_hypo(conn, hypo_id, input_method):
    """
    传入假设表id，返回假设dict
    :param conn:
    :param hypo_id:
    :param input_method:
    :return:
    """
    logger(1, '读取用户假设')
    tb = Db.hypo['tb']

    try:
        hypo_data = await conn(tb).wait('find_one', {'_id': hypo_id})
        for useless in ['_id', 'fx', 'sys', 'date']:
            hypo_data.pop(useless, 0)
        # 目前页面只支持用户输入借款利率及税率两项参数
        if input_method == 12:
            hypo = hypo_data
        else:
            hypo = {"date": hypo_data["date"], "kd": hypo_data["kd"], "tr": hypo_data["kd"]}
        return hypo
    except Exception as err:
        logger(2, f'读取用户假设失败...{err}')
        return dict()


async def read_fs(conn, bal_list, flow_list):
    """
    传入财报id列表，读取财报，整理为最近12月报表，
    将编号替换为名称，
    返回财报并打包为财报类的格式
    :param conn:
    :param fs_id_list:
    :return:
    """
    logger(1, '读取财务报表')
    # 读取报表id
    bstb = Db.bs['tb']
    pstb = Db.ps['tb']
    # 读取报表数据
    bal_data = await conn(bstb).wait('find', where={'_id': {'$in': bal_list}})
    flow_data = await conn(pstb).wait('find', where={'_id': {'$in': flow_list}})
    if "_class" in bal_data.columns:
        bal_data = bal_data.drop(columns=['fx', 'gaap', 'sys', '_class'])
        flow_data = flow_data.drop(columns=['fx', 'gaap', 'sys', '_class'])
    else:
        bal_data = bal_data.drop(columns=['fx', 'gaap', 'sys'])
        flow_data = flow_data.drop(columns=['fx', 'gaap', 'sys'])

    return bal_data, flow_data


async def read_bm(conn, bm_id):
    """
    传入商业模式id，将编号替换为名称后返回
    :param conn:
    :param bm_id:
    :return:
    """
    logger(1, '读取商业模型')
    tb = Db.bm['tb']
    try:
        bm_data = await conn(tb).wait('find_one', {'_id': bm_id})
        for useless in ['_id', 'fx', 'sys']:
            bm_data.pop(useless, 0)
        bm = BM(bm_data)
        return bm
    except Exception as err:
        logger(2, f'读取商业模型失败...{err}')
        return {}


def read_algo(loop, root, full_fs: FinStm, ind_dict: dict, peer_list: list, peer_dict: dict, hypo: Hypo):
    """
    读取并返回算法假设列表
    :param loop:
    :param root:
    :param full_fs: 财务报表
    :param ind_dict: 行业字典
    :param peer_list: 对标公司列表
    :param peer_dict:
    :param hypo:
    :return:
    """
    logger(1, '读取算法数据')

    # 读取数据
    tasks = [ef(read_basic_db()),
             ef(read_orig_db()),
             ef(read_hypo_db(ind_dict)),
             ]
    loop.run_until_complete(wait(tasks))

    mkt = tasks[0].result()
    orig = tasks[1].result()
    algo, rg_data, ref_dict, similar_dict, rep = tasks[2].result()

    mkt = mkt.merge(orig, on='code', how='left')
    mkt_net = copy.deepcopy(mkt)
    algo_net = copy.deepcopy(algo)
    # 预测增长率
    rg, rg_dict = predict(root, rg_data, ref_dict, similar_dict, full_fs[-1]['rev'])  # todo 新的增长率预测模型

    # 存储分行业预测增长率和预测增长率
    rep['rg_dict'] = rg_dict
    algo['rg'] = [rg]

    # 计算网信指标
    mkt_net = cal_mkt_mults(mkt_net, 'mini')
    peer_net = mkt_net.query('code in @peer_list')

    # 防止金融公司有形净资产取出0值
    peer_zero = peer_net.query('na == 0')
    if len(peer_zero) > 0:
        from pandas import concat
        peer_not_zero = peer_net.query('na != 0')
        peer_zero.eval('na = ta - tl', inplace=True)
        peer_net = concat([peer_not_zero, peer_zero])
    peer_net.eval('pb = mv / na', inplace=True)
    peer_net.replace(inf, nan)

    peer_net.eval('npm = np / rev', inplace=True)
    peer_net = peer_net.loc[:, ['code', 'mv', 'share', 'ub', 'pe', 'pb', 'ps', 'npm']]
    mkt_mult = mkt_net.loc[:, ['pe', 'pb', 'ps']].apply(lambda x: x.median(), axis=0).to_dict()

    # 计算指标
    mkt = cal_mkt_mults(mkt, 'lite')

    # 计算市场数据
    logger(0, '计算市场数据...')
    mkt_hypo = cal_mkt_future(mkt, hypo)
    algo.update(mkt_hypo)

    # 计算可比公司权重
    logger(0, '计算可比公司相似性...')
    # 计算可比公司公司指标
    peer = cal_peer_index(mkt, peer_list, hypo['yds'])
    peer_vote = vote(peer, full_fs[-1], hypo)

    # 引入行业权重
    for index, data in peer_vote.iterrows():
        for ind in peer_dict:
            if data['code'] in peer_dict[ind]:
                peer_vote.loc[index, 'wt'] *= ind_dict[ind]

    peer = peer.merge(peer_vote, on='code', how='left')

    # 加权平均可比公司数据
    logger(0, '计算可比公司加权平均数据...')
    wa_cols = ['code', 'ub', 'evop', 'pe', 'evic', 'pb', 'cm', 'sm', 'dsi', 'dso', 'dpo']
    peer_vote = peer_vote.merge(peer.loc[:, wa_cols], on='code', how='left')
    peer_vote.rename(columns={'cm': 'acm', 'sm': 'asm', 'dsi': 'adsi', 'dso': 'adso', 'dpo': 'adpo'}, inplace=True)

    # 计算加权平均假设
    for name in ['ub', 'evop', 'pe', 'evic', 'pb', 'acm', 'asm', 'adsi', 'adso', 'adpo']:
        limit = NormalRange().__getattribute__(name)
        norm = peer_vote.query(f'@limit[0] < {name} < @limit[1]')
        algo[name] = norm.eval(f'{name} * wt').sum() / norm['wt'].sum()

    int_rate = hypo['kd']
    peer.eval('nopat1 = ie * (1 - @int_rate) + np1', inplace=True)
    peer_mults = cal_peer_mults(peer)

    # 返回可比公司比率
    peer.eval('cr = 1 - nopat / rev + capr', inplace=True)
    peer_ratio = peer.loc[:, ['code', 'wt', 'var', 'cr', 'rg', 'ub']]

    # 返回可比公司资产负债
    peer_fs = peer.loc[:, ['code', 'mv', 'wt', 'cash', 'ar', 'inv', 'ppe', 'ta', 'loan', 'ap', 'tl', 'rev', 'np', 'rg']]

    return algo, peer_mults, peer_ratio, peer_fs, rep, rg, peer_net, algo_net, mkt_mult


async def read_basic_db():
    logger(0, '读取上市公司市值数据...')
    r = redis.StrictRedis(connection_pool=redis_pool)
    if r.exists("basic_db"):
        dict_res = eval(r.get("basic_db").decode())
        return pd.DataFrame(dict_res)
    else:
        db_config = Config.Database.ConnDB
        tb, select = Db.mv['tb'], Db.mv['select']

        async with ConnMongo(**db_config.base) as conn:
            mkt = await conn(tb).wait('find_new', select=select)
        data_res = mkt.rename(columns={Fd.mv: 'mv', Fd.code: 'code'}).loc[: ,['code', 'mv']]
        data_dict = data_res.to_dict()
        r.set("basic_db", str(data_dict), ex=604800)
        return data_res


async def read_orig_db():
    """
    读取上市公司市场数据
    包括财务数据、附注、衍生
    :return:
    """
    logger(0, '读取上市公司市场数据...')
    r = redis.StrictRedis(connection_pool=redis_pool)
    if r.exists("origin_db"):
        dict_res = eval(r.get("origin_db").decode())
        return pd.DataFrame(dict_res)
    else:
        db_config = Config.Database.ConnDB
        async with ConnMongo(**db_config.orig) as conn:
            # 读取总股本
            tb, select = Db.share['tb'], Db.share['select']
            share_data = await conn(tb).wait('find_new', select=select)
            orig = share_data.rename(columns={Fd.share: 'share', Fd.code: 'code'}).loc[:, ['code', 'share']]
            orig = orig.drop_duplicates(subset=["code"]).reset_index()

            # 读取无杠杆beta
            tb, select = Db.beta['tb'], Db.beta['select']
            ub_data = await conn(tb).wait('find_new', select=select)
            ub_data.rename(columns={Fd.ub: 'ub', Fd.std: 'std', Fd.code: 'code'}, inplace=True)
            ub_data = ub_data.drop_duplicates(subset=["code"]).reset_index()
            ub_data.eval('std = std / 100', inplace=True)
            orig = orig.merge(ub_data.loc[:, ['code', 'std', 'ub']], on='code', how='left')

            # 读取流动资产数据
            tb, select = Db.ca['tb'], Db.ca['select']
            ca_data = await conn(tb).wait('find_new', select=select)
            ca_data.rename(columns={Fd.cash: 'cash', Fd.ce: 'ce', Fd.ar: 'ar', Fd.inv: 'inv', Fd.code: 'code'},
                           inplace=True)
            ca_data = ca_data.drop_duplicates(subset=["code"]).reset_index()
            ca_data.eval('cash = cash + ce', inplace=True)  # 合并现金和现金等价物
            orig = orig.merge(ca_data.loc[:, ['code', 'cash', 'ar', 'inv']], on='code', how='left')

            # 读取投资性房地产、固定资产、在建工程、无形资产、长期待摊费用
            tb, select = Db.la['tb'], Db.la['select']
            la_data = await conn(tb).wait('find_new', select=select)
            la_data.rename(columns={Fd.ip: 'ip', Fd.ppe: 'ppe', Fd.cip: 'cip', Fd.ia: 'ia', Fd.dev: 'dev', Fd.le: 'le',
                                    Fd.ta: 'ta', Fd.code: 'code'}, inplace=True)
            la_data = la_data.drop_duplicates(subset=["code"]).reset_index()
            la_data.eval('ppe = ppe + ip + cip + ia + dev + le', inplace=True)  # 合并资本性资产
            orig = orig.merge(la_data.loc[:, ['code', 'ppe', 'ta']], on='code', how='left')

            # 读取负债
            # 读取应付账款
            tb, select = Db.cl['tb'], Db.cl['select']
            cl_data = await conn(tb).wait('find_new', select=select)
            cl_data.rename(columns={Fd.ap: 'ap', Fd.code: 'code'}, inplace=True)
            cl_data = cl_data.drop_duplicates(subset=["code"]).reset_index()
            orig = orig.merge(cl_data.loc[:, ['code', 'ap']], on='code', how='left')

            # 读取负债合计
            tb, select = Db.ll['tb'], Db.ll['select']
            ll_data = await conn(tb).wait('find_new', select=select)
            ll_data.rename(columns={Fd.tl: 'tl', Fd.code: 'code'}, inplace=True)
            ll_data = ll_data.drop_duplicates(subset=["code"]).reset_index()
            orig = orig.merge(ll_data.loc[:, ['code', 'tl']], on='code', how='left')

            # 读取附注数据
            # 读取对标公司lyr-研发支出
            tb, select = Db.note['tb'], Db.note['select']
            note_data = await conn(tb).wait('find_new', select=select)
            note_data.rename(columns={Fd.rd: 'rd', Fd.code: 'code'}, inplace=True)
            orig = orig.merge(note_data.loc[:, ['code', 'rd']], on='code', how='left')

            # 读取衍生数据
            # 读取TTM营业收入、TTM营业成本、LYR折旧和摊销、TTM EBIT、TTM EBT, TTM所得税、TTM归母净利润、TTM经营活动现金流、
            # TTM净现金流、TTM资本性支出、TTM现金分红、MRQ带息债、MRQ全部投入资本、MRQ归母有形净资产、3年营收增长率
            tb, select = Db.der['tb'], Db.der['select']
            der_data = await conn(tb).wait('find_new', select=select)
            der_data.rename(columns={Fd.gr: 'rev', Fd.cogs: 'cogs', Fd.da: 'da', Fd.op: 'op', Fd.tp: 'tp', Fd.np: 'np',
                                     Fd.cfo: 'cfo', Fd.tcf: 'tcf', Fd.capex: 'capex', Fd.div: 'div', Fd.loan: 'loan',
                                     Fd.ic: 'ic', Fd.na: 'na', Fd.rg3: 'rg3', Fd.code: 'code'},
                            inplace=True)
            der_data.eval('rg = (1 + rg3) ** (1 / 3) - 1', inplace=True)  # 年化营收增长率
            der_data.drop(columns=['_id', 'rg3'], inplace=True)
            orig = orig.merge(der_data, on='code', how='left')

            # 读取一致预期数据
            # 读取预测营业收入中值、预测归母净利润中值、预测每股现金流中值、预测每股现金股利中值、预测EBIT中值、预测EBITDA中值
            tb, select = Db.est['tb'], Db.est['select']
            est_data = await conn(tb).wait('find_new', select=select)
            est_data.rename(columns={Fd.est_rev: 'rev1', Fd.est_np: 'np1', Fd.est_cps: 'cps1',  Fd.est_dps: 'dps1',
                                     Fd.est_op: 'op1', Fd.est_opda: 'opda1', Fd.est_bps: 'bps1', Fd.est_tp: 'tp1',
                                     Fd.code: 'code'},
                            inplace=True)
            est_data.drop(columns=['_id'], inplace=True)
            orig = orig.merge(est_data, on='code', how='left')
            orig.eval('cf1 = cps1 * share', inplace=True)
            orig.eval('div1 = dps1 * share', inplace=True)
            orig.eval('na1 = bps1* share', inplace=True)
            orig.drop(['cps1', 'dps1', 'bps1'], axis=1, inplace=True)
            orig = orig.drop_duplicates(subset=["code"]).reset_index()
            dict_res = orig.to_dict()
            r.set("origin_db", str(dict_res), ex=604800)
            return orig


async def read_hypo_db(ind_dict):
    logger(0, '读取资本市场数据...')
    algo = dict()
    doc = dict()
    db_config = Config.Database.ConnDB

    async with ConnMongo(**db_config.hypo) as conn:
        # 读取无风险利率
        tb, select = Db.rf['tb'], Db.rf['select']
        rf_data = await conn(tb).wait('find_new', select=select)
        algo['rf'] = rf_data.iloc[0][Fd.rf]

        # 读取市场风险溢价
        tb, select = Db.mrp['tb'], Db.mrp['select']
        mrp_data = await conn(tb).wait('find_new', select=select)
        algo['mrp'] = mrp_data.iloc[0][Fd.mrp]

        # 读取所选行业最优资本结构
        tb = Db.dic['tb']
        dic_data = await conn(tb).wait('find_new')
        wanted_ind = list(ind_dict.keys())
        exist_ind = dic_data[Fd.industry].tolist()
        similar_dict = si(wanted_ind, exist_ind)
        dic = 0
        dic_dict = {}
        for ind in ind_dict:
            similar_data = dic_data[dic_data[Fd.industry].isin(similar_dict[ind])]
            ind_dic = ind_dict[ind] * average(similar_data[Fd.dic])
            dic_dict[ind] = ind_dic
            dic += ind_dic

        doc['dic_dict'] = dic_dict
        algo['dic'] = dic

        # 读取预测增长率相关
        logger(0, '预测未来一年营业收入增长率...')
        ref_dict = {}
        tb, where = Db.indrg['tb'], Db.indrg['where']
        dic_data = await conn(tb).wait('find')
        wanted_ind = list(ind_dict.keys())
        exist_ind = dic_data["indus"].tolist()
        similar_dict = si(wanted_ind, exist_ind)
        for ind in ind_dict:
            for similar in similar_dict[ind]:
                ref_dict[similar] = ind_dict[ind] / len(similar_dict[ind])
        rg_data = await conn(tb).wait('find', where={where: {'$in': list(ref_dict.keys())}})
        rg_data.drop(columns=['_id'], inplace=True)
    return algo, rg_data, ref_dict, similar_dict, doc


async def read_ipo(name):
    r = redis.StrictRedis(connection_pool=redis_pool)
    db_config = Config.Database.ConnDB
    if r.exists("ipo_a"):
        company_dict = eval(r.get("ipo_a").decode())
        if name in company_dict:
            if company_dict[name].startswith("68"):
                return {"科创板": 0}
            else:
                return {"沪深A股": 0}

    else:
        tb, select = Db.company['tb'], Db.company['select']
        async with ConnMongo(**db_config.orig) as conn:
            com = await conn(tb).wait('find_new', select=select)
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
        db_config = Config.Database.ConnDB
        tb, select = Db.hk_company['tb'], Db.hk_company['select']

        with ConnMongo(**db_config.orig) as conn:
            com = await conn(tb).wait('find_new', select=select)
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
        db_config = Config.Database.ConnDB
        tb, select = Db.america_company['tb'], Db.america_company['select']

        with ConnMongo(**db_config.orig) as conn:
            com = await conn(tb).wait('find_new', select=select)
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
        db_config = Config.Database.ConnDB
        tb, select = Db.san_company['tb'], Db.san_company['select']

        with ConnMongo(**db_config.orig) as conn:
            com = await conn(tb).wait('find_new', select=select)
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


def read_peer_data(loop, fs, indus, peer_list, na, name, spider, tyc):
    tasks = [ef(read_basic_db()),
             ef(read_orig_db()),
             ef(read_hypo_db({str(indus): 1})),
             ef(read_net(name, spider, tyc)),
             ef(read_ipo(name))
             ]
    loop.run_until_complete(wait(tasks))

    mkt = tasks[0].result()
    orig = tasks[1].result()
    algo, rg_data, ref_dict, similar_dict, rep = tasks[2].result()
    net_info = tasks[3].result()
    ipo = tasks[4].result()
    mkt = mkt.merge(orig, on='code', how='left')

    # 计算指标
    mkt = cal_mkt_mults(mkt, 'mini')
    peer = mkt.query('code in @peer_list')

    # 预测增长率
    # rg, rg_dict = predict(root, rg_data, ref_dict, similar_dict, rev)
    fs["na"] = na
    rg = predict_online(indus, fs)

    # 防止金融公司有形净资产取出0值
    peer_zero = peer.query('na == 0')
    if len(peer_zero) > 0:
        from pandas import concat
        peer_not_zero = peer.query('na != 0')
        peer_zero.eval('na = ta - tl', inplace=True)
        peer = concat([peer_not_zero, peer_zero])
    peer.eval('pb = mv / na', inplace=True)
    peer.replace(inf, nan)

    peer.eval('npm = np / rev', inplace=True)
    peer = peer.loc[:, ['code', 'mv', 'share', 'ub', 'pe', 'pb', 'ps', 'npm']]
    mkt_mult = mkt.loc[:, ['pe', 'pb', 'ps']].apply(lambda x: x.median(), axis=0).to_dict()
    return rg, peer, algo, mkt_mult, net_info, ipo


def read_all_mini(loop, fs, name, indus, na, spider: int = 1, tyc: int = 1):
    logger(0, '读取对标公司代码...')
    peers_code = read_indus_peers(indus)
    logger(0, '读取对标公司数据...')
    rg, peer, algo, mkt_mult, net_info, ipo = read_peer_data(loop, fs, indus, peers_code, na, name, spider, tyc)
    return rg, peer, algo, mkt_mult, net_info, ipo


async def read_net(name, spider: int = 1, tyc: int = 1):
    import requests
    logger(0, '读取爬虫和天眼查...')
    conn_config = Config.Database.ConnDB
    network_info_grasper = requests.get(conn_config.tyc % (name, spider, tyc))
    return eval(network_info_grasper.content.decode())


def read_pattern(vid, db, db_config):
    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.vr['tb'], db.vr['select']
        vid_data = conn(tb).find_one(where={'id': vid}, select=select)
    return vid_data


def prepare():
    """
    执行估值前准备
    1. 清理sklearn资源
    2. 判断运行环境, 配置文件路径
    3. 生成异步事件循环
    4. 生成估值文档
    5. 导入数据库设置
    :param lv: 估值等级: lite, mini
    :return: 根目录路径, 事件循环, 估值文档
    """
    # 导入工程包
    import Config.Database
    from Config.Database import Database as Db, Fields as Fd
    # 导入通用包
    import os
    # import keras
    from asyncio import new_event_loop as nel, set_event_loop as sel

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    # keras.backend.clear_session()
    root = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/"
    loop = nel()
    sel(loop)

    doc = dict()
    db_config = Config.Database.ConnDB
    return root, loop, doc, db_config, Db, Fd


def ready(vid):
    """
    执行估值前准备
    1. 清理sklearn资源
    2. 判断运行环境, 配置文件路径
    3. 生成异步事件循环
    4. 生成估值文档
    5. 导入数据库设置
    :param vid: 估值id
    :param lv: 估值等级: lite, mini
    :return: 根目录路径, 事件循环, 估值文档
    """
    # 导入工程包
    import Config.Database
    from Config.Database import Database as Db, Fields as Fd
    logger(2, '## 开始估值 VID: %s ##' % vid)

    db_config = Config.Database.ConnDB
    return db_config, Db, Fd
