# -*- coding: utf-8 -*-：
from Algorithm.Average import synthesis, syn_traceback
# from Algorithm.GuessFS import guess_na
from Data.Conn import ConnMongo, ConnMysql
# from Business.Adviser import BMAnalyst
from Data.Read import prepare
from Report.Log import logger
from Tool.Util import merge_data_lite


def run_lite(vid: int, eid: int, saving: bool = True, *args, **kwargs):
    """
    执行快速估值的方法
    :param vid: 估值id
    :param eid: 公司id
    :param saving: 是否储存
    :param args: 备用字段
    :param kwargs: 备用字段
    :return:
    """
    # 导入工程包
    from Data.Read import read, read_algo, read_ipo
    from Data.Save import save
    from Hypothesis.Basement import Hypo
    from FinMod.SortFS import sort_fs
    from Algorithm.Complete import analyse_hypo
    from Process.Valuate import dcf_valuator, mkt_valuator, aba_valuator, opt_valuator, net_valuator
    from Evaluate.IPO import IPOProspect
    from Tool.Util import GenTreat

    # 估值准备
    root, loop, doc, db_config, db, fd = prepare()
    # root: 读取目录，根据windows和linux环境而变
    # loop: 异步协程的事件循环
    # doc: 用于记录估值过程中产生的中间变量
    # db_config: 读取数据库的配置
    # db: 数据库-数据表
    # fd: 字段表

    # 读取估值信息
    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.enterprise['tb'], db.enterprise['select']
        com_data = conn(tb).find_one(where={'id': eid}, select=select)
        tb, select = db.vr['tb'], [fd.input_method]
        vr_method = conn(tb).find_one(where={"id": vid}, select=select)

    with ConnMongo(**db_config.tyc_mongo) as conn:
        tb, select = db.tyc['tb'], db.tyc['select']
        tyc_data = conn(tb).find_one(where={'name': com_data["enterprise_name"]}, select=select)

    with ConnMongo(**db_config.rdt_mongo) as conn:
        tb, select = db.record['tb'], db.record['select']
        vid_data = conn(tb).find_one(where={'_id': vid}, select=select)

    vid_data = merge_data_lite(vid_data, tyc_data, vr_method)

    # 整合行业字典
    ind_dict = dict()
    claimed_peers_industry = []
    for key, value in vid_data[fd.mindcode].items():
        ind_dict[key] = value[0]
        claimed_peers_industry.append(value[1])

    doc['ind_dict'] = ind_dict

    # peer_info, user_hypo, orig_fs, bm, net_info = read(loop, ind_dict, claimed_peers_industry, vid_data,
    #                                                    name=com_data["enterprise_name"], spider=0)
    peer_info, user_hypo, orig_fs, bm, ipo = read(loop, ind_dict, claimed_peers_industry, vid_data,
                                                       name=com_data["enterprise_name"], spider=0)

    # 检修
    # print('========原始财务报表========')
    # print(pd.DataFrame(orig_fs).T)

    # 拆解对标公司
    peer_dict, peer_list = peer_info
    # peer_dict: {行业代码1: [公司代码1, ...], 行业代码2: [公司代码2, ...], ...}
    doc['peers'] = peer_dict

    # 用户假设
    hypo = Hypo()
    # print(user_hypo)
    if len(user_hypo) > 0:
        hypo.deep_update(user_hypo)

    # 处理财务报表
    orig_bal, orig_flow = orig_fs
    fs = sort_fs(orig_bal, orig_flow)

    doc['share'] = fs[-1]['share']
    fs_hypo = analyse_hypo(fs, hypo)
    hypo.deep_update(fs_hypo)

    # 处理商业模型
    print('FBI WARNING: 待补充商业模型假设...')
    bm_hypo = {}
    # bm.update({"market": vid_data[fd.market], "round": vid_data[fd.round]})
    # bm_analyst = BMAnalyst(bm)
    # bm_hypo = bm_analyst.advise()
    doc['bm'] = bm_hypo

    # 读取算法假设
    algo, peer_mults, peer_ratio, peer_fs, rep, rg, peer_net, algo_net, mkt_mult = read_algo(
        loop, root, fs, ind_dict, peer_list, peer_dict, hypo)
    doc.update(rep)
    doc['peer_data'] = peer_mults.to_dict('records')

    # 整理最终假设
    hypo.deep_update(algo)
    hypo.adjust(bm_hypo)
    hypo.deep_update(user_hypo)
    logger(1, '整合假设完成...')
    try:
        hypo.__delitem__('date')
    except Exception as err:
        pass

    doc['hypo'] = hypo.to_general()

    # 读取估值模式
    logger(1, '收入法估值')
    mode = vid_data[fd.mode]

    # 按模式进行收入法估值
    # 检修
    # print('========整理后的历史财务数据========')
    # print(pd.DataFrame(fs).T)

    full_fs, dcf_val, dcf_detail = dcf_valuator(fs, hypo, mode)

    doc_fs = full_fs.to_general()
    doc['fs'] = doc_fs[full_fs.start():]
    doc['dcf_detail'] = dcf_detail

    # 市场法估值
    logger(1, '市场法估值')
    fs0 = fs[-1]  # TTM财务数据
    try:
        fs1 = full_fs[full_fs.start()]
    except IndexError:
        fs1 = None
    mkt_val, mkt_detail = mkt_valuator(peer_mults, fs0, fs1, hypo)
    doc['mkt_detail'] = mkt_detail

    # 期权法估值
    logger(1, '期权法估值')
    opt_val, opt_detail = opt_valuator(fs0, peer_ratio, hypo)
    doc['opt_detail'] = opt_detail

    # 资产法估值
    logger(1, '资产法估值')
    aba_val, aba_detail = aba_valuator(fs0, peer_fs, hypo)
    doc['aba_detail'] = aba_detail

    # # 网信估值
    # logger(1, '网信估值')
    # net_val, net_detail = net_valuator(root, fs0, net_info['tyc'])
    # doc['net_detail'] = net_detail

    # 综合评估
    logger(1, '计算综合估值')
    syn_val, model_result = synthesis(int(hypo['dgt']), doc)
    doc['syn_val'] = syn_val
    doc['syn_wt'] = model_result
    doc = GenTreat(doc, hypo['dgt']).get()
    # 综合追溯
    logger(1, '计算可追溯综合估值')
    doc['traceback'] = syn_traceback(int(hypo['dgt']), doc)

    # 上市估计
    logger(1, '计算上市预计')
    from Config.Type import market_type
    if ipo:
        doc['ipo_prospect'] = ipo
    else:
        if vid_data[fd.market] == 5:
            ipo_evaluator = IPOProspect(full_fs, syn_val[1])
            doc['ipo_prospect'] = ipo_evaluator.get()
        else:
            doc['ipo_prospect'] = {market_type[vid_data[fd.market]]: 0}
    if saving:
        # 存储通用估值结果
        logger(1, '存储估值结果')
        gen_record, model_record = save(vid, doc, mode, orig_bal, orig_flow, ipo)
        response = {'syn': gen_record, 'model': model_record}
        logger(2, '## 估值结束 VID: %s ##' % vid)
    else:
        print('>> Document <<\n', doc)
    return "SUCCESS"
